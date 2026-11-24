---
layout: page
title: "AI-Generated Image Detection and Artifact Explanation"
description: "LeViT + Neighboring Pixel Relationships detector reaching 99.21% on CIFAKE, plus Ovis VLM artifact explanations. Inter-IIT 13.0 Silver."
img: assets/img/projects/ai-image-detection/thumb.jpg
importance: "2"
category: "Competition"
award: "Silver Medal, Inter-IIT Tech Meet 13.0 (Adobe Research problem statement)"
period: "Nov 2024 – Dec 2024"
team: "Team 64"
links:
  code: https://github.com/ShreyansJain04/AI-Image-Detection-Artifact-Identification
  blog: /blog/2024/ai-image-detection-adobe-inter-iit/
tags: [deepfake detection, LeViT, NPR, vision-language models, XAI]
highlights:
  - "Detected AI-generated images with LeViT + Neighboring Pixel Relationships (NPR): 99.21% accuracy on CIFAKE, the highest of all participating IITs."
  - "Improved robustness with a custom dataset and new frequency-domain augmentations; Ovis VLM explains the artifacts it finds."
  - "Continued afterwards with Adobe Research on out-of-distribution generalization (adversarial, self-supervised and continual learning)."
---

<div class="tldr" markdown="1">
**Problem.** Adobe Research's Inter-IIT 13.0 problem: detect AI-generated images in a 32x32 dataset (CIFAKE plus GAN, diffusion and Adobe Firefly images), then explain *why* an image looks synthetic.  
**Approach.** A LeViT-192 classifier on Neighboring Pixel Relationship (NPR) features, pretrained on 4M GenImage samples, fine-tuned on CIFAKE with frequency-noise and blur augmentation and focal loss. A zero-shot Ovis 1.6 VLM then names and describes artifacts in flagged images.  
**Result.** **99.21%** accuracy on CIFAKE (F1 0.9869), the highest accuracy among competing teams. **Silver Medal** at Inter-IIT Tech Meet 13.0, IIT Bombay.
</div>

## Overview

Generative models make it easy to produce convincing images, so detectors need to be accurate, robust to the way images are actually shared (compression, blur, noise), and ideally able to justify their decisions. The challenge, posed by Adobe Research, had two tasks: (1) classify real versus AI-generated images at 32x32 resolution, and (2) identify the artifacts in images flagged as fake and write a short explanation. The low resolution makes models cheap, but it erases much of the fine detail that human-visible artifacts rely on.

## Method

### Task 1: detection

**NPR.** Up-sampling layers in generators leave local correlations between neighbouring pixels. NPR captures these relationships directly in the spatial domain rather than through frequency analysis, which is what let our detector generalise across generators.

{% include figure.html path="assets/img/projects/ai-image-detection/npr1.png" class="img-fluid rounded z-depth-1" zoomable=true caption="NPR heatmaps per colour channel for a real image and its counterpart, and differential NPR between real and fake (figure from the NPR work, reproduced in our report)." %}

**LeViT.** We chose LeViT, a hybrid convolution-plus-attention transformer built for fast inference, and settled on LeViT-192 after comparing it with LeViT-128/128s and EfficientNet variants.

{% include figure.html path="assets/img/projects/ai-image-detection/levit.png" class="img-fluid rounded z-depth-1" zoomable=true caption="LeViT-192 architecture." %}

**Training.** Stage one pretrains on 4 million images subsampled from GenImage, resized to 32x32 and spanning ImageNet-1K classes and many generators. Stage two fine-tunes on CIFAKE (60,000 images: 50,000 train, 10,000 test). We added compression and blur augmentation, plus frequency noise created by manipulating Fourier components, and used a focal-loss variant to focus on hard examples:

$$
\mathrm{FL}(p_t) = -\alpha (1 - p_t)^\gamma \log(p_t) + 0.6\cdot \mathrm{BCE}
$$

<div class="row">
  <div class="col-sm mt-3 mt-md-0">{% include figure.html path="assets/img/projects/ai-image-detection/infer.png" class="img-fluid rounded z-depth-1" zoomable=true caption="Parameter count vs inference time across candidate models." %}</div>
  <div class="col-sm mt-3 mt-md-0">{% include figure.html path="assets/img/projects/ai-image-detection/p_values.jpg" class="img-fluid rounded z-depth-1" zoomable=true caption="P-values of image features under frequency noise and blur." %}</div>
</div>

A statistical analysis showed that frequency noise shifts frequency-domain features such as mean frequency, while blur disturbs texture descriptors (LBP), leaving global statistics like mean and variance largely unchanged. That told us the two perturbations probe different weaknesses.

### Task 2: artifact explanation

No dataset pairs fake images with labelled artifacts, so we went zero-shot. Images flagged by Task 1 are passed to **Ovis 1.6 (Gemma2-9B)** with a single prompt listing candidate artifacts (inconsistent object boundaries, texture bleeding, unrealistic reflections, conflicting light sources, aliasing at high-contrast edges). The model returns structured `{artifact: explanation}` output.

{% include figure.html path="assets/img/projects/ai-image-detection/ovis.png" class="img-fluid rounded z-depth-1" zoomable=true caption="Ovis architecture, used as the zero-shot artifact explainer." %}

## Results

| Model | Accuracy (%) | F1 |
|---|---|---|
| LeViT_128 | 97.14 | 0.9711 |
| LeViT_192 | 95.87 | 0.9586 |
| LeViT_192 + Aug | 98.17 | 0.9817 |
| EfficientNet_b0 | 98.47 | 0.9847 |
| LeViT_128 + NPR | 98.88 | 0.98 |
| **LeViT_192 + NPR + Aug + Frequency Noise** | **99.21** | **0.9869** |

Each ingredient helped: augmentation lifted LeViT-192 from 95.87% to 98.17%, and adding NPR with frequency noise pushed it to 99.21%. Qualitatively, Ovis surfaced explanations such as texture bleeding between adjacent regions, artificial noise patterns on uniform surfaces, blurred object boundaries and distorted window reflections.

**Limitations.** The 32x32 resolution hides subtle cues, some "artifacts" overlap with natural variation (false positives), and scaling to high-resolution images would need more compute and probably a stronger classifier.

## My role

- Team lead: assembled the team from the ML Club, set the technical direction, and built the LeViT + NPR detection framework and the frequency augmentation pipeline.
- Continued with Adobe Research on out-of-distribution robustness, exploring adversarial training, jigsaw-style self-supervised learning and continual learning.
