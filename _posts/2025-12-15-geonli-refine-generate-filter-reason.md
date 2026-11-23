---
layout: post
title: "Building GeoNLI: Refine, Generate, Filter, Reason"
date: 2025-12-15
description: "How our Inter-IIT 14.0 ISRO solution handles captioning, VQA and oriented grounding on satellite imagery, and why we split perception from logic."
tags: [remote sensing, VLM, SAM3, neuro-symbolic]
categories: project-writeups
related_posts: false
toc:
  sidebar: left
---

For Inter-IIT Tech Meet 14.0, the ISRO problem statement asked for a natural-language interface to Earth-observation (EO) imagery. Our team (Team 58: Karan Gandhi, Laksh Jain, Romit Mohane, Shreyans Jain, Umang Shikarvar and Viraj Vekaria) ended up with a Silver Medal. This post walks through how the system was put together and, more usefully, why each piece is there. The short version of the project is on the [project page]({{ '/projects/geonli/' | relative_url }}); code is at [Umang-Shikarvar/GeoNLI](https://github.com/Umang-Shikarvar/GeoNLI).

## The problem in one picture

One interface, three tasks: write a caption for a scene, answer a question (yes/no, a number, or a free-form answer), and ground a referring expression such as "the smallest plane near the vehicle" with a box on the image. Inputs can be RGB, false-colour composite (FCC) or SAR.

Two properties of EO data shaped everything. First, objects are small and crowded, so coordinate-token grounding by a VLM tends to merge neighbours and returns axis-aligned boxes for objects that are anything but axis-aligned. Second, the inputs are spectrally strange: a vision encoder trained on RGB reads red vegetation in an FCC image as something very different from vegetation.

{% include figure.html path="assets/img/projects/geonli/overall_arch.png" class="img-fluid rounded z-depth-1" zoomable=true caption="Everything is routed through a unified RGB representation first." %}

## Decision 1: fix the input before touching the model

Rather than hope the VLM generalises across modalities, we add a deterministic domain-adaptation layer. For FCC images (channels map to NIR, Red, Green) we synthesise the missing blue channel with a linear model from the literature (Patra et al.):

$$
B_{synth} = a_B + b_B \cdot G + c_B \cdot R + d_B \cdot \mathrm{NIR}
$$

with coefficients $$a_B = 13.9053$$, $$b_B = 0.8733$$, $$c_B = -0.1382$$, $$d_B = -0.1006$$, then restack as natural colour. For SAR we use a Pix2Pix SAR-to-RGB generator, which keeps geometry while inventing plausible colour. Real-ESRGAN follows as a 4x sharpener only, so the downstream segmenter sees crisp edges and not GAN blur.

The risk, which we wrote down in the report, is that the generator can hallucinate or erase detail, and fixed FCC coefficients assume standard band responses. We accepted that trade because everything downstream got simpler.

## Decision 2: segmentation-first grounding

We did not ask a VLM to emit coordinates. The grounding pipeline has four stages, which gave the report its name.

{% include figure.html path="assets/img/projects/geonli/sam_methodology.jpeg" class="img-fluid rounded z-depth-1" zoomable=true caption="Refine, Generate, Filter, Reason." %}

**Refine.** Mistral-7B strips spatial language from the query ("leftmost airplane" becomes "airplane"), since a segmentation model has no idea what "leftmost" means.

**Generate.** SAM3, fine-tuned on VRSBench, produces dense masks. We recover oriented bounding boxes from the contours with rotating calipers, which is why a model supervised on axis-aligned boxes can still output rotated ones.

**Filter.** SAM3 happily segments shadows, gangways and service vehicles. We crop each candidate, rotate it upright, and score it with CLIP against the class text; anything under 0.25 is dropped, then NMS removes duplicates.

**Reason.** The surviving boxes are drawn on the image with index, colour and area, and Qwen3-VL picks the indices matching the full query, returning JSON with a rationale. Selecting an index is a much easier task for a VLM than regressing coordinates.

{% include figure.html path="assets/img/projects/geonli/pipeline_flow_sam3.jpg" class="img-fluid rounded z-depth-1" zoomable=true caption="Raw SAM3 output, after NMS, after CLIP filtering on an airport scene." %}

### Fine-tuning SAM3 on sparse labels

VRSBench does not label every instance (five of fifty cars might be annotated). A detector trained to find all instances is penalised for correct detections. So we trained SAM3 to segment the *specific instance referenced by the query*, with a composite loss:

$$
L_{total} = \lambda_{ce} L_{ce} + \lambda_{pres} L_{pres} + \lambda_{box} L_{box} + \lambda_{giou} L_{giou}
$$

A focal classification term, a presence term (so the model can say "nothing here"), an L1 box term and a GIoU term. What mattered in practice:

- Aggressive loss weights were unstable; we lowered the classification and presence weights from 20 to 10 and the focal positive weight from 10 to 5.
- One epoch was best. More epochs overfit the prompt phrasing and hurt zero-shot behaviour.
- We froze the ViT and text encoder and trained only the prompt encoder and mask decoder; fine-tuning the whole model diverged after two epochs.
- Gradient clipping, mixed precision and warmup kept training stable.

## Decision 3: captions that must agree with detections

Free-form VLM captions invent objects. Our captioning is *grounding-first*: we run the grounding pipeline, serialise the verified detections (class, box, confidence) into the prompt as hints, and instruct the model to use only those. Qwen3-VL was fine-tuned on VRSBench captions with LoRA and bf16 on a single A100 for fast iteration. The ablation showed hinted generation raises object-level precision. We also learned that super-resolution on low-GSD crops helps attribute recognition (roof colour, vehicle type) but sometimes adds artefacts, so we use it selectively.

The cost is a recall bottleneck: if SAM3 misses an object, the caption cannot mention it.

## Decision 4: do not let the VLM do arithmetic

VLMs miscount dense clusters and cannot compute area or perimeter. The VQA system therefore has a router (Mistral-7B) with three outcomes:

- **Semantic** questions go straight to a fine-tuned Qwen3-VL-8B.
- **Binary** questions run the grounding pipeline, and the VLM answers over the filtered objects.
- **Numeric** questions (count, length, area, perimeter) run grounding and then a deterministic geometry engine computes the number.

If the OBB pipeline fails to parse or is ambiguous, the system falls back to the fine-tuned VLM so an answer is always returned. The VLM alone scored 90.86 binary accuracy but only 0.56 on the numeric score (MAE 0.73, RMSE 1.41), which is exactly the gap the geometry engine targets.

{% include figure.html path="assets/img/projects/geonli/vqa_methodology.png" class="img-fluid rounded z-depth-1" zoomable=true caption="The VQA router and deterministic calculation layer." %}

## What the numbers said

On the VRSBench validation split, strict grounding accuracy (Acc@0.7) was 31.3% against 19.9% for GeoChat and 13.6% for LLaVA-1.5, and on the non-unique (crowded) subset it was 32.5% against 18.0% for GeoChat. At the loose threshold (Acc@0.5) GeoChat is still ahead on the unique subset (57.4 vs 52.5), so the win is about precision and clutter, not everywhere. Captioning reached BLEU-1 52.9 and BERTScore F1 0.897; our BLEU-4 (12.6) is a little below LLaVA-1.5 because our captions are terse. Removing the CLIP filter cost about 12% IoU.

{% include figure.html path="assets/img/projects/geonli/queries.jpg" class="img-fluid rounded z-depth-1" zoomable=true caption="Spatial, attribute, region and relational queries on one airport scene." %}

## Shipping it

The system is a Flask backend with a model manager that wraps each pipeline behind adapters, a single `POST /geoNLI/eval` endpoint with an evaluation mode and an interactive mode, a React/Vite dashboard, and a Vercel proxy in front. All models are open-source and run locally on GPUs.

{% include figure.html path="assets/img/projects/geonli/pipeline.png" class="img-fluid rounded z-depth-1" zoomable=true caption="The full deployed architecture." %}

{% include figure.html path="assets/img/projects/geonli/ui.jpg" class="img-fluid rounded z-depth-1" zoomable=true caption="The dashboard." %}

## What I would do differently

- Errors cascade. A hierarchical pipeline is explainable but its recall ceiling is set by the first stage.
- The router is a single point of fragility, and malformed VLM JSON can slip past even regex extraction and repair.
- Rotating calipers assumes convex shapes, so U-shaped buildings get loose boxes.
- A learned way to threshold the CLIP filter would beat a fixed 0.25.

The biggest lesson was to put deterministic code wherever a precise answer exists and keep the generative models for the parts that really need language. That separation is also what made the system debuggable under competition time pressure.

Full details: [GeoNLI project page]({{ '/projects/geonli/' | relative_url }}) and the [code](https://github.com/Umang-Shikarvar/GeoNLI).
