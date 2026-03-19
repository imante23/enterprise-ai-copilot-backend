from openai import OpenAI
from app.core.config import settings
import logging
import time

client = OpenAI(api_key=settings.OPENAI_API_KEY)

logger = logging.getLogger("llm_service")

# Precio gpt-4o-mini 
PRICE_INPUT_PER_1K = 0.00015
PRICE_OUTPUT_PER_1K = 0.0006

# Límite preventivo de output (respuesta)
MAX_OUTPUT_TOKENS = 300

# Límite preventivo de input (contexto + prompt + pregunta)
MAX_INPUT_TOKENS_ALLOWED = 1700



def estimate_tokens(text: str) -> int:
    """
    Aproximación simple:
    1 token ≈ 4 caracteres
    """
    return len(text) // 4


def generate_answer(prompt: str):

    # Control ANTES de gastar dinero
    estimated_input_tokens = estimate_tokens(prompt)

    if estimated_input_tokens > MAX_INPUT_TOKENS_ALLOWED:
        return {
            "answer": "Input too large. Context exceeds token policy limits.",
            "usage": {
                "prompt_tokens_estimated": estimated_input_tokens,
                "completion_tokens": 0,
                "total_tokens": estimated_input_tokens,
                "estimated_cost_usd": 0
            }
        }
    
    # Arranca medición de tiempo
    start_time = time.perf_counter()

   
    response = client.chat.completions.create(
        model=settings.MODEL_NAME,
        messages=[
            {
            #System estricto para evitar alucinaciones
            "role": "system",
            "content": """
                You are a strict enterprise AI assistant.

                You must answer ONLY using the provided context.
                DO NOT use prior knowledge.
                DO NOT make assumptions.

                When using information from the context, you MUST cite it in this format:

                "According to document {name}, section {number}..."

                Use the source and section labels exactly as they appear in the context.

                If the answer is not explicitly found in the context, respond with exactly:

                "I don't know, based on the documents provided."
                """
            },
            #User con la consulta (Contexto + pregunta)
            {"role": "user", "content": prompt},
        ],
        temperature=0.2,
        max_tokens=MAX_OUTPUT_TOKENS,
    )

    # FIN de la medicion
    end_time = time.perf_counter()
    latency_ms = round((end_time - start_time) * 1000, 2)

   
   
    usage = response.usage

    prompt_tokens = usage.prompt_tokens
    completion_tokens = usage.completion_tokens
    total_tokens = usage.total_tokens

    # Estimación de costo real
    estimated_cost = (
        (prompt_tokens / 1000) * PRICE_INPUT_PER_1K +
        (completion_tokens / 1000) * PRICE_OUTPUT_PER_1K
    )

    # print("\n--- TOKEN USAGE ---")
    # print(f"Prompt tokens: {prompt_tokens}")
    # print(f"Completion tokens: {completion_tokens}")
    # print(f"Total tokens: {total_tokens}")
    # print(f"Estimated cost (USD): ${estimated_cost:.6f}")
    # print("-------------------\n")

    
    #Pensado para produccion y analizar datos de mas usuarios
    logger.info(
        "llm_call_completed",
        extra={
            "extra_data": {
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "total_tokens": total_tokens,
                "estimated_cost_usd": round(estimated_cost, 6),
                "latency_ms": latency_ms
            }
        }
    )

    return {
        "answer": response.choices[0].message.content,
        "usage": {
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": total_tokens,
            "estimated_cost_usd": round(estimated_cost, 6),
            "latency_ms": latency_ms
        }
    }