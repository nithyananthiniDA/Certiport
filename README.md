# CertiPort – AI-Powered Telecom Certification Assistant

**An intelligent document retrieval and question-answering system for telecom certification requirements.**

## About the Project

CertiPort is an AI-powered assistant designed to help telecom test and compliance engineers retrieve technical requirements from Telecom Engineering Centre (TEC) standards and MTCTE documents.

Instead of manually searching hundreds of pages, users can ask questions and retrieve relevant technical clauses with document, page, and clause references.

## Key Features

- Extracts text and technical clauses from TEC PDF documents.
- Supports page-level and clause-level search.
- Uses BM25 for relevance-based information retrieval.
- Supports exact clause-number lookup.
- Generates context-grounded answers using the OpenAI API.
- Provides source citations for verification.
- Provides TEC document-based fallback answers when AI generation is unavailable.

## Technology Stack

- **Language:** Python
- **Backend:** FastAPI
- **Information Retrieval:** BM25, rank-bm25
- **PDF Processing:** PyMuPDF
- **AI Integration:** OpenAI API
- **Data Storage:** JSON
- **Testing:** Pytest
- **Version Control:** Git and GitHub

## Dataset

Currently processed:

- 4 TEC/MTCTE documents
- 304 document pages
- 636 extracted clauses

## System Architecture

```text
User Question
     |
     v
FastAPI Backend
     |
     v
BM25 Search Engine
     |
     v
Relevant TEC Clauses
     |
     v
OpenAI Answer Generation
     |
     v
Answer + Source Citations
```

## API Endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/health` | Application health |
| GET | `/search` | Search document pages |
| GET | `/clauses/search` | Search technical clauses |
| GET | `/ask` | Ask questions using TEC documents |

API documentation: `http://127.0.0.1:8000/docs`

## Installation

```bash
git clone https://github.com/nithyananthiniDA/Certiport.git
cd Certiport
python -m venv .venv
```

Activate the environment:

```powershell
.\.venv\Scripts\Activate.ps1
```

Install dependencies:

```bash
pip install -e .
```

Configure your OpenAI API key in a local `.env` file:

```env
OPENAI_API_KEY=your_api_key
```

Run the application:

```bash
python -m uvicorn app.main:app --reload
```

## Testing

Run automated tests:

```bash
python -m pytest -v
```

**Latest verified result: 12 tests passed.**

## Future Enhancements

- Hybrid BM25 and vector search.
- Semantic document retrieval.
- Cross-encoder reranking.
- Expansion to 2,000+ pages.
- Automated telecom compliance test-plan generation with human approval.

## Project Disclaimer

CertiPort is an engineering support tool. All technical requirements must be verified against the latest official TEC documents.

## Author

**Nithyananthini D A**

Electronics and Communication Engineering

GitHub: [nithyananthiniDA](https://github.com/nithyananthiniDA)

**Project Repository:** [CertiPort](https://github.com/nithyananthiniDA/Certiport)