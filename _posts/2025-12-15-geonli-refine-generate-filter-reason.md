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
featured: 7
---

> **TL;DR.** Don't ask a VLM for coordinates. We had SAM3 produce masks, filtered them with CLIP, and only asked the VLM to pick among numbered boxes; counts and areas came from geometry, not generation. That design took silver on ISRO's problem with under a fifth of the compute the other top-5 teams used, and beat GeoChat on strict grounding (31.3% vs 19.9% Acc@0.7).

In December 2025 our six-person team (Team 58: Karan Gandhi, Laksh Jain, Romit Mohane, Shreyans Jain, Umang Shikarvar and Viraj Vekaria) took the Silver Medal on the ISRO problem statement at Inter-IIT Tech Meet 14.0. We finished second, with 320.13 points behind IIT Delhi's 400, and we did it using less than one-fifth of the compute the other top-5 teams used. Their budgets were roughly ₹1-2 lakh.

I was the team lead. This post is the leadership and strategy story: how I picked the team, how we chose a direction, where we spent and did not spend compute, and what failed. The technical details are on the [project page]({{ '/projects/geonli/' | relative_url }}), and the code is at [Umang-Shikarvar/GeoNLI](https://github.com/Umang-Shikarvar/GeoNLI).

## The brief

ISRO wanted one natural-language interface to Earth-observation imagery. It had to caption a scene, answer questions (yes/no, numeric, or free-form) and ground a referring expression such as "the smallest plane near the vehicle" with an oriented box. Inputs could be RGB, false-colour composite (FCC) or SAR, and the whole thing had to run on open-source models offline.

That is three tasks, three modalities and one deployment constraint, so the first job as lead was not choosing a model. It was deciding how the work would be split so that every piece fit into the same system.

## Building the team and splitting the work

I selected and assembled the six of us, then set the technical direction for each vertical: captioning, VQA, grounding, domain adaptation and the UI. The split mattered because the tasks depend on each other. Captions use grounding output as input, numeric VQA uses grounding output, and every task depends on getting non-RGB images into a form the models understand. If each person had built a standalone solution, we would have had six demos and no system.

I kept grounding for myself. It was the task everything else leaned on, so it was the one where a mistake would cost us the most, and I wanted to be the person debugging it.

## How we chose a direction

Off-the-shelf VLMs struggle with this kind of imagery for four reasons, and they drove the plan:

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

VRSBench does not label every instance: a scene can have 50 cars with only 5 annotated. A detector trained to find everything gets penalised for correct detections that nobody labelled. So we trained SAM3 on the single instance a query refers to, with a weakly supervised setup, and a composite loss of focal, presence, L1 and GIoU terms.

## Compute: where we spent and where we did not

The headline number is the budget. The other top-5 teams were working with budgets of roughly ₹1-2 lakh, and we used less than a fifth of the compute they did. I managed the budget and the GPU allocation, so I can say what that looked like in the design.

The savings did not come from one trick. They came from a handful of design choices that all point the same way:

- **No training of large models from scratch.** Everything is built on open-source models used zero-shot or lightly adapted. Domain adaptation is a deterministic layer, a linear model for FCC, so RGB-pretrained models work unchanged.
- **Small, cheap fine-tuning.** SAM3 was trained with frozen vision and text encoders, updating only the mask decoder and prompt encoder, for a single epoch. Captioning used LoRA with mixed precision on a single A100. VQA fine-tuning used two L40S GPUs.
- **Deterministic code instead of more model.** Counting, length, area and perimeter come from geometry on the filtered boxes. A larger model would have cost more and still guessed.
- **Selective use of expensive steps.** Super-resolution helped attribute recognition on very low-resolution crops but sometimes added artefacts, so we used it selectively rather than everywhere.

The lesson I took from it: compute efficiency is mostly an architecture decision. Every time a deterministic component can replace a model call, you save GPU time and gain debuggability.

## What failed or nearly did

Our ablations are a decent record of the things that went wrong:

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

Full details are on the [GeoNLI project page]({{ '/projects/geonli/' | relative_url }}), and the code is on [GitHub](https://github.com/Umang-Shikarvar/GeoNLI).
