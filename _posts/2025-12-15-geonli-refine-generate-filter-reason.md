---
layout: post
title: "How we won silver at Inter-IIT 14.0 with 1/5th the compute"
date: 2025-12-15
description: "Leading Team 58 through the ISRO problem at Inter-IIT Tech Meet 14.0: why we chose segmentation-first grounding, how we budgeted GPUs, and what did not work."
tags: [remote sensing, VLM, SAM3, neuro-symbolic, leadership]
categories: project-writeups
related_posts: false
toc:
  sidebar: left
project: geonli
---
<!-- Source conflicts resolved to the report values: CLIP threshold 0.25 (deck says 0.24); SAM3 fine-tuned for 1 epoch (deck says 3). Do not mention on the page. -->

<div class="tldr" markdown="1">
**Problem.** ISRO's Inter-IIT 14.0 problem asked for a natural-language interface to Earth-observation imagery: captioning, visual question answering (VQA) and oriented referring-expression grounding, over RGB, false-colour (FCC) and SAR inputs, using only open-source models that run offline.  
**Approach.** A neuro-symbolic **Refine-Generate-Filter-Reason** pipeline: deterministic domain adaptation to a unified RGB, a fine-tuned SAM3 for oriented grounding, CLIP and NMS filtering, a VLM for final selection, and a router that sends numeric questions to a geometry engine.  
**Result.** 31.3% Acc@0.7 for grounding on VRSBench (GeoChat: 19.9%). **Silver Medal**, second place on the leaderboard with 320.13 points behind IIT Delhi's 400.  
**My role.** Team lead. I assembled the team, set the technical direction for every vertical, managed budget and GPU compute, and presented to the judges. I personally drove the SAM3-based grounding pipeline.
</div>

<!-- Source conflicts resolved to the report values: CLIP threshold 0.25 (deck says 0.24); SAM3 fine-tuned 1 epoch (deck says 3). Do not mention on the page. -->

In December 2025 our six-person team (Team 58: Karan Gandhi, Laksh Jain, Romit Mohane, Shreyans Jain, Umang Shikarvar and Viraj Vekaria) took the Silver Medal on the ISRO problem statement at Inter-IIT Tech Meet 14.0. We finished second, with 320.13 points behind IIT Delhi's 400, and we did it using less than one-fifth of the compute the other top-5 teams used. Their budgets were roughly ₹1-2 lakh.

I was the team lead. This post is the leadership and strategy story: how I picked the team, how we chose a direction, where we spent and did not spend compute, and what failed. The full technical details are in the [last section](#technical-details), and the code is at [Umang-Shikarvar/GeoNLI](https://github.com/Umang-Shikarvar/GeoNLI).

## The brief

ISRO wanted one natural-language interface to Earth-observation imagery. It had to caption a scene, answer questions (yes/no, numeric, or free-form) and ground a referring expression such as "the smallest plane near the vehicle" with an oriented box. Inputs could be RGB, false-colour composite (FCC) or SAR, and the whole thing had to run on open-source models offline.

That is three tasks, three modalities and one deployment constraint, so the first job as lead was not choosing a model. It was deciding how the work would be split so that every piece fit into the same system.

## Building the team and splitting the work

I selected and assembled the six of us, then set the technical direction for each vertical: captioning, VQA, grounding, domain adaptation and the UI. The split mattered because the tasks depend on each other. Captions use grounding output as input, numeric VQA uses grounding output, and every task depends on getting non-RGB images into a form the models understand. If each person had built a standalone solution, we would have had six demos and no system.

I kept grounding for myself. It was the task everything else leaned on, so it was the one where a mistake would cost us the most, and I wanted to be the person debugging it.

## How we chose a direction

The report lays out why off-the-shelf VLMs struggle here, and these reasons drove the plan:

- **Coordinates as tokens lose precision.** A VLM that emits box coordinates quantises them into bins. In a parking lot or a harbour full of containers, neighbouring objects merge.
- **Axis-aligned bias.** A ship lying on a diagonal gets a box full of background.
- **Hallucinated arithmetic.** VLMs miscount dense clusters and cannot compute area or perimeter.
- **Spectral mismatch.** FCC and SAR images do not look like what RGB-trained encoders were trained on. Passing FCC directly led to errors like reading red vegetation as fire.

Each problem pointed at the same idea: do not ask one end-to-end model to do everything. Let each component do what it is good at, and put deterministic code wherever a precise answer exists. That gave us the neuro-symbolic structure: fix the input first, ground with a segmentation model, filter and reason over candidates, and compute numbers instead of guessing them.

## Why segmentation-first grounding

This was the central bet, and I drove it. Instead of asking a VLM for coordinates, we ask SAM3 for masks and recover oriented boxes from the contours with rotating calipers. That solves the precision, merging and rotation problems together.

SAM3 on its own over-segments, though. On an airport scene it returns shadows, gangways and service vehicles as "airplanes". So the pipeline has four stages:

1. **Refine.** Mistral-7B strips spatial language from the query ("leftmost airplane" becomes "airplane"), because a segmenter has no idea what "leftmost" means.
2. **Generate.** A SAM3 model fine-tuned on VRSBench produces dense masks and oriented boxes.
3. **Filter.** CLIP scores each rotated crop against the class text, and NMS removes duplicates.
4. **Reason.** Qwen3-VL sees the image with indexed, coloured boxes and picks the ones matching the full query, returning JSON with a rationale.

{% include figure.html path="assets/img/projects/geonli/sam_methodology.jpeg" class="img-fluid rounded z-depth-1" zoomable=true caption="Refine, Generate, Filter, Reason." %}

The point of the last stage is a division of labour. A VLM is poor at regressing coordinates but good at looking at five numbered boxes and saying which one is "the smallest plane". We turned a hard task into an easy one.

{% include figure.html path="assets/img/projects/geonli/report/p04_2.png" class="img-fluid rounded z-depth-1" zoomable=true caption="Raw SAM3 output, after NMS, after CLIP filtering, and the final VLM pick on an airport scene." %}

### Fine-tuning on sparse labels

VRSBench does not label every instance. The report gives the example of 5 of 50 cars being annotated. A detector trained to find everything gets penalised for correct detections that nobody labelled. So we trained SAM3 on the single instance a query refers to, with a weakly supervised setup, and a composite loss of focal, presence, L1 and GIoU terms.

## Compute: where we spent and where we did not

The headline number is the budget. The other top-5 teams were working with budgets of roughly ₹1-2 lakh, and we used less than a fifth of the compute they did. I managed the budget and the GPU allocation, so I can say what that looked like in the design.

The report does not give a per-decision cost breakdown, so I will stick to the choices it documents, which all point the same way:

- **No training of large models from scratch.** Everything is built on open-source models used zero-shot or lightly adapted. Domain adaptation is a deterministic layer, a linear model for FCC, so RGB-pretrained models work unchanged.
- **Small, cheap fine-tuning.** SAM3 was trained with frozen vision and text encoders, updating only the mask decoder and prompt encoder, for a single epoch. Captioning used LoRA with mixed precision on a single A100. VQA fine-tuning used two L40S GPUs.
- **Deterministic code instead of more model.** Counting, length, area and perimeter come from geometry on the filtered boxes. A larger model would have cost more and still guessed.
- **Selective use of expensive steps.** Super-resolution helped attribute recognition on very low-resolution crops but sometimes added artefacts, so we used it selectively rather than everywhere.

The lesson I took from it: compute efficiency is mostly an architecture decision. Every time a deterministic component can replace a model call, you save GPU time and gain debuggability.

## What failed or nearly did

The ablations in the report are a decent record of the things that went wrong:

- **Removing the CLIP filter** caused a spike in false positives, mostly shadows, and IoU dropped by about 12%.
- **Fine-tuning the full SAM3** diverged after two epochs. Freezing the vision encoder was essential.
- **Aggressive loss weights** were unstable. Lowering the classification and presence weights from 20 to 10 and the focal positive weight from 10 to 5 helped, with gradient clipping and warmup. Cutting the focal weight all the way from 20 to 1 made the model ignore small objects entirely.
- **More epochs** overfit and hurt zero-shot generalisation. One epoch was best out of the 1-5 we tried.

None of these was a surprise in hindsight, but each one cost iteration time, which is exactly what a budget-constrained team cannot waste.

## VQA and captioning: letting the pipeline do the hard part

Captioning is grounding-first. We serialise the verified detections into the prompt and tell the model to use only those, which cuts hallucinated objects. The cost is a recall ceiling: if SAM3 misses an object, the caption cannot mention it.

VQA uses a Mistral-7B router. Semantic questions go to a fine-tuned Qwen3-VL-8B, while binary and numeric ones go through grounding. For numbers, a geometry engine computes the answer. The fine-tuned VLM alone scored 90.86 binary accuracy but only 0.56 on the numeric score, which is why the engine exists. If anything fails to parse, the system falls back to the VLM so an answer always comes back.

{% include figure.html path="assets/img/projects/geonli/vqa_methodology.png" class="img-fluid rounded z-depth-1" zoomable=true caption="The VQA router and deterministic calculation layer." %}

## The result, honestly

On the VRSBench validation split, strict grounding accuracy (Acc@0.7) was 31.3% against 19.9% for GeoChat and 13.6% for LLaVA-1.5. On the crowded non-unique subset it was 32.5% against 18.0% for GeoChat. GeoChat still beats us on Unique Acc@0.5 (57.4 vs 52.5), so the win is about precision and clutter. In captioning we lead on BLEU-1 (52.9) and report BERTScore F1 0.897, but trail on BLEU-2 to BLEU-4 because our captions are terse.

{% include figure.html path="assets/img/projects/geonli/results.png" class="img-fluid rounded z-depth-1" zoomable=true caption="The final scoreboard: Team 58 (IIT Gandhinagar) second, 320.13 points, behind IIT Delhi's 400." %}

## Presenting it

I led the final presentation to the judges. The pipeline's stage-by-stage structure helped here: it is easy to show a dense airport scene and walk through raw SAM3 output, NMS, CLIP filtering and the final selection. Explainability was a real asset when time was short.

## What I would do differently

- **Errors cascade.** A hierarchical pipeline is explainable, but its recall ceiling is set by the first stage.
- **The router is fragile.** It can misroute ambiguous queries, and malformed VLM JSON can still slip past regex extraction and repair.
- **Geometry assumptions.** Rotating calipers assume convex shapes, so U-shaped buildings get loose boxes.
- **Generated inputs.** Pix2Pix can invent or erase structure in SAR, and fixed FCC coefficients may shift colours on uncalibrated sensors.

The biggest lesson was about leadership as much as modelling: pick one architectural idea, make every vertical serve it, and spend compute only where a model is genuinely needed.

The code is on [GitHub](https://github.com/Umang-Shikarvar/GeoNLI).

## Technical details

The story above covers the decisions. This section is the reference: the full architecture, the remaining pipeline pieces and every number from the report.

### System overview

{% include figure.html path="assets/img/projects/geonli/report/slide_p02.png" class="img-fluid rounded z-depth-1" zoomable=true caption="Full architecture: React dashboard, Vercel proxy and Flask server in front of domain adaptation and the captioning, VQA and grounding pipelines." %}

### Domain adaptation

A deterministic layer converts every input to RGB so that RGB-pretrained models work zero-shot. FCC images are converted to natural colour by synthesising the missing blue channel with a linear model over green, red and NIR (following Patra et al.), which avoids errors like reading red vegetation as fire. SAR images go through a Pix2Pix SAR-to-RGB generator. Real-ESRGAN is used only as a 4x sharpening step so small objects keep clean edges.

### Query types

{% include figure.html path="assets/img/projects/geonli/report/p10_2.jpg" class="img-fluid rounded z-depth-1" zoomable=true caption="Four query types on one scene: spatial (leftmost plane), attribute (smallest plane), region (planes at the bottom) and relational (plane near the vehicle)." %}

### Full results

All numbers are on the official VRSBench validation split (9,350 images).

**Grounding (Acc@IoU, %).**

| Method | Unique @0.5 | Unique @0.7 | Non-Unique @0.5 | Non-Unique @0.7 | All @0.5 | All @0.7 |
|---|---|---|---|---|---|---|
| GeoChat w/o ft | 20.7 | 5.4 | 7.3 | 1.7 | 12.9 | 3.2 |
| LLaVA-1.5 | 51.1 | 16.4 | 34.8 | 11.5 | 41.6 | 13.6 |
| GeoChat | **57.4** | 22.6 | 44.5 | 18.0 | 49.8 | 19.9 |
| **GeoNLI** | 52.5 | **30.0** | **55.0** | **32.5** | **53.8** | **31.3** |

Strict-precision accuracy (Acc@0.7) is about double the strong VLM baselines, and the gain is largest on the non-unique (crowded) subset: 32.5% against 18.0% for GeoChat. GeoChat still wins the loose Unique Acc@0.5, so the advantage is precision and clutter handling, not everywhere.

**Localisation quality (mIoU).**

| Subset | mIoU |
|---|---|
| Unique | 42.60% |
| Non-Unique | 42.28% |
| **Overall** | **42.44%** |

**VQA** (fine-tuned Qwen3-VL-8B baseline, without the router pipeline):

| Metric | Value |
|---|---|
| Binary accuracy | 90.86 |
| Semantic (BERT-BLEU) | 0.79 |
| Numeric score | 0.56 |
| MAE / RMSE | 0.73 / 1.41 |
| Format failures | 0 |

The 0.56 numeric score is why the deterministic engine exists: it replaces estimation with calculation. The report does not give separate numbers for the full hybrid pipeline.

**Captioning:**

| Method | BLEU-1 | BLEU-2 | BLEU-3 | BLEU-4 | CIDEr | BERTScore F1 |
|---|---|---|---|---|---|---|
| GeoChat w/o ft | 13.9 | 6.6 | 3.0 | 1.4 | 0.4 | - |
| LLaVA-1.5 | 48.1 | 31.5 | 21.2 | **14.7** | **33.9** | - |
| GeoChat | 46.7 | 30.2 | 20.1 | 13.8 | 28.2 | - |
| **GeoNLI** | **52.9** | 22.2 | 10.8 | 12.6 | - | **0.897** |

GeoNLI leads on BLEU-1 but trails on BLEU-2 to BLEU-4, which the report attributes to a concise captioning style. CIDEr was not reported for our model.

**Ablations.**

- Removing the CLIP filter dropped IoU by about 12%, mostly from SAM3 segmenting shadows.
- Fine-tuning the full SAM3 diverged after two epochs; freezing the vision encoder was essential.
- Cutting the focal loss weight from 20 to 1 made the model ignore small objects entirely.
- One epoch was best; further training overfit and hurt zero-shot generalisation.

### Demo and UI

A React (Vite) dashboard sits in front of a Flask GPU backend, with a Vercel proxy providing an HTTPS endpoint for judge evaluation. Users upload an image, pick its type (RGB, SAR or FCC) and spatial resolution, generate a caption, or chat with Grounding and VQA toggles to get text answers and OBB overlays. A single `POST /geoNLI/eval` endpoint serves a structured evaluation mode and an interactive mode, and models are pre-loaded at startup.

<div class="row">
  <div class="col-sm mt-3 mt-md-0">{% include figure.html path="assets/img/projects/geonli/ui.jpg" class="img-fluid rounded z-depth-1" zoomable=true caption="The dashboard: image sessions, canvas, grounding, VQA and caption actions." %}</div>
  <div class="col-sm mt-3 mt-md-0">{% include figure.html path="assets/img/projects/geonli/backend_and_frotend_arch.jpg" class="img-fluid rounded z-depth-1" zoomable=true caption="GPU server with a model manager and three pipelines, behind a Vercel proxy." %}</div>
</div>

**Stack:** Flask, React + Vite, PyTorch, Hugging Face Transformers; Mistral-7B, Qwen3-VL, SAM 3, OpenCLIP, Pix2Pix, Real-ESRGAN.

### Team and links

Team 58, IIT Gandhinagar: Karan Gandhi, Laksh Jain, Romit Mohane, Shreyans Jain (team lead), Umang Shikarvar, Viraj Vekaria.

- [Code on GitHub](https://github.com/Umang-Shikarvar/GeoNLI)
