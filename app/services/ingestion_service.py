import uuid
from pypdf import PdfReader
from app.services.embedding_service import generate_embedding
from app.db.vector_store import collection


CHUNK_SIZE = 600
CHUNK_OVERLAP = 80



def delete_document_by_id(document_id: str):
    collection.delete(
        where={"document_id": document_id}
    )

def delete_document_by_filename(original_filename: str):
    collection.delete(
        where={"source_file": original_filename}
    )


def clean_text(text: str) -> str:
    return " ".join(text.split())

def chunk_text(text: str):
    chunks = []
    start = 0

    while start < len(text):
        end = start + CHUNK_SIZE
        chunks.append(text[start:end])
        start += CHUNK_SIZE - CHUNK_OVERLAP

    return chunks

def extract_text_from_pdf(file_path: str):
    reader = PdfReader(file_path)

    if reader.is_encrypted:
        reader.decrypt("")

    text = ""

    for page in reader.pages:
        text += page.extract_text() or ""

    return text

def ingest_document(file_path: str, original_filename: str):
    delete_document_by_filename(original_filename)

    raw_text = extract_text_from_pdf(file_path)
    text = clean_text(raw_text)

    chunks = chunk_text(text)

    document_id = str(uuid.uuid4())

    all_ids = []
    all_embeddings = []
    all_metadatas = []

    for index, chunk in enumerate(chunks):
        chunk_id = str(uuid.uuid4())
        embedding = generate_embedding(chunk)

        all_ids.append(chunk_id)
        all_embeddings.append(embedding)
        all_metadatas.append({
            "document_id": document_id,
            "chunk_index": index,
            "source_file": original_filename
        })

    collection.add(
        documents=chunks,
        embeddings=all_embeddings,
        ids=all_ids,
        metadatas=all_metadatas
    )

    return {
        "chunks_created": len(chunks),
        "document_id": document_id,
    }