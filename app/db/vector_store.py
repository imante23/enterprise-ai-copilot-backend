import chromadb
from chromadb.config import Settings as ChromaSettings
import os

os.makedirs("uploads", exist_ok=True)
os.makedirs("chroma_db", exist_ok=True)

chroma_client = chromadb.Client(
    ChromaSettings(
        persist_directory="chroma_db",
        anonymized_telemetry=False,
    )
)

collection = chroma_client.get_or_create_collection(
    name="enterprise_knowledge"
)



def list_documents():
    results = collection.get(
        include=["metadatas"],
        limit=10000  
    )

    metadatas = results.get("metadatas", [])

    if not metadatas:
        return []

    documents = {}

    for meta in metadatas:
        doc_id = meta["document_id"]
        source = meta.get("source_file", "unknown")

        if doc_id not in documents:
            documents[doc_id] = {
                "document_id": doc_id,
                "source_file": source,
                "chunks": 0
            }

        documents[doc_id]["chunks"] += 1

    return list(documents.values())