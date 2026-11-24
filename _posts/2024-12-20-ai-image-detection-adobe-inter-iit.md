---
layout: post
title: "Detecting AI-Generated Images at 32x32: Our Adobe Challenge at Inter-IIT 13.0"
date: 2024-12-20
description: "How LeViT, Neighboring Pixel Relationships and frequency-noise augmentation reached 99.21% on CIFAKE, and an honest look at what a zero-shot VLM's artifact explanations were really worth."
tags: [deepfake detection, LeViT, NPR, vision-language models]
categories: project-writeups
related_posts: false
toc:
  sidebar: left
---

Inter-IIT Tech Meet 13.0, held at IIT Bombay, included a computer-vision problem statement from **Adobe Research**: detect AI-generated images, then explain *why* an image looks fake. I led our team (Team 64, IIT Gandhinagar), which I put together from the ML Club, and we won a **Silver Medal** with the highest detection accuracy among all IITs. This post goes through what we built, why each piece was there, and, with some hindsight, which parts held up.

The short version is on the [project page]({{ '/projects/ai-image-detection/' | relative_url }}), and the code is [on GitHub](https://github.com/ShreyansJain04/AI-Image-Detection-Artifact-Identification).

## The two tasks, and the catch

1. **Detection.** Classify **32×32** images as real or AI-generated. The fakes came from several GANs, diffusion models and Adobe Firefly. CIFAKE was provided for development, with a ResNet-50 baseline in the problem statement.
2. **Explanation.** For each image flagged as fake, name the artifacts that give it away and describe them briefly.

The catch is the resolution. At 32×32 an image is 1,024 pixels. Most of the cues people use to spot a fake (garbled text, odd hands, inconsistent reflections) simply aren't visible. That pushed us towards signals that survive at tiny sizes, and it's also why the explanation task turned out to be much harder than it looked.

## Detection: three ideas that stacked

### 1. A small, fast backbone

We benchmarked two model families on CIFAKE (50,000 training and 10,000 test images):

- **LeViT**, a hybrid that uses convolutions early to shrink the image, then transformer attention on the smaller feature maps. It's built for fast inference.
- **EfficientNet**, a CNN that scales depth, width and resolution together.

We also plotted parameter count against inference time, because a detector is only useful if it's cheap to run on every uploaded image.

{% include figure.html path="assets/img/projects/ai-image-detection/infer.png" class="img-fluid rounded z-depth-1" zoomable=true caption="Parameter count versus inference time across the candidates." %}

On their own, the backbones were close. EfficientNet-B0 led at 98.47%, LeViT-128 scored 97.14%, and the bigger LeViT-192 actually did *worse* at 95.87%. A larger model didn't help on 32×32 inputs, so the gains had to come from what we fed the model and how we trained it.

{% include figure.html path="assets/img/projects/ai-image-detection/levit.png" class="img-fluid rounded z-depth-1" zoomable=true caption="LeViT-192: convolutional stem, then attention stages that shrink the feature map step by step." %}

### 2. Looking where generators leave fingerprints: NPR

Almost every image generator, GAN or diffusion, builds its output by **up-sampling**: it produces a small feature map and repeatedly enlarges it. Up-sampling copies or interpolates values, so neighbouring output pixels end up more correlated than they would be in a real photo. That correlation is a fingerprint.

**Neighboring Pixel Relationships (NPR)**, from Tan et al. (CVPR 2024), turns that into a feature. Shrink the image by 2× and enlarge it back with nearest-neighbour interpolation, then take the difference:

$$\mathrm{NPR}(x) = x - \mathrm{up}_{2\times}\!\big(\mathrm{down}_{2\times}(x)\big)$$

Within each 2×2 block, this measures how each pixel differs from its block's reference pixel. Natural images and up-sampled images have different statistics here. Because NPR works in the pixel domain, not the frequency domain, it generalises across generators well: the original paper reports results on images from 28 different generators, beating earlier methods by 11.6%.

Here is NPR computed on two of the images our model flagged as fake:

{% include figure.html path="assets/img/blog/ai-image-detection/npr-examples.png" class="img-fluid rounded z-depth-1" zoomable=true caption="Two 32×32 images flagged as AI-generated, and the magnitude of their NPR maps. Even at this size, the residual concentrates on object structure and texture, not on the flat sky or background." %}

{% include figure.html path="assets/img/projects/ai-image-detection/npr1.png" class="img-fluid rounded z-depth-1" zoomable=true caption="From our report: per-channel NPR heatmaps and the difference between real and fake NPR maps." %}

Feeding NPR into the classifier was the single biggest jump: LeViT-128 went from 97.14% to **98.88%**.

### 3. Pretraining at scale, then robustness

Accuracy on clean CIFAKE isn't the real goal. Real images get compressed, resized and blurred, and the hidden test set could include generators we hadn't seen. So we did three things:

- **Pretrain on GenImage.** We pretrained LeViT-192 for real-versus-fake on **4 million images** subsampled from GenImage, resized to 32×32 and covering the ImageNet-1K classes across many generators. Then we fine-tuned on CIFAKE, whose classes match the CIFAR-10 evaluation set.
- **Augment like the real world.** JPEG compression and blur, plus **frequency noise**: small random perturbations to the image's Fourier components, simulating the high-frequency changes that resampling and re-encoding cause.
- **Focal loss.** This down-weights examples the model already gets right and concentrates training on hard ones:

$$
\mathrm{FL}(p_t) = -\alpha (1 - p_t)^\gamma \log(p_t) + 0.6 \cdot \mathrm{BCE}, \qquad p_t = e^{-\mathrm{BCE}}
$$

Were blur and frequency noise really different augmentations, or two names for the same thing? We checked statistically by measuring how each one shifts a set of hand-crafted image features. **Frequency noise** significantly moved frequency-domain features such as mean frequency. **Blur** moved texture features: local binary pattern (LBP) histograms. Global statistics (mean, standard deviation, skewness, kurtosis) barely changed under either. So the two perturbations stress different parts of the representation, which is why we used both.

{% include figure.html path="assets/img/projects/ai-image-detection/p_values.jpg" class="img-fluid rounded z-depth-1" zoomable=true caption="P-values for the change in each image feature under frequency noise and blur. Low values mean the perturbation significantly shifts that feature." %}

### Results

| Model | Accuracy (%) | Precision | Recall | F1 |
|---|---|---|---|---|
| EfficientNet-v2-S (from scratch) | 96.39 | 0.966 | 0.961 | 0.964 |
| LeViT-128s | 96.99 | 0.971 | 0.969 | 0.970 |
| LeViT-128 | 97.14 | 0.982 | 0.961 | 0.971 |
| LeViT-192 | 95.87 | 0.960 | 0.957 | 0.959 |
| LeViT-128 + aug | 98.08 | 0.983 | 0.979 | 0.981 |
| LeViT-192 + aug | 98.17 | 0.981 | 0.983 | 0.982 |
| EfficientNet-B0 | 98.47 | 0.984 | 0.985 | 0.985 |
| LeViT-128 + NPR | 98.88 | 0.986 | 0.987 | 0.980 |
| **LeViT-192 + NPR + aug + frequency noise** | **99.21** | **0.992** | 0.982 | **0.987** |

Two things stand out. Augmentation alone helped the larger LeViT-192 most (95.87% → 98.17%): the bigger model had been overfitting, and robustness training gave it something useful to learn. And no single idea was enough. NPR, pretraining and augmentation each added roughly half to one point, and the final model is the one that combined them all.

## Explanation: what the vision-language model actually did

### The setup

No dataset pairs fake images with labelled artifacts, so we couldn't train an explainer. We used **Ovis 1.6 (Gemma2-9B)**, an open vision-language model, zero-shot. Every image the detector flagged was sent to Ovis with one prompt listing candidate artifacts by category (anatomy, texture, lighting, geometry, mechanical parts and so on), asking for a structured reply of `{artifact: explanation}`.

{% include figure.html path="assets/img/projects/ai-image-detection/ovis.png" class="img-fluid rounded z-depth-1" zoomable=true caption="Ovis structurally aligns visual and text embeddings: image patches are mapped to probabilistic 'visual words' from an embedding table, like text tokens." %}

The outputs read well. For the airplane above, Ovis said the edges were "blurred, lacking clear definition" and the window reflections were "not natural". For the cat, it pointed to "texture bleeding between adjacent regions". We put examples like these in our final report.

### Looking back: auditing all 94 explanations

Reading the full output file again for this post, I counted what the model actually returned across all **94** flagged images:

- It reported an average of **37 artifacts per image**, with a minimum of 9 and a maximum of 62. For a 1,024-pixel image, that isn't a diagnosis, it's a checklist.
- **"Unrealistic specular highlights"** was reported for **every single image**, including ones with no shiny surfaces.
- In **9% of explanations** (317 of 3,466), the model contradicted itself, saying an artifact was present while stating its subject wasn't. Real examples: *"Metallic surface artifacts: there are no metallic surfaces, but the artifacts suggest a digital manipulation"*, and "incorrect wheel geometry" or "misaligned body panels" on images with no vehicle.

{% include figure.html path="assets/img/blog/ai-image-detection/artifact-frequency.png" class="img-fluid rounded z-depth-1" zoomable=true caption="How often each artifact was reported across the 94 flagged images. The model reports most of the prompt's list on most images, whatever they show." %}

The pattern is clear: **when a prompt lists candidate artifacts, the VLM tends to confirm the list instead of checking it.** At 32×32 there's very little visual evidence to anchor it, so it fills the gap with plausible-sounding text. The explanations sounded right, but they weren't evidence.

### What I'd do instead

- **Ask for absence explicitly.** Ask about one artifact at a time, with "not present" as an equally valid answer, and score the model's confidence.
- **Ground explanations in the detector.** Use attribution maps from the classifier, or NPR residual maps like the ones above, to show *where* the evidence is, then ask the VLM to describe only those regions.
- **Upscale before explaining.** A super-resolved view gives the VLM more to work with, though it adds its own artifacts.
- **Build a small labelled set.** Even a few hundred images with human-marked artifacts would let you measure explanation precision instead of guessing it.

## What remained open

- **Resolution.** At 32×32, subtle artifacts are invisible. Working at full resolution would need much more compute and probably a stronger detector.
- **Generator coverage.** Accuracy depends on how varied the training generators are. Generalising to unseen generators is the hard problem.
- **Continuing with Adobe.** After the competition we continued working with Adobe Research on out-of-distribution generalisation, exploring adversarial training, jigsaw-style self-supervised learning and continual learning.

## Takeaway

The detection side taught me that, at tiny resolutions, the right *representation* matters more than model size. NPR targets the one fingerprint every up-sampling generator leaves, and it beat simply scaling the backbone. The explanation side taught me something more uncomfortable: a fluent explanation is not a correct one. If I did it again, I would measure the explainer as carefully as the detector.
