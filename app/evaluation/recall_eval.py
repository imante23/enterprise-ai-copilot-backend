EVAL_DATASET = [
    {
        "question": "¿De cuánto es el exceso de peso en Argentina?",
        "expected_document": "Malnutricion_Arg_Unicef.pdf"
    },
    {
        "question": "¿Dónde hay datos de encuestas?",
        "expected_document": "Malnutricion_Arg_Unicef.pdf"
    },
    {
        "question": "¿Dónde hay datos de la Organización Panamericána de la Salud?",
        "expected_document": "Malnutricion_Arg_Unicef.pdf"
    },

     {
        "question": "¿Cuál es la estrategia de UNICEF hacia 2030?",
        "expected_document": "Malnutricion_Arg_Unicef.pdf"
    },

     {
        "question": "¿Componentes de alimentación saludable?",
        "expected_document": "Malnutricion_Arg_Unicef.pdf"
    },

     {
        "question": "¿Qué es desnutrición?",
        "expected_document": "Desnutricion_Pediatria.pdf"
    },
       {
        "question": "¿Qué es fisiopatología?",
        "expected_document": "Desnutricion_Pediatria.pdf"
    },
       {
        "question": "¿Qué es la antropometría?",
        "expected_document": "Desnutricion_Pediatria.pdf"
    },
       {
        "question": "¿Evaluación de la bioquímica?",
        "expected_document": "Desnutricion_Pediatria.pdf"
    },
       {
        "question": "¿Cómo se clasifica la desnutrición?",
        "expected_document": "Desnutricion_Pediatria.pdf"
    },
   
]

from app.services.retrieval_service import retrieve_relevant_chunks

def evaluate_recall_at_k(top_k: int = 4):

    correct = 0

    for sample in EVAL_DATASET:

        retrieval = retrieve_relevant_chunks(
            query=sample["question"],
            top_k=top_k,
            expand_neighbors=False
        )

        retrieved_metadatas = retrieval["metadatas"][0]

        retrieved_files = [
            meta.get("source_file")
            for meta in retrieved_metadatas
        ]

        # Se normaliza el nombre de archivo
        retrieved_files = [
            file.split("/")[-1] for file in retrieved_files
        ]

        expected_file = sample["expected_document"]

        if expected_file in retrieved_files:
            correct += 1

    recall = correct / len(EVAL_DATASET)

    print("Question:", sample["question"])
    print("Expected:", expected_file)
    print("Retrieved:", retrieved_files)
    print("----")

    return {
        "recall_at_k": round(recall, 3),
        "correct": correct,
        "total": len(EVAL_DATASET)
    }