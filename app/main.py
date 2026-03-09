from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.logging import setup_logging
from app.api import routes_upload, routes_ask, routes_documents, routes_delete, routes_eval


setup_logging()

app = FastAPI(
    title="Enterprise AI Knowledge Copilot",
    version="1.0.0"
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



app.include_router(routes_upload.router)
app.include_router(routes_ask.router)
app.include_router(routes_documents.router)
app.include_router(routes_delete.router)
app.include_router(routes_eval.router)

@app.get("/health")
def health():
    return {"status": "ok"}