# RAG Server

## Overview

This project implements a Retrieval-Augmented Generation (RAG) backend using:

- FastAPI
- Celery
- Redis
- Postgres
- Ollama
- LangChain
- Doclingr
- FAISS Vector Store
- NGINX (Docker)

The backend accepts uploaded documents, extracts text, optionally translates non-English content, generates embeddings, stores them in a vector database, and allows semantic querying.

---

# Project Configuration

The project uses Python configuration files instead of scattered constants.

```
config/
├── __init__.py
├── paths.py
└── settings.py
```

## paths.py

Contains all filesystem locations used throughout the application.

Example:

- uploads/
- uploads/originals/
- uploads/translated/
- vector_store/
- documents/

Any required directories are automatically created when the application starts.

Example usage:

```python
from config.paths import ORIGINAL_UPLOAD_DIR
```

instead of

```python
Path("uploads")
```

---

## settings.py

Contains configurable application settings.

Example:

```python
EMBED_MODEL = "mxbai-embed-large"

CHUNK_SIZE = 300
CHUNK_OVERLAP = 80

OLLAMA_BASE_URL = "http://host.docker.internal:11434"
```

Instead of using

```python
os.getenv(...)
```

all services import configuration directly:

```python
from config.settings import (
    EMBED_MODEL,
    CHUNK_SIZE,
    CHUNK_OVERLAP,
    OLLAMA_BASE_URL,
)
```

---

# Install Ollama

Install Ollama

```bash
curl -fsSL https://ollama.com/install.sh | sh
```

Pull embedding model

```bash
ollama pull mxbai-embed-large
```

Start Ollama

```bash
ollama serve
```

---

# Install Redis

Redis is required for

- Celery
- Background task queue
- Workflow orchestration

Install

```bash
sudo apt update
sudo apt install redis-server
```

Start Redis

```bash
sudo service redis-server start
```

Postgres Tables

CREATE TABLE documents (
    id SERIAL PRIMARY KEY,
    workflow_id UUID NOT NULL UNIQUE,
    original_filename VARCHAR(255) NOT NULL,
    stored_filename VARCHAR(255) NOT NULL,
    original_language VARCHAR(30),
    translated BOOLEAN NOT NULL DEFAULT FALSE,
    file_extension VARCHAR(20),
	mime_type VARCHAR(100),
	file_size BIGINT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
---

# Running without Docker

## Terminal 1

Start Celery Worker

```bash
cd rag-server

celery -A orchestration.celery_tasks:celery_app worker --loglevel=info
```

---

## Terminal 2

Start FastAPI

```bash
cd rag-server

uvicorn main:app --reload
```

Server

```
http://127.0.0.1:8000
```

Swagger

```
http://127.0.0.1:8000/docs
```

---

# Running with Docker

Start

```bash
docker compose up --build
```

Stop

```bash
docker compose down
```

Verify

```
http://localhost:8080/
```

Expected response

```json
{
    "message": "RAG Server Running"
}
```

Swagger

```
http://localhost:8080/docs
```

---

# API Examples

Upload document

```bash
curl -X POST "http://127.0.0.1:8000/upload" \
-F "file=@sample.pdf"
```

Query

```bash
curl -X POST "http://127.0.0.1:8000/query" \
-H "Content-Type: application/json" \
-d '{
  "question": "What is the project deadline?",
  "top_k": 5
}'
```

---

# Overall Architecture

```
                    Client
                       │
                       ▼
               FastAPI Upload API
                       │
                       ▼
           Save Original File
                       │
                       ▼
         Workflow Manager creates Workflow
                       │
                       ▼
             Celery Background Queue
                       │
                       ▼
            Document Extraction
                       │
                       ▼
          Language Detection
                       │
         ┌─────────────┴─────────────┐
         │                           │
         ▼                           ▼
     English                    Japanese
         │                           │
     Translate to Jap        Translate to English
         │                           │
         └─────────────┬─────────────┘
                       ▼
             Save Translated Text
                       ▼
                 Chunk Document
                       ▼
             Generate Embeddings
                       ▼
            Store in FAISS Database
                       ▼
             Workflow Completed
                       ▼
         WebSocket Status Updates
```

---

# Upload Request Execution Flow

When the client calls

```
POST /upload
```

the following sequence occurs.

## Step 1

The uploaded file is received by

```
api/routes/upload_routes.py
```

---

## Step 2

A unique Job ID is generated.

Example

```
9fd91dbe-b5d6-4a1d...
```

---

## Step 3

The uploaded file is saved into

```
uploads/originals/
```

using the generated Job ID.

Example

```
uploads/originals/9fd91dbe.pdf
```

---

## Step 4

The API computes the file hash.

This is stored as document metadata.

---

## Step 5

The upload route calls

```
start_ingestion_workflow(...)
```

The Workflow Manager

- creates a Workflow ID
- initializes workflow status
- determines the pipeline
- dispatches processing to Celery

---

## Step 6

The API immediately returns

```json
{
    "status": "accepted",
    "workflow_id": "...",
    "pipeline": "ingest_document"
}
```

The client does **not** wait for document processing to finish.

---

# Background Processing

The Celery worker now processes the workflow asynchronously.

## Extract Document

The extraction service reads the uploaded file and converts it into plain text.

Supported formats include PDF, DOCX, TXT, and other formats supported by Docling.

---

## Language Detection

The extracted text is analyzed to determine its language.

If the document is already English, processing continues normally.

If the document is Japanese, it is translated into English using the configured LLM.

The translated text is stored under

```
uploads/translated/
```

using the same workflow or document identifier.

---

## Chunking

The English text is divided into smaller overlapping chunks using

```
RecursiveCharacterTextSplitter
```

Configuration comes from

```
config/settings.py
```

```
CHUNK_SIZE
CHUNK_OVERLAP
```

---

## Embedding Generation

Each chunk is sent to Ollama using

```
mxbai-embed-large
```

to generate vector embeddings.

---

## Vector Storage

Generated embeddings, chunk text, and metadata are stored inside the FAISS vector database.

Typical metadata includes

- source filename
- page number
- file hash
- workflow ID
- language information (if applicable)

---

## Workflow Completion

Once all stages succeed

- workflow status becomes COMPLETED
- completion events are published
- connected WebSocket clients receive the final status update

---

# Query Flow

When the client sends

```
POST /query
```

the following occurs:

1. Generate an embedding for the user's question.
2. Perform a similarity search in the FAISS vector store.
3. Retrieve the top matching document chunks.
4. Use the retrieved context to answer the question.
5. Return the generated response to the client.

---

# WebSocket Notifications

The frontend subscribes using the Workflow ID returned by `/upload`.

During processing, the backend emits events such as:

- PIPELINE_STARTED
- STAGE_UPDATE
- PIPELINE_COMPLETED
- PIPELINE_FAILED

These events allow the frontend to display real-time progress without polling the server.

# looking into Log file (lateset 100 lines)
docker compose logs --tail=100 -f worker