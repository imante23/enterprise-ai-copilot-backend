from typing import Optional
from app.services.embedding_service import generate_embedding
from app.db.vector_store import collection


def retrieve_relevant_chunks(
    query: str,
    top_k: int = 4,
    document_ids: Optional[list[str]] = None,
    expand_neighbors: bool = False
):

    query_embedding = generate_embedding(query)

    initial_k = top_k * 3

    query_params = {
        "query_embeddings": [query_embedding],
        "n_results": initial_k,
        "include": ["documents", "metadatas", "distances"]
    }

    # Filtro desde frontend
    if document_ids:
        query_params["where"] = {
            "document_id": {"$in": document_ids}
        }

    results = collection.query(**query_params)

    documents = results["documents"][0]
    metadatas = results["metadatas"][0]
    distances = results["distances"][0]
    ids = results["ids"][0]

    ranked = sorted(
        zip(documents, metadatas, distances, ids),
        key=lambda x: x[2]  # menor distancia = más relevante
    )

  
    if not document_ids and ranked:

        doc_scores = {}

        for _, meta, distance, _ in ranked:
            doc_id = meta["document_id"]
            doc_scores.setdefault(doc_id, []).append(distance)

        best_doc = min(
            doc_scores,
            key=lambda d: sum(doc_scores[d]) / len(doc_scores[d])
        )

        ranked = [
            item for item in ranked
            if item[1]["document_id"] == best_doc
        ]

    base_chunks = ranked[:top_k]

    if not base_chunks:
        return {
            "documents": [[]],
            "metadatas": [[]],
            "ids": [[]],
            "sources": [],
            "document_ids": []
        }

    effective_doc_ids = list(
        {meta["document_id"] for _, meta, _, _ in base_chunks}
    )

    effective_doc_id = effective_doc_ids[0]

   # SIN expansión de vecinos
    if not expand_neighbors:

        sources = []

        for doc, meta, distance, chunk_id in base_chunks:
            sources.append({
                "file": meta.get("source_file"),
                "section": meta.get("chunk_index"),
                "chunk_id": chunk_id,
                "score": distance
            })


        return {
            "documents": [[doc for doc, _, _, _ in base_chunks]],
            "metadatas": [[meta for _, meta, _, _ in base_chunks]],
            "ids": [[chunk_id for _, _, _, chunk_id in base_chunks]],
            "sources": sources,
            "document_ids": effective_doc_ids
        }

 
    #Expansi+on de vecinos
    neighbor_indices = set()

    for _, meta, _, _ in base_chunks:
        idx = meta["chunk_index"]
        neighbor_indices.update([idx - 1, idx, idx + 1])

    neighbor_indices = [i for i in neighbor_indices if i >= 0]

    neighbor_results = collection.get(
        where={
            "$and": [
                {"document_id": effective_doc_id},
                {"chunk_index": {"$in": neighbor_indices}}
            ]
        },
        include=["documents", "metadatas"]
    )

    seen = set()
    final_docs = []

    for doc, meta, chunk_id in zip(
        neighbor_results["documents"],
        neighbor_results["metadatas"],
        neighbor_results["ids"]
    ):
        key = (meta["document_id"], meta["chunk_index"])
        
        if key not in seen:
            seen.add(key)

            # score aproximado (no viene del get)
            score = next(
                (d for _, m, d, cid in ranked if cid == chunk_id),
                None
            )

            final_docs.append((doc, meta, chunk_id, score))

    final_docs = sorted(final_docs, key=lambda x: x[1]["chunk_index"])
    final_docs = final_docs[: top_k * 2]


    sources = []

    for doc, meta, chunk_id, score in final_docs:
        sources.append({
            "file": meta.get("source_file"),
            "section": meta.get("chunk_index"),
            "chunk_id": chunk_id,
            "score": score
        })

    return {
        "documents": [[doc for doc, _, _, _ in final_docs]],
        "metadatas": [[meta for _, meta, _, _ in final_docs]],
        "ids": [[chunk_id for _, _, chunk_id, _ in final_docs]],
        "sources": sources,
        "document_ids": effective_doc_ids
    }

