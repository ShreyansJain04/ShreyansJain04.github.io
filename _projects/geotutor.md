---
layout: page
title: "GeoTutor: An AI Tutoring System for GIS Education with Hybrid RAG"
description: "Adaptive GIS tutor: BM25 + dense retrieval + cross-encoder reranking, citations on every answer, SM-2 spaced repetition."
img: assets/img/projects/geotutor/thumb.jpg
importance: "6"
category: "Research"
period: "May 2025 – Jul 2025"
advisor: "Prof. Dharmendra Saraswat & Prof. Vaneet Aggarwal, Purdue University"
status: "Research internship · Purdue"
links:
  code: https://github.com/ShreyansJain04/GISLLM
tags: [LLM, RAG, education, GIS, tutoring-system, FastAPI]
highlights:
  - "Intelligent tutoring system for GIS education on a hybrid RAG pipeline: BM25 + dense FAISS retrieval + cross-encoder reranking, with citations on every answer."
  - "Adaptive teaching engine with a learner-memory model: personalized plans, misconception detection, SuperMemo-2 spaced repetition."
  - "FastAPI + Pydantic backend integrated with a React frontend; journal manuscript in preparation with Purdue faculty."
---
<!-- TODO: verify (1) the manuscript is an unfinished draft (author/abstract placeholders, target journal "Computers and Education: Artificial Intelligence" only in the template header); no submission status stated, so no venue is claimed here. (2) No evaluation numbers exist in the draft. (3) Team/period unknown. -->

<div class="tldr" markdown="1">
**Problem.** LLMs hallucinate, which is especially costly when teaching GIS, where map projections and software workflows must be exactly right. Existing GIS assistants answer questions but do not teach.  
**Approach.** A full-stack tutoring system that grounds every explanation in a curated GIS knowledge base through a hybrid RAG pipeline, and personalizes instruction with a planner agent and a learner-memory system.  
**Result.** A working system (FastAPI backend, React frontend) with auditable, citation-backed answers, adaptive learning paths and spaced-repetition review. The draft paper is a system description; it reports no benchmark numbers yet.
</div>

## Overview

GeoTutor starts from a simple observation: the open problem is not an AI that knows GIS, but one that knows how to teach it. Its design constraints are explicit: every output must be supported by retrieved context; learning-path decisions must be derivable from logged learner state; review scheduling must follow a known algorithm (SM-2); and the system must refuse to answer when the retrieved context is insufficient.

## Method

{% include figure.html path="assets/img/projects/geotutor/system_architecture.png" class="img-fluid rounded z-depth-1" zoomable=true caption="GeoTutor system architecture: the Domain Expert (RAG core), Planner Agent and Memory System behind a FastAPI orchestration layer." %}

**Knowledge base.** A scraped snapshot of the ESRI ArcGIS Pro documentation (as structured Markdown, organized by toolbox), plus open-access GIS textbooks and library material on spatial analysis, cartography, coordinate reference systems and GIS programming. It can be refreshed by re-scraping and re-indexing.

**Domain Expert (hybrid RAG).**
- Sentence-aware chunking with a soft 512-character limit and a 3-sentence rolling overlap.
- Sparse retrieval with Okapi BM25 and dense retrieval with all-MiniLM-L6-v2 embeddings in FAISS, run in parallel and fused by $$\text{score} = \alpha\, S_{\text{dense}} + (1-\alpha)\, S_{\text{sparse}}$$ with $$\alpha = 0.7$$.
- A cross-encoder (ms-marco-MiniLM-L-6-v2) reranks 10 candidates down to the top 5 passed to the LLM.
- Retrieval diagnostics are logged for later analysis.

**Planner Agent and memory.** The planner turns a topic into a JSON learning plan with prerequisites and difficulty. The memory system persists per-user profiles, analyses error types, study-time patterns and hedging language as a confusion signal, and ranks weak areas by overdue reviews, error density and confusion frequency. Flashcards use SuperMemo-2 with the ease factor clamped to 1.3-3.0 and a 10-minute cool-down after failures.

**Modes.** Dashboard, Chat, Learn, Review, Test (no scaffolding) and Sources (shows exactly which documents are indexed). Learn mode runs an explain, example, question, score, reflect loop with mastery thresholds (at least 0.8 mastered; below 0.6 weak area). The repository also supports multiple LLM providers (OpenAI, DeepSeek, Ollama, Anthropic, Google).

## Results

The draft is a system paper: no quantitative evaluation is reported yet. The project's value so far is the design, a reproducible implementation, and an auditable pipeline where each answer can be traced to retrieved sources and logged learner state.

## My role

- Designed and implemented GeoTutor end to end: the hybrid RAG pipeline (BM25 + dense retrieval + cross-encoder reranking), prompt engineering for context-aware responses, and the adaptive tutoring components.
- Source: CV description; code at [GISLLM](https://github.com/ShreyansJain04/GISLLM).
