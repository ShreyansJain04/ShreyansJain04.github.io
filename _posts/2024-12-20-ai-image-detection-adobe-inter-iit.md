---
layout: post
title: "Detecting AI-Generated Images at 32x32: Our Adobe Challenge at Inter-IIT 13.0"
date: 2024-12-20
description: "LeViT plus Neighboring Pixel Relationships for detection, and a zero-shot VLM for explaining artifacts."
tags: [deepfake detection, LeViT, NPR, vision-language models]
categories: project-writeups
related_posts: false
toc:
  sidebar: left
---

Inter-IIT Tech Meet 13.0 at IIT Bombay included a computer-vision problem statement from Adobe Research on detecting AI-generated images and explaining the decision. Our team (Team 64) earned a Silver Medal. This is the story of how the detector came together. The summary lives on the [project page]({{ '/projects/ai-image-detection/' | relative_url }}) and the code at [the repository](https://github.com/ShreyansJain04/AI-Image-Detection-Artifact-Identification).

## The two tasks

1. **Detection.** Classify images from a dataset of 32x32 pixels as real or AI-generated. Fakes came from various GANs, diffusion models and Adobe Firefly. CIFAKE was provided, with a ResNet50 baseline in the problem statement.
2. **Explanation.** For images flagged as fake, identify artifacts and give a short description.

The 32x32 resolution is a double-edged sword. It makes models small and cheap, but it blurs exactly the details (textures, lighting, boundaries) that you would normally use to spot a fake.

## Picking the architecture

We first benchmarked families on CIFAKE (60,000 images, 50,000 train and 10,000 test): LeViT, a hybrid of convolutions and transformer attention designed for fast inference, and EfficientNet, a compound-scaled CNN. We also plotted parameters against inference time to keep the model practical.

{% include figure.html path="assets/img/projects/ai-image-detection/infer.png" class="img-fluid rounded z-depth-1" zoomable=true caption="Parameter count versus inference time across candidates." %}

Plain LeViT-192 scored 95.87%, below LeViT-128 (97.14%) and EfficientNet-b0 (98.47%). The model was not the whole story, so the next gains had to come from features and data.

{% include figure.html path="assets/img/projects/ai-image-detection/levit.png" class="img-fluid rounded z-depth-1" zoomable=true caption="LeViT-192." %}

## Neighboring Pixel Relationships

Generators build images through up-sampling operators, which leave local correlations between neighbouring pixels. Neighboring Pixel Relationships (NPR) represent exactly that. They work in the spatial domain, as opposed to frequency-based detectors, and the NPR paper reports generalisation across 28 generator models with an 11.6% margin over earlier methods. Feeding NPR features to the classifier was the single most useful change: LeViT-128 + NPR reached 98.88%.

{% include figure.html path="assets/img/projects/ai-image-detection/npr1.png" class="img-fluid rounded z-depth-1" zoomable=true caption="NPR heatmaps and the real-versus-fake difference." %}

## Training recipe

Two stages. First, pretrain LeViT-192 to separate real from fake on 4 million images subsampled from GenImage, resized to 32x32 and spanning ImageNet-1K classes across generators. Second, fine-tune on CIFAKE, whose classes match CIFAR-10, which is what the final evaluation used.

Robustness mattered because real images get compressed, blurred and noisy. We augmented with compression, blur, and frequency noise made by perturbing Fourier components. We also used focal loss to concentrate on hard examples:

$$
\mathrm{FL}(p_t) = -\alpha (1 - p_t)^\gamma \log(p_t) + 0.6 \cdot \mathrm{BCE}, \quad p_t = e^{-\mathrm{BCE}}
$$

We ran a statistical test of how each perturbation changes image features. Frequency noise moved frequency-domain features such as mean frequency; blur moved local binary pattern (LBP) texture features; plain moments like mean, standard deviation, skewness and kurtosis barely changed. The two perturbations hit different parts of the representation, so using both made sense.

{% include figure.html path="assets/img/projects/ai-image-detection/p_values.jpg" class="img-fluid rounded z-depth-1" zoomable=true caption="P-values of features under frequency noise and blur." %}

## Results

| Model | Accuracy (%) | F1 |
|---|---|---|
| LeViT_192 | 95.87 | 0.9586 |
| LeViT_192 + Aug | 98.17 | 0.9817 |
| LeViT_128 + NPR | 98.88 | 0.98 |
| LeViT_192 + NPR + Aug + Frequency Noise | **99.21** | **0.9869** |

The final combination reached 99.21% on CIFAKE. The lesson was that each piece (representation, augmentation, pretraining at scale) added a bit, and none was sufficient alone.

## Explaining the fakes without labels

No dataset provides artifact labels, so we could not train an explainer. Instead, we used the **Ovis 1.6 Gemma2-9B** vision-language model zero-shot. The input is only images the detector flagged. A single prompt lists the artifacts to look for, such as inconsistent object boundaries, texture bleeding, unrealistic reflections, conflicting light sources and aliasing on high-contrast edges, and asks for a structured reply of artifact names with explanations.

{% include figure.html path="assets/img/projects/ai-image-detection/ovis.png" class="img-fluid rounded z-depth-1" zoomable=true caption="Ovis architecture." %}

Typical outputs flagged "texture bleeding between adjacent regions", "artificial noise patterns in uniform surfaces", blurred airplane edges and distorted window reflections. These are plausible but unverified: there is no ground truth, and some of these artifacts also occur naturally, so false positives are likely.

## What did not work or remained open

- Resolution: at 32x32 subtle artifacts are invisible; high resolution would need much more compute and likely a stronger classifier.
- Dataset dependence: performance leans on the diversity of the training generators.
- After the competition, we continued with Adobe Research on out-of-distribution generalisation, looking at adversarial training, jigsaw-style self-supervised learning and continual learning.

For the compact version, see the [project page]({{ '/projects/ai-image-detection/' | relative_url }}).
