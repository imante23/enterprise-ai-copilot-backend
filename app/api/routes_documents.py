from fastapi import APIRouter
from app.db.vector_store import list_documents

router = APIRouter()

@router.get("/documents")
def get_documents():
    return list_documents()