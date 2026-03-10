# System Design Walkthrough - Compliance Analysis API

This document explains the **architectural decisions behind the Compliance Analysis API**.
The goal of this project is to demonstrate **modern GenAI backend design patterns** used in real-world AI systems.

The system focuses on:

* modular architecture
* model-agnostic LLM integration
* retrieval augmented generation (RAG)
* cost-efficient inference
* clean API design

---

# 1. Problem Statement

Organizations produce large volumes of documents such as:

* privacy policies
* marketing disclosures
* financial compliance statements
* internal governance documents

Manually verifying these documents against **regulatory compliance rules** is slow and error-prone.

This system provides an automated way to:

1. ingest documents
2. retrieve relevant sections
3. evaluate them against compliance rules
4. generate structured violation reports

---

# 2. Design Goals

The architecture was designed with the following goals:

### 1 Simplicity

The system intentionally avoids heavy frameworks to maintain clarity.

This makes the project easier to:

* understand
* extend
* run locally

---

### 2 Model Agnostic Design

LLM providers change rapidly.
The architecture ensures models can be swapped without rewriting the system.

Supported providers:

* OpenAI
* local models via Ollama
* any OpenAI-compatible endpoint

This is achieved using a **shared LLM interface**.

---

### 3 Cost Efficient Inference

Large language models are expensive.

To reduce cost, the system performs **deterministic filtering before LLM analysis**.

This ensures only relevant document sections are sent to the model.

---

### 4 Modular Pipeline

Each stage of processing is isolated:

* parsing
* chunking
* embeddings
* retrieval
* analysis

This makes the pipeline easier to debug and extend.

---

# 3. High-Level Architecture

The system follows a **RAG-based document analysis pipeline**.

```
Document Upload
     ↓
Document Parsing
     ↓
Text Chunking
     ↓
Embedding Generation
     ↓
Vector Search
     ↓
Deterministic Risk Filtering
     ↓
Token Context Limitation
     ↓
LLM Compliance Analysis
     ↓
LLM Judge Validation
     ↓
Structured Compliance Report
```

This architecture reflects the pattern used in many modern **AI knowledge systems**.

---

# 4. Why Retrieval Augmented Generation (RAG)

Sending entire documents directly to LLMs is inefficient.

Problems with naive prompting:

* high token cost
* slower inference
* increased hallucination risk

RAG solves this by:

1. converting text into embeddings
2. retrieving only relevant sections
3. providing focused context to the LLM

Benefits:

* lower token usage
* improved accuracy
* better scalability

---

# 5. Document Processing Pipeline

Documents pass through several preprocessing stages before analysis.

### Parsing

Supported formats:

* PDF
* DOCX
* JSON

Libraries used:

* PyMuPDF for PDFs
* python-docx for Word documents

The parser extracts raw text and basic metadata.

---

### Chunking

Documents are split into smaller sections.

Typical parameters:

* chunk size: 800 tokens
* overlap: 150 tokens

Chunking improves retrieval quality and prevents context window overflow.

Each chunk stores metadata:

* document ID
* page number
* chunk ID

---

### Embedding Generation

Embeddings convert text into vector representations.

This project uses:

```
sentence-transformers
```

Default model:

```
all-MiniLM-L6-v2
```

Advantages:

* open source
* fast inference
* runs locally

---

# 6. Vector Search

The system stores embeddings in **FAISS**.

FAISS was chosen because:

* it runs locally
* it has excellent performance
* it requires minimal infrastructure

Vector search enables **semantic retrieval**, meaning the system can find relevant content even when keywords differ.

Example:

Query:

```
third party data sharing
```

Can retrieve text such as:

```
we may disclose user information to partner organizations
```

---

# 7. Deterministic Risk Filtering

Before invoking the LLM, a rule-based filter is applied.

Compliance rules include keywords such as:

```
share data
third party
user information
```

Chunks matching these keywords are marked as **risk candidates**.

Benefits:

* reduces LLM calls
* lowers token cost
* improves response speed

This hybrid approach (rules + LLM) is common in production AI systems.

### Context Limits & Token Clipping
Filtered chunks are estimated for token count (e.g. `words * 1.3`). If the combined token size exceeds the maximum context limit (e.g. 4000 tokens), the system automatically prunes the lowest-similarity chunks. This strict boundary ensures the LLM does not crash due to context overflow while retaining the most precise vector hits.

---

# 8. LLM Compliance Analysis

Relevant chunks are evaluated by the LLM.

The prompt contains:

* the compliance rule
* the candidate text chunk

The model determines:

* whether a rule is violated
* severity of the issue
* explanation
* citation

Output is returned as **structured JSON**.

---

# 9. LLM Judge Validation

A second LLM pass evaluates the generated analysis.

This stage checks:

* logical consistency
* citation accuracy
* reasoning quality

The judge returns a **confidence score** that helps identify unreliable results.

This pattern is increasingly used in **high-trust AI workflows**.

---

# 10. API Design

The system exposes three main endpoints.

Start analysis:

```
POST /analyze
```

Check job status:

```
GET /status/{job_id}
```

Retrieve results:

```
GET /report/{job_id}
```

Document processing runs **asynchronously** to avoid blocking the API.

---

# 11. Evaluation Pipeline & Metrics

The system includes an automated evaluation pipeline (`app/eval/evaluator.py`) to systematically benchmark the model's accuracy against a curated dataset.

The evaluator compares the LLM's detected compliance violations against a ground-truth dataset expected results list. It calculates:
* True Positives, False Positives, False Negatives
* Precision
* Recall
* F1 Score

This module guarantees that future modifications to prompts or pipeline retrieval steps can be objectively measured for regression.

---

# 12. Model Abstraction Layer

All LLM calls pass through a shared interface.

Example structure:

```
BaseLLM
   ├── OpenAIClient
   └── OllamaClient
```

This design ensures the rest of the pipeline does not depend on any specific provider.

Switching models only requires updating environment variables.

---

# 13. Why FastAPI

FastAPI was chosen because it provides:

* high performance
* automatic OpenAPI documentation
* async support
* easy testing

The `/docs` endpoint provides interactive API testing.

---

# 14. Logging and Observability

The system logs important metadata for each request:

* request ID
* job ID
* model used
* processing time

This improves debugging and transparency.

---

# 15. Deployment Strategy

The project includes a **Dockerfile** to simplify deployment.

Benefits:

* consistent runtime environment
* easy cloud deployment
* reproducible builds

---

# 16. Tradeoffs

Several deliberate tradeoffs were made for simplicity.

Not included in the initial version:

* clause extraction models
* complex multi-agent orchestration
* knowledge graphs
* distributed vector databases

These features could be added in future versions.

---

# 17. Possible Future Extensions

The architecture is designed to support upgrades such as:

* clause classification models
* advanced reranking
* legal knowledge graphs
* multi-agent reasoning
* compliance dashboards
* distributed vector stores

---

# 18. Key Takeaways

This project demonstrates how to build a **clean GenAI backend architecture** using modern patterns:

* retrieval augmented generation
* model abstraction
* vector search
* deterministic filtering
* LLM validation

These patterns are commonly used in real-world AI systems that must balance **accuracy, cost, and scalability**.
