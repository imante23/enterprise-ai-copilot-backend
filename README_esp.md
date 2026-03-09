# Enterprise RAG System – Proyecto de portafolio 

## Descripción general

Este proyecto es un **sistema de Retrieval-Augmented Generation (RAG) orientado a producción**, construido con un stack moderno de IA.

Permite a los usuarios subir documentos, consultarlos en lenguaje natural y recibir respuestas estrictamente basadas en el contenido de los documentos con citas estructuradas.

El sistema incluye:

- Ingesta y fragmentación de documentos
- Recuperación semántica basada en embeddings
- Generación con LLM consciente del contexto
- Control de tokens y estimación de costos
- Aplicación obligatoria de citas de fuente
- Pipeline de evaluación Recall@k
- Interfaz de chat con optimizaciones de UX

---

# Arquitectura

## Backend

- **FastAPI** – capa de API
- Arquitectura modular de servicios
- Separación clara de responsabilidades:

- `retrieval_service`
- `llm_service`
- `evaluation`
- `routes`

## Stack de IA

- Modelo de chat de OpenAI (configurable)
- Recuperación basada en embeddings
- Base de datos vectorial (Chroma o equivalente)

## Frontend

- React + TypeScript
- Interfaz estilo chat
- Campo de entrada con autoajuste de tamaño
- Efecto de escritura en las respuestas del asistente
- Selección de múltiples documentos
- Opción de recuperación optimizada

---

# Funcionalidades principales

## 1. Pipeline de Ingesta de Documentos

- Soporte para subida de archivos PDF
- Manejo de PDFs cifrados con AES (dependencia `cryptography`)
- Estrategia de fragmentación con preservación de metadatos

Metadatos almacenados por fragmento:

- archivo fuente
- sección
- id del documento

---

## 2. Sistema de Recuperación

- Búsqueda por similitud semántica
- Expansión opcional de vecinos (`expand_neighbors`)
- Filtrado por múltiples documentos
- Construcción de contexto consciente del límite de tokens
- Control preventivo del límite de tokens de entrada

### Protección de Tokens

Antes de llamar al LLM:

- Estimación de tokens de **contexto + pregunta**
- Límite estricto (`MAX_INPUT_TOKENS_ALLOWED`)
- Manejo seguro si se excede el límite

---

## 3. Guardrails para el LLM

El prompt del sistema fuerza:

- Uso exclusivo del contexto proporcionado
- Prohibición de alucinaciones
- Formato obligatorio de citación

Formato requerido:

> "Según el documento {nombre}, sección {número}..."

Si la información no se encuentra:

> "No lo sé, basándome en los documentos proporcionados"

Se utiliza una temperatura baja para respuestas determinísticas.

---

## 4. Seguimiento de costos y uso

Seguimiento por solicitud:

- Tokens de prompt
- Tokens de respuesta
- Tokens totales
- Costo estimado en USD
- Latencia (ms)

El modelo de precios es configurable por cada 1000 tokens.

Esto demuestra **conciencia de costos**, una habilidad crítica en sistemas de IA en producción.

---

## 5. Framework de Evaluación

### Implementación de Recall@k

Pipeline de evaluación personalizado para medir la calidad de recuperación.

Incluye:

- Dataset manual de preguntas de evaluación
- Mapeo de documentos esperados
- Cálculo de recall top-k
- Endpoint de API para evaluación

Ejemplo de salida:

```json
{
  "recall_at_k": 0.8,
  "correct": 8,
  "total": 10
}
```

Esto demuestra comprensión de:

* Métricas de recuperación
* Evaluación offline
* Separación entre rendimiento de recuperación y generación

---

# Aspectos destacados de ingeniería

✔ Arquitectura Retrieval-Augmented Generation
✅ Gestión de tokens y optimización de costos
✅ Capacidad de logging estructurado
✅ Métricas de evaluación
✅ Guardrails contra alucinaciones
✅ Diseño backend modular y limpio
✅ Implementación frontend con foco en UX

---

# Conceptos avanzados demostrados

* Gestión de ventanas de contexto
* Prompting determinístico para LLM
* Recuperación de fragmentos consciente de metadatos
* Medición de latencia
* Modelado de estimación de costos
* Manejo de errores similar a producción
* Selección de modelos basada en configuración


---

# Estructura del proyecto

```
app/
 ├── core/
 ├── services/
 │    ├── retrieval_service.py
 │    ├── llm_service.py
 ├── routes/
 │    ├── routes_ask.py
 ├── evaluation/
 │    ├── recall_eval.py
frontend/
 ├── Chat.tsx
```

---

# ¿Por qué es importante este proyecto?

Este proyecto demuestra habilidades prácticas de ingeniería en IA más allá de la experimentación con prompts:

* Diseño de sistemas de IA end-to-end
* Construcción de pipelines de evaluación
* Gestión del costo de inferencia
* Implementación de restricciones de seguridad
* Diseño de servicios backend escalables

Refleja pensamiento de producto de IA del mundo real, no solo experimentación.

---

# Posibles mejoras futuras

* Métricas Precision@k y MRR
* Evaluación automática de calidad de respuestas
* Respuestas en streaming
* Búsqueda híbrida (BM25 + embeddings)
* Soporte multi-tenant
* Control de acceso basado en roles
* Despliegue con Docker + CI/CD

---

# Autor

AI Engineer Portfolio Project
Enfocado en Sistemas de Recuperación, Integración de LLM, y Diseño de IA para producción.


