"""
graph_rag.py
------------
Lớp MultihopGraphRAG thực hiện:
  - Bước 1: Kết nối Neo4j
  - Bước 2: Tìm kiếm vector + mở rộng đa bước (multi-hop) qua các quan hệ
            CAN_CU, THAY_THE, HOP_NHAT, SUA_DOI_BO_SUNG, ...
  - Xây dựng ngữ cảnh (context) tổng hợp để đưa vào LLM.
"""

import re
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

from neo4j import GraphDatabase

import config
from embeddings import embed_text


@dataclass
class RetrievedChunk:
    chunk_id: str
    text: str
    document_title: str
    score: Optional[float] = None      # điểm tương đồng vector (chỉ có ở bước 0)
    hop: int = 0                       # 0 = khớp trực tiếp, >0 = lấy qua multi-hop
    path_relationships: List[str] = field(default_factory=list)  # đường quan hệ dẫn tới chunk này

    def to_context_block(self) -> str:
        hop_tag = "Khớp trực tiếp" if self.hop == 0 else f"Liên quan qua {self.hop} bước ({' -> '.join(self.path_relationships)})"
        return (
            f"[Văn bản: {self.document_title} | {hop_tag}]\n"
            f"{self.text.strip()}"
        )


class MultihopGraphRAG:
    def __init__(
        self,
        uri: str = config.NEO4J_URI,
        user: str = config.NEO4J_USER,
        password: str = config.NEO4J_PASSWORD,
        database: str = config.NEO4J_DATABASE,
    ):
        self._driver = GraphDatabase.driver(uri, auth=(user, password))
        self._database = database

    def close(self):
        self._driver.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def verify_connectivity(self) -> bool:
        try:
            self._driver.verify_connectivity()
            return True
        except Exception as e:
            print(f"[graph_rag] Lỗi kết nối Neo4j: {e}")
            return False

    def extract_document_references(self, question: str) -> List[str]:
        """Trích xuất các mã định danh văn bản như 46/2023/NĐ-CP khỏi câu hỏi."""
        refs = re.findall(r"\b\d{1,4}/\d{4}/[A-Za-zÀ-ỹ]+(?:-[A-Za-zÀ-ỹ]+)*\b", question)
        return list(dict.fromkeys(refs))

    def direct_document_search(self, question: str, top_k: int = config.DEFAULT_TOP_K) -> List[RetrievedChunk]:
        """Ưu tiên truy vấn trực tiếp theo số hiệu văn bản để lấy chunk từ document đúng."""
        references = self.extract_document_references(question)
        if not references:
            return []

        clauses = []
        params: Dict[str, Any] = {"limit": top_k}
        for idx, ref in enumerate(references[:3]):
            params[f"ref{idx}"] = ref.lower()
            clauses.append(f"(toLower(doc.{config.DOCUMENT_TITLE_PROPERTY}) CONTAINS $ref{idx} OR toLower(chunk.{config.CHUNK_TEXT_PROPERTY}) CONTAINS $ref{idx})")

        if not clauses:
            return []

        cypher = f"""
        MATCH (chunk:{config.CHUNK_NODE_LABEL})-[:{config.BELONGS_TO_REL}]->(doc:{config.DOCUMENT_NODE_LABEL})
        WHERE {' OR '.join(clauses)}
        RETURN
            elementId(chunk) AS chunk_id,
            chunk.{config.CHUNK_TEXT_PROPERTY} AS text,
            coalesce(doc.{config.DOCUMENT_TITLE_PROPERTY}, 'Không rõ văn bản') AS document_title
        LIMIT $limit
        """

        with self._driver.session(database=self._database) as session:
            result = session.run(cypher, parameters=params)
            records = [dict(r) for r in result]

        return [
            RetrievedChunk(
                chunk_id=r["chunk_id"],
                text=r["text"] or "",
                document_title=r["document_title"],
                score=None,
                hop=0,
                path_relationships=[],
            )
            for r in records
        ]

    # ------------------------------------------------------------------
    # Bước 2a: Tìm kiếm vector (seed search)
    # ------------------------------------------------------------------
    def vector_search(self, question: str, top_k: int = config.DEFAULT_TOP_K) -> List[RetrievedChunk]:
        """Chuyển câu hỏi thành vector và tìm các Chunk gần nhất trong Neo4j
        thông qua vector index đã tạo ở Bài thực hành 1."""
        query_vector = embed_text(question)

        cypher = f"""
        CALL db.index.vector.queryNodes($index_name, $top_k, $query_vector)
        YIELD node AS chunk, score
        OPTIONAL MATCH (chunk)-[:{config.BELONGS_TO_REL}]->(doc:{config.DOCUMENT_NODE_LABEL})
        RETURN
            elementId(chunk) AS chunk_id,
            chunk.{config.CHUNK_TEXT_PROPERTY} AS text,
            coalesce(doc.{config.DOCUMENT_TITLE_PROPERTY}, 'Không rõ văn bản') AS document_title,
            score
        ORDER BY score DESC
        """

        with self._driver.session(database=self._database) as session:
            result = session.run(
                cypher,
                index_name=config.VECTOR_INDEX_NAME,
                top_k=top_k,
                query_vector=query_vector,
            )
            records = [dict(r) for r in result]

        return [
            RetrievedChunk(
                chunk_id=r["chunk_id"],
                text=r["text"] or "",
                document_title=r["document_title"],
                score=r["score"],
                hop=0,
                path_relationships=[],
            )
            for r in records
        ]

    def keyword_search(self, question: str, top_k: int = config.DEFAULT_TOP_K) -> List[RetrievedChunk]:
        """Fallback dùng từ khóa khi vector search không trả về kết quả."""
        tokens = [t for t in re.split(r"[^a-zA-Z0-9À-ỹ]+", question.lower()) if t]
        if not tokens:
            return []

        terms = sorted(set(tokens), key=lambda t: (-len(t), t))[:8]
        if any(term.isdigit() for term in tokens):
            terms = [t for t in terms if not t.isdigit()][:6]
            terms = [t for t in terms if len(t) >= 2]
        clauses = []
        params: Dict[str, Any] = {"limit": top_k, "terms": terms}
        for idx, term in enumerate(terms):
            params[f"kw{idx}"] = term
            clauses.append(f"toLower(chunk.{config.CHUNK_TEXT_PROPERTY}) CONTAINS $kw{idx}")

        if not clauses:
            return []

        cypher = f"""
        MATCH (chunk:{config.CHUNK_NODE_LABEL})-[:{config.BELONGS_TO_REL}]->(doc:{config.DOCUMENT_NODE_LABEL})
        WHERE {' OR '.join(clauses)}
        WITH chunk, doc,
             reduce(score = 0, term IN $terms | score + case when toLower(chunk.{config.CHUNK_TEXT_PROPERTY}) CONTAINS term then 1 else 0 end) AS score
        RETURN
            elementId(chunk) AS chunk_id,
            chunk.{config.CHUNK_TEXT_PROPERTY} AS text,
            coalesce(doc.{config.DOCUMENT_TITLE_PROPERTY}, 'Không rõ văn bản') AS document_title,
            score
        ORDER BY score DESC
        LIMIT $limit
        """

        with self._driver.session(database=self._database) as session:
            result = session.run(cypher, parameters=params)
            records = [dict(r) for r in result]

        return [
            RetrievedChunk(
                chunk_id=r["chunk_id"],
                text=r["text"] or "",
                document_title=r["document_title"],
                score=None,
                hop=0,
                path_relationships=[],
            )
            for r in records
        ]

    # ------------------------------------------------------------------
    # Bước 2b: Mở rộng đa bước (multi-hop expansion)
    # ------------------------------------------------------------------
    def multihop_expand(
        self,
        seed_chunks: List[RetrievedChunk],
        hops: int = config.DEFAULT_HOPS,
        relationship_types: Optional[List[str]] = None,
        max_chunks_per_hop: int = config.MAX_CONTEXT_CHUNKS_PER_HOP,
    ) -> List[RetrievedChunk]:
        """Từ các Chunk khớp trực tiếp (hop=0), duyệt qua các quan hệ liên kết
        giữa các Document (CAN_CU, THAY_THE, HOP_NHAT, SUA_DOI_BO_SUNG, ...)
        để lấy thêm các đoạn văn bản ngữ cảnh liên quan, tối đa `hops` bước nhảy.
        """
        if hops <= 0 or not seed_chunks:
            return []

        rel_types = relationship_types or config.MULTIHOP_RELATIONSHIPS
        rel_pattern = "|".join(rel_types)

        seed_ids = list({c.chunk_id for c in seed_chunks})

        # Duyệt document liên quan trong bán kính `hops` bước, theo cả 2 chiều
        # (vì ví dụ "A thay_the B" có thể cần trả lời cả khi hỏi từ A hoặc từ B),
        # đồng thời trả về đường đi (path) để biết đã đi qua quan hệ nào.
        cypher = f"""
        MATCH (seed:{config.CHUNK_NODE_LABEL})
        WHERE elementId(seed) IN $seed_ids
        MATCH (seed)-[:{config.BELONGS_TO_REL}]->(seed_doc:{config.DOCUMENT_NODE_LABEL})
        MATCH path = (seed_doc)-[rels:{rel_pattern}*1..{hops}]-(related_doc:{config.DOCUMENT_NODE_LABEL})
        WHERE related_doc <> seed_doc
        WITH related_doc, path, length(path) AS hop_count,
             [r IN relationships(path) | type(r)] AS rel_path
        MATCH (chunk:{config.CHUNK_NODE_LABEL})-[:{config.BELONGS_TO_REL}]->(related_doc)
        RETURN DISTINCT
            elementId(chunk) AS chunk_id,
            chunk.{config.CHUNK_TEXT_PROPERTY} AS text,
            related_doc.{config.DOCUMENT_TITLE_PROPERTY} AS document_title,
            hop_count,
            rel_path
        ORDER BY hop_count ASC
        LIMIT $limit
        """

        with self._driver.session(database=self._database) as session:
            result = session.run(
                cypher,
                seed_ids=seed_ids,
                limit=max_chunks_per_hop * hops,
            )
            records = [dict(r) for r in result]

        expanded = [
            RetrievedChunk(
                chunk_id=r["chunk_id"],
                text=r["text"] or "",
                document_title=r["document_title"] or "Không rõ văn bản",
                score=None,
                hop=r["hop_count"],
                path_relationships=r["rel_path"],
            )
            for r in records
        ]
        return expanded

    # ------------------------------------------------------------------
    # Ghép ngữ cảnh cuối cùng: khớp trực tiếp + multi-hop
    # ------------------------------------------------------------------
    def retrieve_context(
        self,
        question: str,
        top_k: int = config.DEFAULT_TOP_K,
        hops: int = config.DEFAULT_HOPS,
        relationship_types: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        direct_seed_chunks = self.direct_document_search(question, top_k=top_k)
        if direct_seed_chunks:
            seed_chunks = direct_seed_chunks
        else:
            try:
                seed_chunks = self.vector_search(question, top_k=top_k)
            except Exception as exc:
                print(f"[graph_rag] Vector search lỗi: {exc}; dùng fallback từ khóa")
                seed_chunks = []

            if not seed_chunks:
                print("[graph_rag] Vector search không trả về kết quả; dùng fallback từ khóa")
                seed_chunks = self.keyword_search(question, top_k=top_k)

        hop_chunks: List[RetrievedChunk] = []
        if hops > 0:
            hop_chunks = self.multihop_expand(
                seed_chunks, hops=hops, relationship_types=relationship_types
            )

        # loại trùng (một chunk có thể vừa là seed vừa xuất hiện lại qua multi-hop)
        seen_ids = {c.chunk_id for c in seed_chunks}
        deduped_hop_chunks = [c for c in hop_chunks if c.chunk_id not in seen_ids]

        all_chunks = seed_chunks + deduped_hop_chunks
        context_text = "\n\n---\n\n".join(c.to_context_block() for c in all_chunks)

        return {
            "question": question,
            "hops": hops,
            "seed_chunks": seed_chunks,
            "hop_chunks": deduped_hop_chunks,
            "all_chunks": all_chunks,
            "context_text": context_text,
        }
