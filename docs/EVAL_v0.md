# CertiPort Evaluation Report — v0

## 1. Objective

Evaluate CertiPort's hybrid BM25 + vector retrieval, RRF ranking,
LLM-generated answers, and TEC document citations.

## 2. Evaluation Questions

| ID | Evaluation question | Expected evaluation |
|---|---|---|
| Q1 | What are the battery test requirements in TEC 67010:2026 for VRLA batteries? | Relevant battery clauses and citations |
| Q2 | Which Essential Requirement applies to a Wi-Fi router? | Correct Essential Requirement reference |
| Q3 | What is the MTCTE process for a GPON ONT? | Relevant MTCTE procedure and steps |
| Q4 | How can I find a TEC document by its document number? | Correct document retrieval |
| Q5 | How can I retrieve a specific clause? | Exact clause retrieval |
| Q6 | Which technical requirements apply to a telecom product? | Relevant technical requirements |
| Q7 | How can I verify the source of an AI-generated answer? | Document and page citations |
| Q8 | What information is required for a telecom equipment test plan? | Relevant test-plan requirements |
| Q9 | How can the system distinguish similar clauses? | Relevant clause ranking and distinction |
| Q10 | How can retrieval accuracy be measured? | Evaluation metrics and methodology |

## 3. Evaluation Metrics

- Retrieval relevance: Are the retrieved clauses relevant to the question?
- Citation correctness: Do document IDs, page numbers and clause numbers match the source?
- Answer accuracy: Is the generated answer supported by the retrieved TEC content?
- Response completeness: Does the answer address the question?

## 4. Scoring Method

Score each metric from 0 to 2:

- 0 = Incorrect or missing
- 1 = Partially correct
- 2 = Correct

Maximum score per question: 8

Maximum total score: 80

## 5. Evaluation Results

| ID | Retrieval relevance (0-2) | Citation correctness (0-2) | Answer accuracy (0-2) | Completeness (0-2) | Total (0-8) |
|---|---:|---:|---:|---:|---:|
| Q1 | Pending | Pending | Pending | Pending | Pending |
| Q2 | Pending | Pending | Pending | Pending | Pending |
| Q3 | Pending | Pending | Pending | Pending | Pending |
| Q4 | Pending | Pending | Pending | Pending | Pending |
| Q5 | Pending | Pending | Pending | Pending | Pending |
| Q6 | Pending | Pending | Pending | Pending | Pending |
| Q7 | Pending | Pending | Pending | Pending | Pending |
| Q8 | Pending | Pending | Pending | Pending | Pending |
| Q9 | Pending | Pending | Pending | Pending | Pending |
| Q10 | Pending | Pending | Pending | Pending | Pending |

## 6. Summary

- Total questions: 10
- Evaluated questions: 0
- Maximum score: 80
- Actual score: Pending
- Overall accuracy: Pending

## 7. Limitations

Scores must be assigned after checking actual API responses against the
original TEC documents. A generated answer or citation is not considered
correct without source verification.

## 8. Next Improvements

- Expand the dataset to at least 500 pages.
- Improve clause-level retrieval and ranking.
- Verify citations against original PDF pages.
- Compare BM25-only and hybrid retrieval.
- Repeat evaluation after each retrieval improvement.

