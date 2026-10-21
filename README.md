# CertiPort – AI-Powered Telecom Certification Assistant

CertiPort is an AI-powered telecom certification assistant that helps engineers find and understand technical requirements from Telecom Engineering Centre (TEC) documents and MTCTE certification resources in India.

## Problem

Telecom test engineers spend considerable time searching through large technical documents to identify certification requirements. Traditional search systems may return lengthy documents without directly answering questions, while semantic search may miss exact identifiers such as `TEC 67010:2026`, `GR 91000:2022`, and `Clause 4.2.1`.

CertiPort aims to solve this problem using hybrid search and AI-powered question answering. It retrieves relevant technical clauses and generates answers supported by source citations, helping engineers verify information more efficiently.

## Who it is for

- Telecom test engineers preparing equipment for MTCTE certification.
- Compliance engineers at telecom equipment manufacturers in India.

## Signature feature

An AI assistant that answers telecom certification questions using technical documents, finds exact clauses, and provides citations so engineers can verify the answers.

## Hardest problem 

The main challenge is retrieving the correct technical clause when a question contains exact document numbers or clause identifiers. CertiPort plans to combine BM25 keyword search, vector-based semantic search, and reranking to improve retrieval accuracy. Answers will use retrieved evidence and citations to reduce unsupported AI responses. Performance will be evaluated using Recall@5 on 50 benchmark questions, with a target of 90% or higher.

## Dataset

| Source | Link | Documents | Pages | Licence / terms |
|---|---|---|---|---|
| Telecom Engineering Centre (TEC) | [TEC Website](https://www.tec.gov.in/) | To be collected | Target: 2,000+ | Subject to individual document terms |

Planned documents include:

- Essential Requirements (ERs)
- Generic Requirements (GRs)
- Technical test guides
- MTCTE certification procedures
- Official circulars

## 10 Real Questions

1. What are the battery test requirements in TEC 67010:2026 for VRLA batteries?
2. Which Essential Requirement applies to a Wi-Fi router?
3. What is the MTCTE process for a GPON ONT?
4. How can I find a TEC document by its document number?
5. How can I retrieve a specific clause?
6. Which technical requirements apply to a telecom product?
7. How can I verify the source of an AI-generated answer?
8. What information is required for a telecom equipment test plan?
9. How can the system distinguish similar clauses?
10. How can retrieval accuracy be measured?


## Run It

### Prerequisites

- Python 3.11 or a compatible version
- Visual Studio Code
- Git

### 1. Clone the repository

```bash
git clone https://github.com/nithyananthiniDA/Certiport.git
cd Certiport
```

### 2. Create and activate a virtual environment

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```powershell
pip install -r requirements-dev.txt
```

### 4. Configure environment variables

```powershell
copy .env.example .env
```

Add any required API credentials to `.env`. Never upload API keys to GitHub.

### 5. Run the application

```powershell
uvicorn app.main:app --reload
```

If implemented, access the API at [http://localhost:8000](http://localhost:8000) and interactive documentation at [http://localhost:8000/docs](http://localhost:8000/docs).

### 6. Run tests

```powershell
pytest
```

## Evaluation Metrics

The primary metric is Recall@5, which measures whether the correct supporting passage appears among the top five search results.

Target: 90% or higher on 50 benchmark questions containing document or clause identifiers.

## Expected Outcome

CertiPort aims to make telecom certification research faster by answering questions in natural language, retrieving exact clauses, and providing citations to official sources. It also aims to support test plan preparation with a human review and approval workflow.

## Disclaimer

CertiPort is an engineering support project. All technical requirements and proposed test plans must be verified against current official TEC documents and applicable regulations.

## Author

Nithyananthini D A

GitHub: [nithyananthiniDA](https://github.com/nithyananthiniDA)

Domain: Artificial Intelligence, Information Retrieval, and Telecommunications
