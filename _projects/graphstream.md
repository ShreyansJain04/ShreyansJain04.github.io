---
layout: page
title: "GraphStream: Sub-Linear Streaming Graph Analytics"
description: "Single-pass, memory-bounded engine running 16 streaming algorithms over million-edge graphs; under 0.6% triangle-count error and under 700 MB peak RAM."
img: assets/img/projects/graphstream/thumb.jpg
importance: 4
category: "ML & Data Projects"
period: "Data Science course project · Apr 2026"
team: "Umang Shikarvar, Romit Mohane, Soham Gaonkar, Shreyans Jain"
links:
  code: https://github.com/Soham-Gaonkar/GraphStreamingLibrary
tags: [streaming algorithms, sketching, graph analytics, sampling]
---

<div class="tldr" markdown="1">
**Problem.** Analyse massive, changing networks (degree statistics, triangles, connectivity, communities) when the full graph is too big to keep in memory.  
**Approach.** A semi-streaming engine that reads each edge once, updates 16 sketching, sampling and sparsification algorithms, and throws the edge away. Memory is capped by design rather than growing with the graph.  
**Result.** Under **0.6% error** on triangle counts and under **700 MB** peak RAM on real SNAP graphs with over a million edges, at up to about **15,000 edges per second**.
</div>

## Overview

GraphStream treats a graph as a stream of edges `(u, v, weight, timestamp)`. Each edge passes through a fixed pipeline once and is then discarded, so the engine never stores the full topology. Built as a four-person team project for a data science course.

## How it works

Every incoming edge updates, in order:

1. **Sketches** for node degrees (Count-Min with conservative update, Count Sketch), plus top-k and Misra-Gries heavy-hitter trackers.
2. **A triangle estimator** that uses the current edge sample before the sampler updates.
3. **Graph Priority Sampling (GPS)**, which keeps a bounded weighted reservoir of edges as a stand-in for the full graph.
4. **Sparsifiers and a spanner** (uniform and spectral sparsification, a greedy spanner) that keep a small graph preserving distances and cuts.
5. **Structure trackers**: union-find connectivity, incremental k-core, and Linear Deterministic Greedy partitioning.

## Results

Benchmarked on four real-world graphs from the SNAP collection:

| Dataset | Nodes | Edges | Throughput | Peak RAM |
|---|---|---|---|---|
| Email-Enron | 36.6 K | 183.8 K | 1,608 edges/s | 245 MB |
| CA-AstroPh | 18.7 K | 396.1 K | 1,654 edges/s | 237 MB |
| Amazon0302 | 262.1 K | 1.23 M | 14,916 edges/s | 629 MB |
| DBLP | 425.9 K | 1.04 M | 14,511 edges/s | 678 MB |

Peak memory stays under 700 MB even past a million edges, and GPS estimates triangle counts to within 0.6% on every dataset.

<div class="row">
  <div class="col-sm mt-3 mt-md-0">{% include figure.html path="assets/img/projects/graphstream/triangle-accuracy.png" class="img-fluid rounded z-depth-1" zoomable=true caption="Triangle-count error on real graphs, well under the 5% target." %}</div>
  <div class="col-sm mt-3 mt-md-0">{% include figure.html path="assets/img/projects/graphstream/memory-accuracy-pareto.png" class="img-fluid rounded z-depth-1" zoomable=true caption="Trading memory for accuracy: a bigger sample budget m cuts triangle error from 0.66 to near zero." %}</div>
</div>

The memory-accuracy curve is the key trade-off. On a synthetic 20,000-node graph, raising the sample budget from 1,000 to 50,000 edges cuts the triangle-count error from about 66% to almost zero, while memory grows from about 16 MB to 74 MB.
