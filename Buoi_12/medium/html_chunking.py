import argparse
import csv
import html
import os
import re
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any, Iterable, Iterator, List, Optional

try:
    from bs4 import BeautifulSoup, NavigableString, Tag
except ImportError:  # pragma: no cover
    BeautifulSoup = None
    NavigableString = None
    Tag = None

try:
    import torch
except ImportError:  # pragma: no cover
    torch = None

try:
    from transformers import AutoModel, AutoTokenizer
except ImportError:  # pragma: no cover
    AutoModel = None
    AutoTokenizer = None

STRUCTURE_PATTERNS = [
    ("chapter", re.compile(r"^Chương\b|prov-chapter|chuong", re.I)),
    ("section", re.compile(r"^Mục\b|prov-section|muc\b", re.I)),
    ("article", re.compile(r"^Điều\b|prov-article|die[u|̀]u\b", re.I)),
    ("clause", re.compile(r"^\d+\.|^Khoản\b|prov-clause|kho[aà]n\b", re.I)),
    ("item", re.compile(r"^[a-z]\)|^[a-z]\.|^\([a-z]\)|prov-item|mục a\b|điểm\b", re.I)),
]

LEVEL_INDEX = {
    "document": 0,
    "chapter": 1,
    "section": 2,
    "article": 3,
    "clause": 4,
    "item": 5,
    "content": 6,
}

BLOCK_TAGS = {"p", "div", "table", "ol", "ul", "li", "tr", "td", "th"}

@dataclass
class Chunk:
    id: str
    document_id: str
    text: str
    label: str
    level: str
    parent_id: str
    order: int
    next_id: Optional[str] = None
    attributes: dict[str, Any] = field(default_factory=dict)


def ensure_bs4() -> None:
    if BeautifulSoup is None:
        raise RuntimeError(
            "BeautifulSoup is required for HTML chunking. Install it with: pip install beautifulsoup4"
        )


def ensure_transformers() -> None:
    if AutoModel is None or AutoTokenizer is None or torch is None:
        raise RuntimeError(
            "transformers and torch are required for embeddings. "
            "Install them with: pip install transformers torch"
        )


def normalize_text(text: str) -> str:
    normalized = html.unescape(text or "")
    normalized = re.sub(r"\s+", " ", normalized)
    return normalized.strip()


def clean_html(soup: "BeautifulSoup") -> None:
    for tag in soup.find_all(True):
        if tag.name == "br":
            tag.replace_with("\n")
            continue
        for attr in list(tag.attrs):
            if attr.lower() in {
                "style",
                "class",
                "id",
                "align",
                "cellspacing",
                "cellpadding",
                "border",
                "width",
                "height",
                "valign",
                "bgcolor",
                "font",
                "face",
                "size",
            }:
                del tag.attrs[attr]

    for obsolete in soup(["script", "style", "link", "meta"]):
        obsolete.decompose()


def iter_blocks(root: "Tag") -> Iterator["Tag"]:
    for child in root.children:
        if isinstance(child, NavigableString):
            continue
        if child.name in BLOCK_TAGS:
            yield child
        else:
            yield from iter_blocks(child)


def classify_block(element: "Tag") -> tuple[str, str]:
    text = normalize_text(element.get_text(" ", strip=True))
    class_names = " ".join(
        [str(c) for c in element.get("class", []) if c]
    ).strip()
    candidate = f"{class_names} {element.name} {text[:120]}"

    for level, pattern in STRUCTURE_PATTERNS:
        if pattern.search(candidate):
            label = text
            return level, label

    # If the text begins with a common heading term, treat it as structure.
    if re.match(r"^Chương\b|^Mục\b|^Điều\b|^Khoản\b|^Điểm\b", text, re.I):
        if re.match(r"^Chương\b", text, re.I):
            return "chapter", text
        if re.match(r"^Mục\b", text, re.I):
            return "section", text
        if re.match(r"^Điều\b", text, re.I):
            return "article", text
        if re.match(r"^Khoản\b|^\d+\.", text, re.I):
            return "clause", text
        if re.match(r"^Điểm\b|^[a-z]\)|^[a-z]\.", text, re.I):
            return "item", text

    if element.name == "table":
        return "content", text
    if element.name in {"li", "td", "th", "tr"}:
        return "content", text

    return "content", text


def build_chunks(document_id: str, html_text: str, title: Optional[str] = None) -> tuple[dict[str, Any], List[Chunk]]:
    ensure_bs4()
    soup = BeautifulSoup(html_text, "html.parser")
    clean_html(soup)

    document_label = title or infer_document_label(soup)
    root_node = {
        "id": document_id,
        "type": "Document",
        "title": document_label,
    }

    body = soup.body or soup
    blocks = list(iter_blocks(body))
    parent_stack: List[Chunk] = []
    chunks: List[Chunk] = []
    last_heading: Optional[Chunk] = None

    for order, block in enumerate(blocks, start=1):
        text = normalize_text(block.get_text(" ", strip=True))
        if not text:
            continue

        level, label = classify_block(block)
        chunk_id = f"{document_id}:{len(chunks)+1:03d}"

        if level == "content":
            parent_id = last_heading.id if last_heading is not None else document_id
        else:
            while parent_stack and LEVEL_INDEX[parent_stack[-1].level] >= LEVEL_INDEX[level]:
                parent_stack.pop()
            parent_id = parent_stack[-1].id if parent_stack else document_id

        chunk = Chunk(
            id=chunk_id,
            document_id=document_id,
            text=text,
            label=label,
            level=level,
            parent_id=parent_id,
            order=order,
            attributes={
                "tag": block.name,
                "class": block.get("class", []),
            },
        )

        chunks.append(chunk)

        if level != "content":
            parent_stack.append(chunk)
            last_heading = chunk

    group_by_parent = defaultdict(list)
    for chunk in chunks:
        group_by_parent[chunk.parent_id].append(chunk)

    for parent_id, siblings in group_by_parent.items():
        siblings.sort(key=lambda c: c.order)
        for first, second in zip(siblings, siblings[1:]):
            first.next_id = second.id

    return root_node, chunks


def infer_document_label(soup: "BeautifulSoup") -> str:
    title_tag = soup.find("title")
    if title_tag and title_tag.string:
        return normalize_text(title_tag.string)
    first_strong = soup.find("strong")
    if first_strong:
        return normalize_text(first_strong.get_text(" ", strip=True))
    return "Document"


_EMBEDDING_CACHE: dict[str, tuple[Any, Any]] = {}

def load_embedding_model(model_name: str, device: str = "cpu") -> tuple[Any, Any]:
    ensure_transformers()
    cache_key = f"{model_name}@{device}"
    if cache_key in _EMBEDDING_CACHE:
        return _EMBEDDING_CACHE[cache_key]

    tokenizer = AutoTokenizer.from_pretrained(model_name, use_fast=True)
    model = AutoModel.from_pretrained(model_name)
    model.to(torch.device(device))
    model.eval()
    _EMBEDDING_CACHE[cache_key] = (tokenizer, model)
    return tokenizer, model


def mean_pooling(model_output: Any, attention_mask: Any) -> Any:
    token_embeddings = model_output.last_hidden_state
    input_mask_expanded = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
    sum_embeddings = torch.sum(token_embeddings * input_mask_expanded, dim=1)
    sum_mask = torch.clamp(input_mask_expanded.sum(dim=1), min=1e-9)
    return sum_embeddings / sum_mask


def embed_texts(
    texts: list[str],
    tokenizer: Any,
    model: Any,
    batch_size: int = 16,
) -> list[list[float]]:
    vectors: list[list[float]] = []
    for start in range(0, len(texts), batch_size):
        batch = texts[start : start + batch_size]
        encoded = tokenizer(
            batch,
            padding=True,
            truncation=True,
            return_tensors="pt",
            max_length=512,
        )
        encoded = {k: v.to("cpu") for k, v in encoded.items()}
        with torch.no_grad():
            outputs = model(**encoded)
        embedding = (
            outputs.pooler_output
            if hasattr(outputs, "pooler_output") and outputs.pooler_output is not None
            else mean_pooling(outputs, encoded["attention_mask"])
        )
        vectors.extend(embedding.cpu().tolist())
    return vectors


def attach_embeddings(
    chunks: List[Chunk],
    tokenizer: Any,
    model: Any,
    batch_size: int = 16,
) -> None:
    texts = [chunk.text for chunk in chunks]
    vectors = embed_texts(texts, tokenizer=tokenizer, model=model, batch_size=batch_size)
    for chunk, vector in zip(chunks, vectors):
        setattr(chunk, "embedding", vector)


def load_content_csv(path: str) -> Iterator[tuple[str, str]]:
    try:
        csv.field_size_limit(10 * 1024 * 1024)
    except OverflowError:
        csv.field_size_limit(2**31 - 1)

    with open(path, "r", encoding="utf-8-sig", newline="") as fp:
        reader = csv.DictReader(fp)
        if "id" not in reader.fieldnames or "content_html" not in reader.fieldnames:
            raise ValueError("content.csv phải chứa cột id và content_html")
        for row in reader:
            yield row["id"].strip(), row["content_html"]


def load_metadata_csv(path: str) -> dict[str, dict[str, str]]:
    metadata = {}
    with open(path, "r", encoding="utf-8-sig", newline="") as fp:
        reader = csv.DictReader(fp)
        for row in reader:
            doc_id = row.get("id") or row.get("doc_id")
            if doc_id:
                metadata[doc_id.strip()] = {k: v for k, v in row.items() if k and v is not None}
    return metadata


def print_chunk_tree(root: dict[str, Any], chunks: List[Chunk], max_depth: int = 5) -> None:
    children = defaultdict(list)
    for chunk in chunks:
        children[chunk.parent_id].append(chunk)

    for chunk_list in children.values():
        chunk_list.sort(key=lambda c: c.order)

    def walk(node_id: str, depth: int) -> None:
        if depth > max_depth:
            return
        for chunk in children.get(node_id, []):
            indent = "  " * depth
            snippet = chunk.text if len(chunk.text) < 140 else chunk.text[:137] + "..."
            print(f"{indent}- [{chunk.level}] {chunk.label}")
            print(f"{indent}  id={chunk.id}, parent_id={chunk.parent_id}, next_id={chunk.next_id}")
            print(f"{indent}  text={snippet}\n")
            walk(chunk.id, depth + 1)

    print(f"Document: {root['title']} ({root['id']})")
    walk(root["id"], 1)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Chunk HTML legal documents into a hierarchical parent-child structure."
    )
    parser.add_argument(
        "--content-csv",
        default="content.csv",
        help="Path to content.csv containing id and content_html columns.",
    )
    parser.add_argument(
        "--metadata-csv",
        default=None,
        help="Optional metadata.csv to map document ids to titles.",
    )
    parser.add_argument(
        "--doc-id",
        default=None,
        help="If provided, only chunk the specified document id.",
    )
    parser.add_argument(
        "--sample",
        type=int,
        default=1,
        help="Number of documents to sample and print after chunking.",
    )
    parser.add_argument(
        "--output-json",
        default=None,
        help="Optional output path to save chunk results as JSON.",
    )
    parser.add_argument(
        "--embed",
        action="store_true",
        help="Generate embeddings for each chunk using the Vietnamese HuggingFace model.",
    )
    parser.add_argument(
        "--embedding-model",
        default="thuannc/vi-distilled-msmarco-MiniLM-L12-cos-v5",
        help="HuggingFace model to use for chunk embeddings.",
    )
    parser.add_argument(
        "--embedding-batch-size",
        type=int,
        default=16,
        help="Batch size for tokenizing and embedding chunks.",
    )
    args = parser.parse_args()

    if args.content_csv and not os.path.exists(args.content_csv):
        parser.error(f"File not found: {args.content_csv}")

    metadata = load_metadata_csv(args.metadata_csv) if args.metadata_csv else {}
    results = []
    count = 0

    tokenizer = model = None
    if args.embed:
        tokenizer, model = load_embedding_model(args.embedding_model, device="cpu")

    for doc_id, html_text in load_content_csv(args.content_csv):
        if args.doc_id and str(doc_id) != str(args.doc_id):
            continue
        title = metadata.get(doc_id, {}).get("title") if metadata else None
        root, chunks = build_chunks(str(doc_id), html_text, title)
        if args.embed:
            print(f"Embedding {len(chunks)} chunks for document {doc_id} using {args.embedding_model} on CPU...")
            attach_embeddings(chunks, tokenizer=tokenizer, model=model, batch_size=args.embedding_batch_size)
        count += 1
        chunk_records = []
        for chunk in chunks:
            payload = chunk.__dict__.copy()
            if hasattr(chunk, "embedding"):
                payload["embedding"] = getattr(chunk, "embedding")
            chunk_records.append(payload)
        results.append({"document": root, "chunks": chunk_records})
        if count <= args.sample:
            print("=" * 80)
            print(f"Sample chunking output for document id={doc_id}")
            print_chunk_tree(root, chunks)
            print("=" * 80)
        if args.doc_id and count >= args.sample:
            break

    if args.output_json:
        import json
        with open(args.output_json, "w", encoding="utf-8") as fp:
            json.dump(results, fp, ensure_ascii=False, indent=2)
        print(f"Saved chunk results to {args.output_json}")

    if count == 0:
        print("No documents were processed. Check --doc-id or input file.")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
