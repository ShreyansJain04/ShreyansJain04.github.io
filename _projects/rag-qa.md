---
layout: page
title: "Retrieval-Augmented QA: Encoder-Decoder vs Decoder-Only"
description: "Open-domain QA testbed comparing T5 and causal LLMs with BM25, FAISS and hybrid retrieval, LoRA/QLoRA fine-tuning, on SQuAD, TriviaQA and Natural Questions."
importance: 5
category: "ML & Data Projects"
period: "Nov 2025"
links:
  code: https://github.com/ShreyansJain04/RumikRag
tags: [RAG, LLM, retrieval, LoRA, QA]
---

<div class="tldr" markdown="1">
**Question.** In retrieval-augmented question answering, how much does the generator's architecture matter compared with the retriever?  
**Approach.** One modular pipeline that swaps retrievers (BM25, FAISS dense, hybrid, optional cross-encoder reranking) and generators (Flan-T5 with LoRA, decoder-only LLMs with QLoRA), and evaluates each pair against a no-retrieval baseline.  
**Status.** Pipeline and evaluation complete on SQuAD v1.1; the first runs are preliminary.
</div>

## Overview

Most production RAG systems use decoder-only chat models, while much of the earlier RAG research used encoder-decoder models like T5. This project builds one testbed for comparing the two fairly, with the same retrievers, the same passages and the same metrics.

## Pipeline

- **Corpus and data.** Loaders for SQuAD v1.1, TriviaQA and Natural Questions, which build a passage corpus from each.
- **Retrieval.** BM25 for lexical matching, FAISS for dense similarity, a hybrid that fuses both, and an optional cross-encoder reranker.
- **Generation.** Flan-T5 fine-tuned with LoRA, and decoder-only LLMs fine-tuned with QLoRA using a chat template that puts the retrieved passages in context.
- **Evaluation.** Exact match and token-level F1 for answers, Recall@k for retrieval, and latency per query, each compared with a no-retrieval baseline.

## What the first runs show

On the SQuAD dev set with 20 retrieved passages, dense FAISS retrieval finds the gold passage more often than the hybrid (24% vs 19% Recall@20), and that carries through to answer quality. One epoch of fine-tuning roughly doubled exact match for the hybrid setup (1.8% to 4.0%). Absolute scores are still low, so these runs are a baseline for the full comparison rather than a final result.
