from fastapi import APIRouter, UploadFile, File
import shutil
import os
from app.services.ingestion_service import ingest_document

router = APIRouter()

@router.post("/upload")
async def upload(file: UploadFile = File(...)):
    file_location = f"temp_{file.filename}"

    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    result = ingest_document(file_location, file.filename)

    os.remove(file_location)

    return {
        "status": "success",
        "chunks_created": result["chunks_created"],
        "document_id": result["document_id"],
        "embedding_model": "text-embedding-3-small"
    }


