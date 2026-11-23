---
layout: page
title: "GeoNLI: A Natural-Language Interface for Satellite Imagery"
description: "Refine-Generate-Filter-Reason pipeline for grounding, captioning and VQA on EO imagery; 31.3% Acc@0.7 on VRSBench. Inter-IIT 14.0 Silver."
img: assets/img/projects/geonli/thumb.jpg
importance: 1
category: "Inter-IIT Tech Meet"
award: "Silver Medal, Inter-IIT Tech Meet 14.0 (ISRO problem statement)"
period: "Inter-IIT Tech Meet 14.0"
team: "Team 58: Karan Gandhi, Laksh Jain, Romit Mohane, Shreyans Jain, Umang Shikarvar, Viraj Vekaria"
links:
  code: https://github.com/Umang-Shikarvar/GeoNLI
  blog: /blog/2025/geonli-refine-generate-filter-reason/
tags: [remote sensing, VLM, SAM3, grounding, VQA, captioning]
---

<div class="tldr" markdown="1">
**Problem.** ISRO's Inter-IIT 14.0 problem asked for a natural-language interface to Earth-observation imagery: captioning, visual question answering and referring-expression grounding, over RGB, false-colour (FCC) and SAR inputs.  
**Approach.** A neuro-symbolic **Refine-Generate-Filter-Reason** pipeline: a domain-adaptation layer to a unified RGB, a fine-tuned SAM3 for oriented grounding, CLIP and NMS filtering, a VLM for final selection, and a router that sends numeric questions to a deterministic geometry engine.  
**Result.** On VRSBench, 31.3% Acc@0.7 for grounding (vs 19.9% for GeoChat), BLEU-1 52.9 for captioning, and 90.86% binary VQA accuracy for the fine-tuned VLM baseline. **Silver Medal** for Team 58 (IIT Gandhinagar).
</div>

## Overview

Satellite images are hard for general vision-language models for two reasons. Objects are small and crowded (parking lots, harbours, airfields), and the inputs are spectrally odd: FCC images map NIR/Red/Green to the display channels, and SAR images have no colour at all. GeoNLI is our end-to-end system for the Inter-IIT Tech Meet 14.0 ISRO challenge. It answers three kinds of requests from one interface: *describe this scene*, *answer this question about it*, and *show me the object I am describing*.

The whole system is built from open-source components that run offline on local GPUs (Mistral-7B, Qwen3-VL, SAM 3, OpenCLIP, Real-ESRGAN), and it is served through a Flask backend and a React dashboard.

{% include figure.html path="assets/img/projects/geonli/overall_arch.png" class="img-fluid rounded z-depth-1" zoomable=true caption="End-to-end flow. FCC and SAR inputs are converted to a unified RGB representation before captioning, grounding and VQA." %}

## Method

**Domain adaptation.** FCC images are converted to natural colour by synthesising the missing blue channel with a linear model over green, red and NIR (following Patra et al.), which avoids errors like reading red vegetation as fire. SAR images go through a Pix2Pix SAR-to-RGB generator. Real-ESRGAN is then used only as a 4x sharpening step so that small objects keep clean edges.

**Grounding (Task A).** Token-based VLM grounding quantises coordinates and tends to merge instances in dense clusters, and it outputs axis-aligned boxes for rotated objects. We instead use a segmentation-first design:

1. **Refine:** Mistral-7B turns a query such as "leftmost airplane" into the atomic prompt "airplane".
2. **Generate:** a SAM3 model fine-tuned on VRSBench produces dense masks; oriented boxes are recovered from mask contours with rotating calipers.
3. **Filter:** candidates are cropped, rotated to axis alignment and scored with CLIP (threshold 0.25), followed by NMS, which removes shadows and ground vehicles.
4. **Reason:** Qwen3-VL sees the image with indexed, coloured boxes and picks the indices matching the full spatial query, returning JSON with a rationale.

VRSBench annotations are sparse (a few of many cars may be labelled), so a standard detector would be penalised for correct but unlabelled detections. We therefore fine-tuned SAM3 on a *single referenced instance* per query with a composite focal, presence, L1 and GIoU loss, frozen vision and text encoders, and one epoch of training.

{% include figure.html path="assets/img/projects/geonli/sam_methodology.jpeg" class="img-fluid rounded z-depth-1" zoomable=true caption="Grounding pipeline: Refine (Mistral-7B), Generate (fine-tuned SAM3 to OBB), Filter (CLIP + NMS), Reason (Qwen3-VL)." %}

{% include figure.html path="assets/img/projects/geonli/pipeline_flow_sam3.jpg" class="img-fluid rounded z-depth-1" zoomable=true caption="Dense airport scene: raw SAM3 output, after NMS, and after CLIP filtering, which removes shadows and vehicles." %}

**Captioning (Task B).** Captioning is grounding-first: the Task A detections (classes, OBBs, confidences) are serialised and injected into the prompt as verified hints, and the model is told to use only those detections. Qwen3-VL is fine-tuned on VRSBench captions with LoRA and mixed precision, and decoded greedily with a short token budget.

**VQA (Task C).** A Mistral-7B router sends semantic questions straight to a fine-tuned Qwen3-VL-8B. Binary and numeric questions go through the grounding pipeline, and numeric answers (count, length, area, perimeter) are computed deterministically from the filtered boxes rather than guessed by the model. If parsing fails, the system falls back to the VLM, so a valid answer is always returned.

{% include figure.html path="assets/img/projects/geonli/vqa_methodology.png" class="img-fluid rounded z-depth-1" zoomable=true caption="VQA router: semantic queries go to the VLM; binary and numeric queries use SAM + CLIP boxes and a deterministic calculation layer, with VLM fallback." %}

## System

{% include figure.html path="assets/img/projects/geonli/pipeline.png" class="img-fluid rounded z-depth-1" zoomable=true caption="Full system diagram: React dashboard, Vercel proxy, Flask server, preprocessing and the three task pipelines." %}

<div class="row">
  <div class="col-sm mt-3 mt-md-0">{% include figure.html path="assets/img/projects/geonli/ui.jpg" class="img-fluid rounded z-depth-1" zoomable=true caption="The dashboard: image sessions, canvas, grounding, VQA and caption actions." %}</div>
  <div class="col-sm mt-3 mt-md-0">{% include figure.html path="assets/img/projects/geonli/backend_and_frotend_arch.jpg" class="img-fluid rounded z-depth-1" zoomable=true caption="GPU server with a model manager and three pipelines, behind a Vercel proxy." %}</div>
</div>

The backend exposes a single `POST /geoNLI/eval` endpoint with an evaluation mode (structured JSON, batched query types) and an interactive mode (multipart form data from the UI).

## Results

{% include figure.html path="assets/img/projects/geonli/queries.jpg" class="img-fluid rounded z-depth-1" zoomable=true caption="Grounding on spatial, attribute, region and relational queries (leftmost, smallest, bottom, near a vehicle)." %}

Grounding on the VRSBench validation set (9,350 images):

| Method | Unique Acc@0.7 | Non-Unique Acc@0.7 | All Acc@0.5 | All Acc@0.7 |
|---|---|---|---|---|
| GeoChat | 22.6 | 18.0 | 49.8 | 19.9 |
| LLaVA-1.5 | 16.4 | 11.5 | 41.6 | 13.6 |
| **GeoNLI** | **30.0** | **32.5** | **53.8** | **31.3** |

Overall mIoU is 42.44%. In captioning, GeoNLI reaches BLEU-1 of 52.9 (best baseline 48.1) and BERTScore F1 of 0.897. For VQA, the fine-tuned VLM alone scores 90.86 binary accuracy, MAE 0.73 and RMSE 1.41; the numeric score of 0.56 is the reason the deterministic engine exists. In ablations, removing the CLIP filter dropped IoU by about 12%, and fine-tuning the full SAM3 diverged after two epochs.

{% include figure.html path="assets/img/projects/geonli/results.png" class="img-fluid rounded z-depth-1" zoomable=true caption="Problem-statement scoreboard: IIT Gandhinagar (Team 58) with 320.13 points." %}

Known limits: errors cascade (captions are bounded by grounding recall), the router can misclassify ambiguous queries, and the convexity assumption in rotating calipers gives loose boxes on U-shaped structures.

## My role

- Member of the six-person Team 58 for the ISRO problem statement at Inter-IIT Tech Meet 14.0.
- <!-- TODO: verify and fill in Shreyans's specific contributions (which of grounding / captioning / VQA / UI) -->

More on the design decisions in the [write-up]({{ '/blog/2025/geonli-refine-generate-filter-reason/' | relative_url }}).
