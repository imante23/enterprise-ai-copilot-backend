from fastapi import APIRouter
from pydantic import BaseModel
from app.services.retrieval_service import retrieve_relevant_chunks
from app.services.llm_service import generate_answer
import time
from typing import Optional, List
from app.services.llm_service import estimate_tokens, MAX_INPUT_TOKENS_ALLOWED

router = APIRouter()

class QuestionRequest(BaseModel):
    question: str
    document_ids: Optional[List[str]] = None
    expand_neighbors: Optional[bool] = False

@router.post("/ask")
def ask(request: QuestionRequest):
    start_time = time.time()

    retrieval = retrieve_relevant_chunks(
        query=request.question,
        document_ids=request.document_ids,
        expand_neighbors=request.expand_neighbors
    )

   

    documents = retrieval["documents"][0]
    metadatas = retrieval["metadatas"][0]
    

    context = ""
    used_sources = []

    for i, doc in enumerate(documents):

        source = metadatas[i].get("source_file", "Unknown")
        section = metadatas[i].get("chunk_index", "N/A")

        labeled_chunk = f"[Documento: {source} | Sección {section}]\n{doc}"

        tentative_context = context + "\n\n" + labeled_chunk
        
        # Estimación de tokens de contexto + pregunta, si son mas altos de lo permitido no se envian al LLM
        estimated_tokens = estimate_tokens(
            f"Context:\n{tentative_context}\n\nQuestion:\n{request.question}"
        )

        if estimated_tokens > MAX_INPUT_TOKENS_ALLOWED:
            break

        context = tentative_context

        source_entry = {
            "file": source,
            "section": section
        }

        

    prompt = f"""
    Context:
    {context}

    Question:
    {request.question}
    """

    llm_response = generate_answer(prompt)

    latency = int((time.time() - start_time) * 1000)

    return {
        "answer": llm_response["answer"],
        "sources": retrieval["ids"][0],
        "confidence": "medium",
        "latency_ms": latency,
        "tokens": llm_response["usage"]
    }

