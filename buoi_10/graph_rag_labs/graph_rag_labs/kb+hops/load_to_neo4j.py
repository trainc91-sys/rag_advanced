import argparse
import csv
import json
import os
import re
import time
from typing import Any

from neo4j import GraphDatabase


def sanitize_relation_type(relation_type: str) -> str:
    candidate = re.sub(r"[^A-Za-z0-9_]+", "_", relation_type.strip().upper())
    if not re.match(r"^[A-Za-z_][A-Za-z0-9_]*$", candidate):
        raise ValueError(f"Invalid relationship type: {relation_type}")
    return candidate


def load_chunks_from_json(path: str) -> list[dict[str, Any]]:
    with open(path, "r", encoding="utf-8") as fp:
        return json.load(fp)


def load_relationships_csv(path: str) -> list[tuple[str, str, str, str]]:
    relationships = []
    with open(path, "r", encoding="utf-8-sig", newline="") as fp:
        reader = csv.DictReader(fp)
        for row in reader:
            doc_id = row.get("doc_id")
            other_doc_id = row.get("other_doc_id")
            rel_text = row.get("relationship") or ""
            rel_type = row.get("relationship_type") or rel_text
            if doc_id and other_doc_id:
                relationships.append((doc_id.strip(), other_doc_id.strip(), rel_text.strip(), rel_type.strip()))
    return relationships


def create_constraints(tx: Any) -> None:
    tx.run("CREATE CONSTRAINT IF NOT EXISTS FOR (d:Document) REQUIRE d.id IS UNIQUE")
    tx.run("CREATE CONSTRAINT IF NOT EXISTS FOR (c:Chunk) REQUIRE c.id IS UNIQUE")


def merge_document(tx: Any, doc_id: str, props: dict[str, Any]) -> None:
    tx.run(
        "MERGE (d:Document {id:$id}) SET d += $props",
        id=doc_id,
        props=props,
    )


def merge_chunk(tx: Any, chunk: dict[str, Any]) -> None:
    attributes = chunk.get("attributes") or {}
    props = {
        "id": chunk["id"],
        "document_id": chunk["document_id"],
        "text": chunk.get("text", ""),
        "label": chunk.get("label", ""),
        "level": chunk.get("level", ""),
        "order": chunk.get("order"),
        "tag": attributes.get("tag"),
        "class_names": attributes.get("class"),
        "embedding": chunk.get("embedding"),
    }
    tx.run(
        "MERGE (c:Chunk {id:$id}) SET c += $props",
        id=props["id"],
        props=props,
    )


def create_part_of(tx: Any, chunk_id: str, document_id: str) -> None:
    tx.run(
        "MATCH (c:Chunk {id:$chunk_id}), (d:Document {id:$doc_id}) "
        "MERGE (c)-[:PART_OF]->(d)",
        chunk_id=chunk_id,
        doc_id=document_id,
    )


def create_parent_of(tx: Any, parent_id: str, child_id: str) -> None:
    tx.run(
        "MATCH (parent:Chunk {id:$parent_id}), (child:Chunk {id:$child_id}) "
        "MERGE (parent)-[:PARENT_OF]->(child)",
        parent_id=parent_id,
        child_id=child_id,
    )


def create_next(tx: Any, current_id: str, next_id: str) -> None:
    tx.run(
        "MATCH (current:Chunk {id:$current_id}), (next:Chunk {id:$next_id}) "
        "MERGE (current)-[:NEXT]->(next)",
        current_id=current_id,
        next_id=next_id,
    )


def create_document_relation(tx: Any, doc_id: str, other_doc_id: str, relation_type: str, rel_text: str) -> None:
    rel_type = sanitize_relation_type(relation_type or rel_text)
    tx.run(
        f"MATCH (a:Document {{id:$doc_id}}), (b:Document {{id:$other_doc_id}}) "
        f"MERGE (a)-[r:{rel_type}]->(b) SET r.raw_relation = $rel_text",
        doc_id=doc_id,
        other_doc_id=other_doc_id,
        rel_text=rel_text,
    )


def ensure_database_exists(driver: Any, database: str, create: bool) -> None:
    if database.lower() == "neo4j":
        return

    with driver.session(database="system") as sys_session:
        result = sys_session.run("SHOW DATABASES YIELD name WHERE name = $name", name=database)
        if result.single() is not None:
            return
        if not create:
            raise RuntimeError(
                f"The database '{database}' does not exist. "
                "Run the script again with --create-database to create it, or use an existing database."
            )
        print(f"Creating Neo4j database '{database}'...")
        sys_session.run(f"CREATE DATABASE `{database}` IF NOT EXISTS")
        print(f"Waiting for database '{database}' to become available...")
        for _ in range(30):
            time.sleep(2)
            state = sys_session.run(
                "SHOW DATABASES YIELD name, currentStatus WHERE name = $name",
                name=database,
            ).single()
            if state and state["currentStatus"].lower() == "online":
                return
        raise RuntimeError(f"Database '{database}' did not become online in time.")


def load_to_neo4j(
    uri: str,
    user: str,
    password: str,
    database: str,
    chunks_json: str,
    metadata_csv: str,
    relationships_csv: str,
    create_database: bool = False,
) -> None:
    driver = GraphDatabase.driver(uri, auth=(user, password))
    try:
        ensure_database_exists(driver, database, create_database)
        with driver.session(database=database) as session:
            session.execute_write(create_constraints)

            metadata = {}
            with open(metadata_csv, "r", encoding="utf-8-sig", newline="") as fp:
                reader = csv.DictReader(fp)
                for row in reader:
                    doc_id = (row.get("id") or row.get("doc_id") or "").strip()
                    if not doc_id:
                        continue
                    props = {k: v for k, v in row.items() if k and v is not None}
                    metadata[doc_id] = props

            print(f"Loaded metadata for {len(metadata)} documents.")

            chunks_data = load_chunks_from_json(chunks_json)
            total_chunks = sum(len(item.get("chunks", [])) for item in chunks_data)
            print(f"Loaded {total_chunks} chunks from {chunks_json}.")

            pending_parent_relations: list[tuple[str, str]] = []
            pending_next_relations: list[tuple[str, str]] = []

            for item in chunks_data:
                document = item["document"]
                doc_id = document["id"]
                doc_props = {"title": document.get("title", ""), **metadata.get(doc_id, {})}
                session.execute_write(merge_document, doc_id, doc_props)

                for chunk in item.get("chunks", []):
                    session.execute_write(merge_chunk, chunk)
                    session.execute_write(create_part_of, chunk["id"], doc_id)
                    if chunk.get("parent_id") and chunk["parent_id"] != doc_id:
                        pending_parent_relations.append((chunk["parent_id"], chunk["id"]))
                    if chunk.get("next_id"):
                        pending_next_relations.append((chunk["id"], chunk["next_id"]))

            print(f"Pending parent relations: {len(pending_parent_relations)}")
            for parent_id, child_id in pending_parent_relations:
                session.execute_write(create_parent_of, parent_id, child_id)

            print(f"Pending NEXT relations: {len(pending_next_relations)}")
            for current_id, next_id in pending_next_relations:
                session.execute_write(create_next, current_id, next_id)

            relationships = load_relationships_csv(relationships_csv)
            print(f"Loaded {len(relationships)} document-level relationships.")
            for doc_id, other_doc_id, rel_text, rel_type in relationships:
                session.execute_write(create_document_relation, doc_id, other_doc_id, rel_type, rel_text)

            print("Neo4j import completed.")
    finally:
        driver.close()


def main() -> int:
    parser = argparse.ArgumentParser(description="Load Documents, Chunks, embeddings and relationships into Neo4j.")
    parser.add_argument("--uri", default="neo4j://127.0.0.1:7687", help="Neo4j URI for Bolt connection.")
    parser.add_argument("--user", default="neo4j", help="Neo4j username.")
    parser.add_argument("--password", default="abcd1234", help="Neo4j password.")
    parser.add_argument("--database", default="kb-hops", help="Neo4j database name.")
    parser.add_argument("--create-database", action="store_true", help="Create the Neo4j database if it does not already exist.")
    parser.add_argument("--chunks-json", default="test_chunks.json", help="Path to the JSON file containing chunked documents and embeddings.")
    parser.add_argument("--metadata-csv", default="metadata.csv", help="Path to metadata.csv.")
    parser.add_argument("--relationships-csv", default="relationships.csv", help="Path to relationships.csv.")
    args = parser.parse_args()

    if not os.path.exists(args.chunks_json):
        parser.error(f"Chunks JSON file not found: {args.chunks_json}")
    if not os.path.exists(args.metadata_csv):
        parser.error(f"Metadata CSV file not found: {args.metadata_csv}")
    if not os.path.exists(args.relationships_csv):
        parser.error(f"Relationships CSV file not found: {args.relationships_csv}")

    load_to_neo4j(
        uri=args.uri,
        user=args.user,
        password=args.password,
        database=args.database,
        chunks_json=args.chunks_json,
        metadata_csv=args.metadata_csv,
        relationships_csv=args.relationships_csv,
        create_database=args.create_database,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
