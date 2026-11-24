---
layout: page
title: "FinDocs: Financial Document Ingestion, Sentiment and Hybrid RAG"
description: "Pipeline that parses financial filings, scores FinBERT sentiment per chunk and answers queries with hybrid dense+BM25 retrieval and reranking."
img: assets/img/projects/findocs/thumb.jpg
importance: 1
category: "ML & Data Projects"
links:
  code: https://github.com/ShreyansJain04/FinDocs
tags: [RAG, NLP, FinBERT, FAISS, retrieval]
---

<div class="tldr" markdown="1">
**Problem.** Earnings calls, filings and reports are long, table-heavy PDFs. Analysts need numbers they can trust and answers they can trace back to a source chunk.  
**Approach.** A modular ingestion and retrieval pipeline: multi-format parsing with high-fidelity table extraction, structure-aware chunking, per-chunk FinBERT sentiment, and a hybrid retriever (E5 dense + BM25 sparse) with cross-encoder reranking.  
**Result.** An auditable, idempotent system that runs on a single T4/L4 GPU, with a CLI, a Streamlit UI and a design in which every ranking decision can be traced.
</div>

## Overview

FinDocs turns a folder of financial documents (PDF, DOCX, PPTX, HTML, TXT, MD) into a searchable, sentiment-annotated index. The guiding idea is that in finance, quality and auditability matter more than raw speed: an analyst or auditor should be able to ask why a chunk ranked where it did and get an answer from BM25 scores, embedding distances, reranker logits and sentiment probabilities.

## Method

The pipeline has six stages, each its own module in `src/fdocs/`:

1. **Parsing and tables.** `pymupdf` and `pdfplumber` are preferred over a generic parser because pdfplumber exposes cell boundaries and row/column structure, which matters for balance sheets and multi-page tables.
2. **Chunking.** Structure-aware chunks of about 300 tokens with 60-token overlap, which leaves headroom under the 512-token limit shared by FinBERT and E5.
3. **Sentiment.** `yiyanghkust/finbert-tone` gives a label and calibrated probabilities per chunk, so downstream code can threshold on confidence rather than only on a label.
4. **Embeddings and dense index.** E5-large-v2 vectors, L2-normalised and stored in a FAISS `IndexFlatIP`, which makes inner product equal to cosine similarity with exact search.
5. **Sparse index.** BM25 catches tickers, acronyms (EPS, EBITDA) and rare terms that embeddings blur.
6. **Fusion and reranking.** Dense and sparse lists are merged with reciprocal rank fusion, then a MiniLM cross-encoder reranks the candidates.

Bookkeeping follows the same audit mindset. Each document is registered by SHA-256 content hash, so re-running ingestion is idempotent and any one-byte change triggers reprocessing. Chunk and table metadata live in Parquet for SQL-style filtering by company, date or sentiment.

Typical usage is `python -m src.fdocs.cli ingest --company AcmeCo` followed by `query ... --mode hybrid --rerank`. Models, chunk sizes and fusion weights are set in `config/default.yaml`, so swapping the embedder (for example to BGE) is a config change plus an index rebuild.

## Results

The repository documents the following operating characteristics on an L4 GPU (README estimates, not a formal benchmark):

| Stage | Approx. throughput |
|---|---|
| PDF parsing | 2-5 pages/s |
| FinBERT sentiment | 50-100 chunks/s |
| E5 embeddings | 100-200 chunks/s |
| Reranking | 500-1000 pairs/s |

Flat exact search works up to roughly 10M chunks, after which the design points to IVF or HNSW. Beyond the README, the source tree also includes active-learning, feedback, fine-tuning, an LLM server stub and a UI module, along with tests for chunk boundaries, sentiment label mapping, table round-trips and RRF fusion.

## My role

- Designed the pipeline and the rationale for each component choice (documented in the repo README and `DESIGN.md`).
- Implemented parsing, chunking, sentiment, indexing, hybrid retrieval and the CLI.
- Planned extensions such as sentiment-versus-price studies, event detection and multi-document reasoning.
