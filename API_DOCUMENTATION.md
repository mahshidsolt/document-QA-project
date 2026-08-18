# API Documentation

Base URL:

```text
http://localhost:8000
```

## 1. Documents API

### List documents

**GET** `/api/documents/`

Returns all stored Django Document records.

Example response:

```json
[
  {
    "id": 1,
    "title": "HR Policy 1404",
    "file": "http://localhost:8000/media/documents/hr_policy_1404.docx",
    "extracted_text": "...",
    "uploaded_at": "2026-08-18T12:00:00Z"
  }
]
```

### Upload a document

**POST** `/api/documents/`

Content type: `multipart/form-data`

Fields:

- `title`: document title
- `file`: `.docx` file

After upload, text extraction, chunking, embedding, and Chroma indexing are performed automatically.

---

## 2. Ask API

### Ask a question

**POST** `/api/ask/`

Content type: `application/json`

Request:

```json
{
  "question": "مرخصی سال ۱۴۰۴ چند روز است؟"
}
```

Response:

```json
{
  "question": "مرخصی سال ۱۴۰۴ چند روز است؟",
  "answer": "۲۶ روز",
  "sources": [
    {
      "document_id": 2
    }
  ]
}
```

The endpoint performs:

1. query normalization,
2. semantic retrieval from Chroma,
3. prompt construction using retrieved chunks,
4. LLM generation through OpenRouter,
5. QA history persistence,
6. source-document association.

---

## 3. QA History API

### List question/answer history

**GET** `/api/history/`

Example response:

```json
[
  {
    "id": 4,
    "question": "مرخصی سال ۱۴۰۴ چند روز است؟",
    "answer": "۲۶ روز",
    "created_at": "2026-08-18T12:15:00Z"
  }
]
```

Records are returned newest first.

---

## Django Admin UI

The project also supports the same workflow from Django Admin:

```text
http://localhost:8000/admin/
```

From Admin, evaluators can:

- create/edit/delete Documents,
- inspect extracted document text,
- create a new QAHistory entry by entering a question,
- receive an automatically generated RAG answer,
- view the source document(s),
- inspect stored question/answer history.

## Error / Limitation Notes

The current implementation is an assessment/development version. Production-grade authentication, advanced service error responses, retrieval confidence thresholds, and rate limiting are future improvements.
