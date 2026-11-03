# CertiPort – System Design

## 1. Project Overview

CertiPort is an AI-powered telecom certification assistant that helps users search and understand Telecom Engineering Centre (TEC) documents.

The system uses FastAPI for API development, BM25 for document retrieval, and OpenAI for AI-generated answers.

## 2. Technology Stack

| Component | Technology |
|---|---|
| Programming Language | Python |
| Backend Framework | FastAPI |
| Search Algorithm | BM25 |
| Data Storage | JSON files |
| AI Integration | OpenAI API |
| Data Processing | PyMuPDF |
| Testing | Pytest |
| Code Quality | Ruff |
| Containerization | Docker |
| CI/CD | GitHub Actions |

## 3. System Architecture

1. TEC PDF documents are processed into structured JSON files.
2. Page-level data is stored in individual JSON files.
3. Clause-level data is stored in `clauses.json`.
4. The search engine loads JSON data and tokenizes the content.
5. BM25 retrieves relevant pages or clauses.
6. The `/ask` endpoint sends retrieved context to the OpenAI API.
7. If AI generation fails, the application returns the retrieved TEC document content as a fallback.
8. Results include document and clause citations.

## 4. API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/health` | Checks application health and environment |
| GET | `/usage` | Returns accumulated token usage and estimated cost |
| GET | `/search` | Searches TEC documents at page level |
| GET | `/clauses/search` | Searches individual TEC clauses |
| GET | `/ask` | Answers questions using retrieved TEC clauses |

### API Parameters

**`/search` and `/clauses/search`**

- `q`: Search query (required)
- `limit`: Number of results (default 10, maximum 50)
- `document_id`: Optional document filter

**`/ask`**

- `q`: Certification question (required)
- `limit`: Number of clauses (default 5, maximum 10)
- `document_id`: Optional document filter

## 5. Data Structure

CertiPort currently uses JSON-based storage. It does not currently use a relational database.

### Page-level document data

Stored in JSON files inside `data/processed/`.

| Field | Description |
|---|---|
| document_id | TEC document identifier |
| page_number | Page number |
| text | Extracted page content |

### Clause-level document data

Stored in `data/processed/clauses.json`.

| Field | Description |
|---|---|
| document_id | TEC document identifier |
| page_number | Page number |
| clause_number | TEC clause number |
| clause_title | Clause heading |
| text | Extracted clause content |

## 6. Search and Retrieval

CertiPort uses BM25 (Best Matching 25) for information retrieval.

The search process:

1. Convert text into lowercase tokens.
2. Extract searchable words and clause numbers.
3. Compare query tokens with document tokens.
4. Calculate BM25 relevance scores.
5. Sort results by score.
6. Return the most relevant pages or clauses.

The system also supports exact clause-number lookup.

## 7. AI Answer Generation and Fallback

The `/ask` endpoint retrieves relevant TEC clauses before generating an answer.

- Primary answer generation: OpenAI API.
- Current fallback: Retrieved TEC document text.
- Citations: Document ID, page number, clause number and clause title.

A separate fallback AI model is not yet implemented.

## 8. Usage Monitoring

The `/usage` endpoint provides:

- Number of successful LLM requests recorded.
- Input tokens.
- Output tokens.
- Total tokens.
- Estimated API cost.
- Model name.

Usage is currently maintained in application memory and resets when the application restarts.

## 9. Error Handling

- HTTP 400: Empty search query or question.
- HTTP 503: TEC document data unavailable.
- HTTP 500: Document data loading error.
- AI API failure: Returns retrieved TEC document content as fallback.

## 10. Deployment

The application is containerized using Docker.

- Docker base image: `python:3.12-slim`
- Application server: Uvicorn
- Container port: 8000
- Local Docker test port: 8002
- Health endpoint: `/health`
- Cloud hosting: Render
- Deployment URL: https://certiport-api.onrender.com

GitHub Actions automates Ruff code-quality checks and Pytest execution on pushes and pull requests.

The Docker deployment uses synthetic demonstration data. Private TEC documents remain separate from the public demo deployment.

## 11. Future Enhancements

- Implement a secondary AI fallback model.
- Integrate PostgreSQL with pgvector.
- Add document embeddings and semantic search.
- Improve retrieval using a re-ranking model.
- Improve evaluation using real telecom certification questions.
- Add persistent usage tracking.
- Expand automated testing and monitoring.

## 12. Conclusion

CertiPort provides a document-based telecom certification search and question-answering system. Its modular architecture supports future improvements in AI, retrieval, storage and deployment.