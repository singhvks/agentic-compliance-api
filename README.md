# Compliance Analysis API

<<<<<<< HEAD
This is a REST API for analyzing compliance of cloud resources.

## Project Documentation
Detailed specifications, functional/non-functional requirements, and design considerations can be found in [docs/requirements.md](docs/requirements.md).

## Setup
Python 3.14.2



## Run the API in Local Dev Mode


=======
A **model-agnostic GenAI backend** for analyzing corporate documents against compliance rules using **Retrieval Augmented Generation (RAG)**.

This project demonstrates modern **LLM system architecture** using open-source components and a clean, production-style backend built with FastAPI.

The system accepts documents (PDF/DOCX/JSON), retrieves relevant sections using semantic search, and evaluates them against compliance rules using a configurable LLM.

---

# Key Features

* **Model-Agnostic LLM Layer**
  Switch between OpenAI, Ollama, or any OpenAI-compatible endpoint via configuration.

* **Open Source Embeddings**
  Uses `sentence-transformers` for local embeddings.

* **Vector Search (RAG)**
  Uses **FAISS** for fast semantic retrieval.

* **Compliance Rule Engine**
  Deterministic keyword filtering before LLM analysis to reduce cost.

* **Structured Compliance Reports**
  Returns machine-readable JSON output with citations and recommendations.

* **Automated Evaluation Pipeline**
  Benchmarks Precision, Recall, and F1 scores against a curated evaluation dataset.

* **Asynchronous Processing**
  Document analysis runs in the background to prevent API blocking.

* **Containerized Deployment**
  Includes Docker support.

---

# System Architecture

The system follows a **simplified RAG architecture** optimized for clarity and modularity.

```
                    ┌─────────────────────┐
                    │  Document Upload    │
                    │   (PDF/DOCX/JSON)   │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │  Document Parser    │
                    │  (PyMuPDF / DOCX)   │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │     Chunking        │
                    │  Tokenized Splits   │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │  Embedding Engine   │
                    │ sentence-transformer│
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │    Vector Store     │
                    │       FAISS         │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │   Semantic Search   │
                    │   Retrieve Chunks   │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ Deterministic Risk  │
                    │ & Context Clipping  │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │   LLM Analyzer      │
                    │ Compliance Review   │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │     LLM Judge       │
                    │ Result Validation   │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │  Compliance Report  │
                    │   Structured JSON   │
                    └─────────────────────┘
```

---

# Repository Structure

```
compliance-api/

app/
  main.py

  api/
    routes.py

  core/
    config.py
    logging.py

    llm/
      base.py
      openai_client.py
      ollama_client.py

  pipeline/
    parser.py
    chunker.py
    embeddings.py
    vector_store.py
    retrieval.py
    analyzer.py
    judge.py

  eval/
    evaluator.py

  models/
    request_models.py
    response_models.py

  storage/
    document_store.py

rules/
  eu_gdpr_rules.json
  us_compliance_rules.json
  uae_compliance_rules.json

policies/
  security_policies.json

architecture_docs/
expected_results/

analysisOutput/

tests/

Dockerfile
requirements.txt
README.md
```

---

# API Endpoints

## Start Compliance Analysis

```
POST /analyze
```

Uploads a document and starts the analysis process.

Example request:

```
curl -X POST http://localhost:8000/analyze \
  -F "file=@sample.pdf" \
  -F "country=EU"
```

Example response:

```
{
  "job_id": "f82a8d10-6d77-4a13-9d39-23e9c7",
  "status": "processing"
}
```

---

## Check Analysis Status

```
GET /status/{job_id}
```

Example response:

```
{
  "job_id": "f82a8d10-6d77-4a13-9d39-23e9c7",
  "status": "completed"
}
```

---

## Retrieve Compliance Report

```
GET /report/{job_id}
```

Example response:

```
{
  "document_id": "sample.pdf",
  "jurisdiction": "EU",
  "violations": [
    {
      "rule_id": "GDPR-13",
      "description": "User data sharing without disclosure",
      "severity": 8,
      "citation": {
        "page": 4,
        "text": "we may share personal information with partners"
      },
      "confidence": 0.87,
      "recommendation": "Add explicit disclosure of third-party data sharing."
    }
  ],
  "analysis_metadata": {
    "model_used": "llama3",
    "chunks_analyzed": 7
  }
}
```

---

# Configuration

Create a `.env` file:

```
MODEL_PROVIDER=ollama
MODEL_NAME=llama3

OPENAI_API_KEY=

OLLAMA_BASE_URL=http://localhost:11434

EMBEDDING_MODEL=all-MiniLM-L6-v2
VECTOR_STORE_PATH=./vector_store
```

Switching models requires **no code changes**.

---

# Running the Project Locally

### 1 Install dependencies

```
pip install -r requirements.txt
```

---

### 2 Start the API

```
uvicorn app.main:app --reload
```

Server will start at:

```
http://localhost:8000
```

---

### 3 Test API

Visit:

```
http://localhost:8000/docs
```

FastAPI automatically generates interactive API documentation.

---

# Docker Deployment

Build image:

```
docker build -t compliance-api .
```

Run container:

```
docker run -p 8000:8000 compliance-api
```

---

# Example Workflow

1. Upload compliance document
2. System parses document
3. Text is chunked and embedded
4. FAISS performs semantic search
5. Deterministic filtering identifies potential compliance risks & drops overlapping text beyond context limits
6. LLM evaluates rule violations
7. Judge model validates analysis
8. API returns structured compliance report

---

# Future Improvements

The architecture intentionally supports future extensions such as:

* clause extraction
* knowledge graph based compliance rules
* multi-agent workflows
* reranking models
* compliance dashboards
* distributed vector stores

---

# Why This Project Exists

Most GenAI demos show simple prompt engineering.

This project demonstrates **real backend architecture used in modern AI systems**, including:

* RAG pipelines
* LLM abstraction layers
* vector search
* structured outputs
* scalable API design

It serves as a **reference implementation for engineers building production-grade GenAI services**.
>>>>>>> dev
