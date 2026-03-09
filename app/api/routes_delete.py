from fastapi import APIRouter
from app.services.ingestion_service import delete_document_by_id

router = APIRouter()

@router.delete("/documents/{document_id}")
def delete_document(document_id: str):
    delete_document_by_id(document_id)
    return {"status": "deleted"}