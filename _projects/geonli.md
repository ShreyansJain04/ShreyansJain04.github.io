---
layout: page
title: "GeoNLI: A Natural-Language Interface for Satellite Imagery"
description: "Refine-Generate-Filter-Reason pipeline for grounding, captioning and VQA on EO imagery; 31.3% Acc@0.7 on VRSBench. Inter-IIT 14.0 Silver, led by Shreyans."
img: assets/img/projects/geonli/thumb.jpg
importance: "1"
category: "Competition"
award: "Silver Medal, Inter-IIT Tech Meet 14.0 (ISRO problem statement)"
period: "Inter-IIT Tech Meet 14.0 · Dec 2025"
role: "Team Lead"
team: "Team 58: Karan Gandhi, Laksh Jain, Romit Mohane, Shreyans Jain, Umang Shikarvar, Viraj Vekaria"
links:
  code: https://github.com/Umang-Shikarvar/GeoNLI
  blog: /blog/2025/geonli-refine-generate-filter-reason/
tags: [remote sensing, VLM, SAM3, grounding, VQA, captioning]
highlights:
  - "Team lead: assembled the 6-member team, set the direction for every vertical, managed budget and compute, and led the final presentation."
  - "Built the segmentation-first grounding pipeline (SAM3 + CLIP + VLM reasoning): 31.3% Acc@0.7 on VRSBench vs 19.9% for GeoChat."
  - "Won silver using less than one-fifth of the compute of other top-5 teams, whose budgets ran ₹1–2 lakh."
---

<div class="tldr" markdown="1">
**Problem.** ISRO's Inter-IIT 14.0 problem asked for a natural-language interface to Earth-observation imagery: captioning, visual question answering (VQA) and oriented referring-expression grounding, over RGB, false-colour (FCC) and SAR inputs, using only open-source models that run offline.  
**Approach.** A neuro-symbolic **Refine-Generate-Filter-Reason** pipeline: deterministic domain adaptation to a unified RGB, a fine-tuned SAM3 for oriented grounding, CLIP and NMS filtering, a VLM for final selection, and a router that sends numeric questions to a geometry engine.  
**Result.** 31.3% Acc@0.7 for grounding on VRSBench (GeoChat: 19.9%). **Silver Medal**, second place on the leaderboard with 320.13 points behind IIT Delhi's 400.  
**My role.** Team lead. I assembled the team, set the technical direction for every vertical, managed budget and GPU compute, and presented to the judges. I personally drove the SAM3-based grounding pipeline.
</div>

## Leading the team

I led Team 58 for the ISRO problem statement. In practice that meant:

- **Team selection.** I selected and assembled the six-person team.
- **Technical direction for every vertical.** I set the direction for captioning, VQA, grounding, domain adaptation and the UI, so that the pieces fit into one pipeline rather than six separate demos.
- **Grounding, hands-on.** I personally drove the grounding pipeline, the SAM3-based Refine-Generate-Filter-Reason system described below.
- **Budget and compute.** I managed the budget and the GPU compute, and made the call on where compute was worth spending.
- **Final presentation.** I led the final presentation to the judges.

<div class="tldr" markdown="1">
**Compute efficiency.** We used **less than one-fifth of the compute** used by the other teams in the leaderboard's top 5, whose budgets were roughly ₹1-2 lakh.
</div>

## Problem and constraints

Satellite images are hard for general vision-language models for two reasons: objects are small and crowded (parking lots, harbours, airfields), and the inputs are spectrally odd. FCC images map NIR/Red/Green to the display channels, and SAR has no colour at all.

The system answers three kinds of requests from one interface:

- **Grounding (Task A):** oriented referring-expression comprehension, e.g. "the red car on the left", returned as oriented bounding boxes (OBBs).
- **Captioning (Task B):** concise, expert-style captions covering object types, coarse counts, attributes and anomalies.
- **VQA (Task C):** binary, numeric (counts, length, area) and semantic questions.

Everything is built from open-source components that run offline on local GPUs (Mistral-7B, Qwen3-VL, SAM 3, OpenCLIP, Real-ESRGAN), with no proprietary APIs.

## System overview

{% include figure.html path="assets/img/projects/geonli/report/slide_p02.png" class="img-fluid rounded z-depth-1" zoomable=true caption="Full architecture: React dashboard, Vercel proxy and Flask server in front of domain adaptation and the captioning, VQA and grounding pipelines." %}

## Method

### Domain adaptation

A deterministic layer converts every input to RGB so that RGB-pretrained models work zero-shot. FCC images are converted to natural colour by synthesising the missing blue channel with a linear model over green, red and NIR (following Patra et al.), which avoids errors like reading red vegetation as fire. SAR images go through a Pix2Pix SAR-to-RGB generator. Real-ESRGAN is used only as a 4x sharpening step so small objects keep clean edges.

### Grounding (my focus)

Token-based VLM grounding quantises coordinates, merges instances in dense clusters, and outputs axis-aligned boxes for rotated objects. We use a segmentation-first design instead:

1. **Refine:** Mistral-7B turns a query such as "leftmost airplane" into the atomic prompt "airplane".
2. **Generate:** a SAM3 model fine-tuned on VRSBench produces dense masks. Oriented boxes are recovered from mask contours with rotating calipers, so a model supervised on axis-aligned data can still output rotated boxes.
3. **Filter:** each candidate is cropped, rotated to axis alignment and scored with CLIP (threshold 0.25), then NMS removes duplicates. This drops shadows, gangways and service vehicles.
4. **Reason:** Qwen3-VL sees the image with indexed, coloured boxes plus each box's coordinates and area, and picks the indices that match the full spatial query. It returns JSON with a rationale. Choosing an index is far easier for a VLM than regressing coordinates.

VRSBench annotations are sparse (for example 5 of 50 cars labelled), so a standard detector is penalised for correct but unlabelled detections. We fine-tuned SAM3 on a single referenced instance per query with a weakly supervised setup and a composite focal, presence, L1 and GIoU loss. The vision and text encoders are frozen, only the mask decoder and prompt encoder are updated, and training runs for one epoch.

{% include figure.html path="assets/img/projects/geonli/sam_methodology.jpeg" class="img-fluid rounded z-depth-1" zoomable=true caption="Grounding pipeline: Refine (Mistral-7B), Generate (fine-tuned SAM3 to OBB), Filter (CLIP + NMS), Reason (Qwen3-VL)." %}

{% include figure.html path="assets/img/projects/geonli/report/p04_2.png" class="img-fluid rounded z-depth-1" zoomable=true caption="Dense airport scene: input, raw SAM3 output, after NMS, after CLIP filtering (which removes shadows and a service van), and the final VLM selection." %}

{% include figure.html path="assets/img/projects/geonli/report/p10_2.jpg" class="img-fluid rounded z-depth-1" zoomable=true caption="Four query types on one scene: spatial (leftmost plane), attribute (smallest plane), region (planes at the bottom) and relational (plane near the vehicle)." %}

### VQA

A Mistral-7B router decides how each question is answered:

- **Semantic** questions go straight to a fine-tuned Qwen3-VL-8B.
- **Binary** questions are routed either to the VLM alone (global scene reasoning) or through grounding, where the VLM answers over the filtered detections (specific objects, proximity, positional relations).
- **Numeric** questions (count, length, area, perimeter) run through grounding, and a deterministic geometry engine computes the number from the filtered boxes, using the image's spatial resolution. The model does not guess.

If parsing fails or the detection is ambiguous, the system falls back to the VLM, so a valid answer is always returned.

{% include figure.html path="assets/img/projects/geonli/vqa_methodology.png" class="img-fluid rounded z-depth-1" zoomable=true caption="VQA router: semantic queries go to the VLM; binary and numeric queries use SAM + CLIP boxes and a deterministic calculation layer, with VLM fallback." %}

### Captioning

Captioning is grounding-first. The Task A detections (classes, OBBs, confidences) are serialised and injected into the prompt as verified hints, with the instruction to use only those detections and not to hallucinate objects. Qwen3-VL-8B is fine-tuned on VRSBench captions with LoRA and mixed precision, then decoded with a short token budget.

## Results

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

The 0.56 numeric score is why the deterministic engine exists: it replaces estimation with calculation. We did not measure the full hybrid pipeline separately on this metric.

**Captioning:**

| Method | BLEU-1 | BLEU-2 | BLEU-3 | BLEU-4 | CIDEr | BERTScore F1 |
|---|---|---|---|---|---|---|
| GeoChat w/o ft | 13.9 | 6.6 | 3.0 | 1.4 | 0.4 | - |
| LLaVA-1.5 | 48.1 | 31.5 | 21.2 | **14.7** | **33.9** | - |
| GeoChat | 46.7 | 30.2 | 20.1 | 13.8 | 28.2 | - |
| **GeoNLI** | **52.9** | 22.2 | 10.8 | 12.6 | - | **0.897** |

GeoNLI leads on BLEU-1 but trails on BLEU-2 to BLEU-4, which we attribute to a concise captioning style. CIDEr was not reported for our model.

**Ablations.**

- Removing the CLIP filter dropped IoU by about 12%, mostly from SAM3 segmenting shadows.
- Fine-tuning the full SAM3 diverged after two epochs; freezing the vision encoder was essential.
- Cutting the focal loss weight from 20 to 1 made the model ignore small objects entirely.
- One epoch was best; further training overfit and hurt zero-shot generalisation.

{% include figure.html path="assets/img/projects/geonli/results.png" class="img-fluid rounded z-depth-1" zoomable=true caption="Problem-statement scoreboard: IIT Gandhinagar (Team 58) second with 320.13 points, behind IIT Delhi's 400." %}

## Demo and UI

A React (Vite) dashboard sits in front of a Flask GPU backend, with a Vercel proxy providing an HTTPS endpoint for judge evaluation. Users upload an image, pick its type (RGB, SAR or FCC) and spatial resolution, generate a caption, or chat with Grounding and VQA toggles to get text answers and OBB overlays. A single `POST /geoNLI/eval` endpoint serves a structured evaluation mode and an interactive mode, and models are pre-loaded at startup.

<div class="row">
  <div class="col-sm mt-3 mt-md-0">{% include figure.html path="assets/img/projects/geonli/ui.jpg" class="img-fluid rounded z-depth-1" zoomable=true caption="The dashboard: image sessions, canvas, grounding, VQA and caption actions." %}</div>
  <div class="col-sm mt-3 mt-md-0">{% include figure.html path="assets/img/projects/geonli/backend_and_frotend_arch.jpg" class="img-fluid rounded z-depth-1" zoomable=true caption="GPU server with a model manager and three pipelines, behind a Vercel proxy." %}</div>
</div>

**Stack:** Flask, React + Vite, PyTorch, Hugging Face Transformers; Mistral-7B, Qwen3-VL, SAM 3, OpenCLIP, Pix2Pix, Real-ESRGAN.

## Lessons and what I would do next

- **Errors cascade.** Caption quality is bounded by grounding recall; objects SAM3 misses are invisible downstream.
- **The router is a single point of fragility.** Mistral-7B can misroute ambiguous queries, and VLM JSON occasionally breaks despite regex extraction and repair. A learned or more robust router is the obvious next step.
- **Geometry assumptions.** Rotating calipers assume roughly convex objects, so U-shaped buildings get loose boxes.
- **Generated inputs.** Pix2Pix can invent or erase structure on SAR, and fixed FCC coefficients may shift colours on uncalibrated sensors.
- **Compute load.** SAM3 plus a VLM plus preprocessing strains GPUs on large images.

The main lesson: put deterministic code wherever a precise answer exists, and keep the generative models for the parts that need language.

## Team and links

Team 58, IIT Gandhinagar: Karan Gandhi, Laksh Jain, Romit Mohane, Shreyans Jain (team lead), Umang Shikarvar, Viraj Vekaria.

- [Code on GitHub](https://github.com/Umang-Shikarvar/GeoNLI)
- [Write-up: how we won silver with a fraction of the compute]({{ '/blog/2025/geonli-refine-generate-filter-reason/' | relative_url }})
