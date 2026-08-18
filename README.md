# Document Question Answering System (RAG)

A Django-based Retrieval-Augmented Generation (RAG) application for uploading and managing `.docx` documents, retrieving relevant document content, generating grounded answers with an LLM, and storing question/answer history.

## Features

- Add, edit, and delete documents through Django Admin
- `.docx` document support
- Automatic full-text extraction using `python-docx`
- Text chunking with LangChain `RecursiveCharacterTextSplitter`
- Multilingual sentence embeddings with Sentence Transformers
- Vector storage and semantic retrieval using Chroma
- LLM answer generation through OpenRouter
- REST API for documents, question answering, and QA history
- Ask questions directly from Django Admin
- Store generated answers together with their source document(s)
- Persistent SQLite data and persistent Chroma vector storage in Docker
- Automatic vector re-indexing when a document file is replaced
- Automatic vector cleanup when a document is deleted

## Tech Stack

- Python 3.13
- Django 6.1
- Django REST Framework
- LangChain
- Chroma
- Sentence Transformers
- `paraphrase-multilingual-MiniLM-L12-v2` embedding model
- OpenRouter for LLM access
- Docker / Docker Compose
- SQLite

## Architecture

```text
DOCX Upload
    |
    v
Django Document Model
    |
    v
python-docx text extraction
    |
    v
LangChain RecursiveCharacterTextSplitter
    |
    v
Sentence Transformer Embeddings
    |
    v
Chroma Vector Database

User Question
    |
    v
Query Normalization
    |
    v
Semantic Retrieval from Chroma
    |
    v
Top relevant chunks
    |
    v
Prompt + Retrieved Context
    |
    v
OpenRouter LLM
    |
    v
Grounded Answer
    |
    v
QAHistory + Source Documents
```

## Project Structure

A typical project layout is:

```text
project-root/
├── manage.py
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── .env.example
├── README.md
├── API_DOCUMENTATION.md
├── db.sqlite3                 # generated locally; optional in submission
├── project/
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── documents/
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── serializers.py
│   ├── signals.py
│   ├── utils.py
│   ├── views.py
│   └── migrations/
├── sample_data/
└── screenshots/
```

## Prerequisites

Install:

- Docker Desktop
- Docker Compose

An OpenRouter API key is also required.

## Environment Configuration

Create a `.env` file in the project root:

```env
OPENROUTER_API_KEY=your_openrouter_api_key_here
```

Do not commit or submit your real `.env` file. Submit `.env.example` instead.

## Run the Project

### 1. Build and start the containers

```bash
docker compose up --build
```

The first build may take longer because the embedding dependencies include Sentence Transformers and PyTorch.

After the first successful build, the project can usually be started with:

```bash
docker compose up
```

### 2. Apply Django migrations

In another terminal:

```bash
docker compose exec web python manage.py migrate
```

### 3. Create an admin user

```bash
docker compose exec web python manage.py createsuperuser
```

### 4. Open the application

Django Admin:

```text
http://localhost:8000/admin/
```

REST API:

```text
http://localhost:8000/api/
```

Chroma is exposed on the host at port `8001`, while Django connects to it internally using the Docker service name `chroma` on port `8000`.

## Using the Application

### Upload a document

1. Open Django Admin.
2. Go to `Documents`.
3. Add a new document.
4. Upload a `.docx` file.
5. Save it.

The application automatically:

1. extracts the document text,
2. stores the full extracted text in SQLite,
3. chunks the text with LangChain,
4. creates embeddings,
5. stores the chunks and metadata in Chroma.

### Ask a question from Django Admin

1. Open `QA histories`.
2. Select `Add QA history`.
3. Enter a question.
4. Save the form.

The system retrieves relevant chunks, generates an answer through OpenRouter, saves the answer, and records the source document(s).

### Ask a question through the API

Send a `POST` request to:

```text
/api/ask/
```

Example request body:

```json
{
  "question": "نام علمی گربه چیست؟"
}
```

Example response:

```json
{
  "question": "نام علمی گربه چیست؟",
  "answer": "Felis catus",
  "sources": [
    {
      "document_id": 3
    }
  ]
}
```

See `API_DOCUMENTATION.md` for complete API documentation.

## Document Update and Delete Behavior

When the uploaded file of an existing document is replaced:

- old Chroma vectors are deleted,
- the new text is extracted,
- new chunks and embeddings are generated,
- Chroma is re-indexed for that document.

When a document record is deleted:

- its Django database record is removed,
- its corresponding Chroma vectors are also removed.

This prevents stale content from being retrieved after a document is changed or deleted.

## Persistence

- Django uses SQLite (`db.sqlite3`) for relational application data.
- Chroma uses the Docker named volume `chroma_data`.

Therefore normal container restarts do not remove the stored application data or vector collection.

## Retrieval Tests

The project was tested with intentionally similar documents to verify retrieval quality, including:

- different HR policy versions containing conflicting values,
- travel policy data,
- security policy negations,
- a product FAQ containing terminology similar to HR documents,
- multi-document questions requiring information from two different sources,
- questions whose answers do not exist in the uploaded documents.

These tests are included in the `sample_data/` directory.

## Current Retrieval Strategy

The current retrieval pipeline uses semantic vector search with Chroma and Sentence Transformer embeddings. Query normalization is applied before retrieval to reduce differences caused by Unicode variants and whitespace.

The number of retrieved chunks is currently configured to support questions that may require context from multiple documents.

## Design Decisions

### Why Django Admin?

The project specification does not require a separate frontend. Django Admin provides a simple, maintainable interface for document management, QA history, and direct question submission without unnecessary frontend complexity.

### Why Chroma?

Chroma provides a lightweight vector database with persistent storage and integrates directly with LangChain. Running it as a separate Docker service also keeps the vector layer independent from Django's relational database.

### Why Sentence Transformers?

The selected multilingual embedding model supports both Persian and English content and is suitable for local embedding generation without requiring a paid embedding API.

### Why LangChain?

LangChain is used for chunking, embedding integration, Chroma vector store access, retrieval, and LLM communication, as required by the project specification.

## Known Limitations

- Retrieval currently uses semantic search only.
- Uploaded physical media files are not automatically removed from disk when a Django document record is deleted.
- The current project is intended as a development/assessment implementation rather than a production deployment.
- API authentication, production security configuration, monitoring, and advanced observability are outside the current scope.

## Further Improvements

The next improvements I would prioritize are:

1. **Hybrid retrieval (Semantic Search + BM25)** to improve exact keyword/entity retrieval while keeping semantic matching.
2. **Reranking** of retrieved candidates before sending context to the LLM.
3. **Retrieval score thresholds** to avoid answering from weak or unrelated context.
4. More detailed source metadata, including document title and chunk index in API responses.
5. Automatic cleanup of orphaned uploaded `.docx` files.
6. Better exception handling for unavailable Chroma/OpenRouter services.
7. Automated unit and end-to-end tests.
8. API authentication and production deployment configuration.

## API Endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/api/documents/` | List documents |
| POST | `/api/documents/` | Upload a document |
| POST | `/api/ask/` | Ask a question using the RAG pipeline |
| GET | `/api/history/` | List saved question/answer history |

## Suggested Evaluation Flow

For a quick demo:

1. Run the Docker services.
2. Open Django Admin.
3. Upload one or more `.docx` sample files.
4. Show the extracted text stored in the Document record.
5. Ask a question from the Admin panel.
6. Show the generated answer and source document.
7. Open `/api/history/` to show stored history.
8. Replace or delete a document and explain how Chroma is synchronized.

## Submission Notes

For a clean assessment submission, include the source code, migrations, Docker files, README, API documentation, screenshots, sample data, and `.env.example`. Do not include your real `.env`, virtual environment, Python cache folders, Git metadata, or downloaded model caches.

## Notes

This project prioritizes simplicity, readability, and maintainability over unnecessary architectural complexity, while keeping the core RAG components modular enough for future retrieval and evaluation improvements.
