from fastapi import APIRouter
from app.evaluation.recall_eval import evaluate_recall_at_k

router = APIRouter()

@router.get("/eval/recall")
def run_recall_eval(k: int = 4):
    return evaluate_recall_at_k(top_k=k)