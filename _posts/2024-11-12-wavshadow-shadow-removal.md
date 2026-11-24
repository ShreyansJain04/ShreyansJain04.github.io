---
layout: post
title: "WavShadow: Teaching a Shadow Remover Where to Look"
date: 2024-11-12
description: "How Haar wavelets, a SAM adapter, masked-autoencoder priors and Fourier convolutions made ShadowFormer converge in about half the epochs on hard real-world shadows (ICVGIP 2024)."
tags: [computer-vision, shadow-removal, wavelets, masked-autoencoder, SAM, transformers]
categories: project-writeups
related_posts: false
toc:
  sidebar: left
---

Removing a shadow from a photo sounds like a brightness fix: find the dark region and lighten it. Anyone who has tried knows it isn't. Shadows have soft edges that fade over many pixels, they fall across textures that must survive the fix, and the region under a shadow has lost information that has to be guessed back. Get the mask slightly wrong and you leave a halo. Get the relighting wrong and you leave a patch that's too flat or the wrong colour.

**WavShadow** is our answer to this, published at ICVGIP 2024. It was a four-person project at IIT Gandhinagar with Viraj Vekaria, Karan Gandhi and Aadya Arora (all equal contribution), advised by Prof. Shanmuganathan Raman. This post explains the design choices and what they bought us.

## Two problems, not one

Shadow removal is really two problems:

1. **Where is the shadow?** A segmentation problem: produce a mask.
2. **What would the scene look like without it?** A restoration problem: relight the masked region so it matches the lit region around it.

Most strong removal models, including ShadowFormer, which we built on, assume a mask is given. In benchmarks that's often the ground-truth mask. Real images don't come with one. So our pipeline produces its own mask first, then removes the shadow using that mask.

{% include figure.html path="assets/img/projects/wavshadow/arch.jpg" class="img-fluid rounded z-depth-1" zoomable=true caption="WavShadow pipeline. Top: a SAM adapter, given wavelet features, predicts the shadow mask. Bottom: a masked autoencoder produces a contextual prior I′, which ShadowFormer (with FFC blocks) uses with the mask to produce the shadow-free image." %}

## Why DESOBA, not just ISTD

The standard benchmark, ISTD, is mostly simple scenes: one shadow cast on a fairly uniform surface. We wanted to test on **DESOBA**, which pairs shadows with the objects that cast them in cluttered real-world scenes: people, poles and bags on grass, pavement and courts. Shadows there cross several textures and overlap with object edges, which is exactly where mask errors and halos show up.

## Part 1: finding the shadow, with wavelets

For segmentation we started from the **Segment Anything Model (SAM)**, which already has a very general sense of "what is an object region". SAM wasn't trained for shadows, so we used a **SAM adapter**: small trainable modules inserted into a frozen SAM that inject task-specific features. Our change was what we fed the adapter: **Haar wavelet features**.

A one-level Haar transform splits an image into four half-resolution bands. Each 2×2 block of pixels $$a, b, c, d$$ becomes:

$$
LL = \tfrac{a+b+c+d}{2}, \quad
LH = \tfrac{a+b-c-d}{2}, \quad
HL = \tfrac{a-b+c-d}{2}, \quad
HH = \tfrac{a-b-c+d}{2}
$$

LL is a blurred copy of the image; LH, HL and HH respond to horizontal, vertical and diagonal changes. Here is that decomposition applied to one of the DESOBA images from our results:

{% include figure.html path="assets/img/blog/wavshadow/haar-bands.png" class="img-fluid rounded z-depth-1" zoomable=true caption="One-level Haar decomposition of a shadowed DESOBA image. The detail bands (right three) light up at the shadow boundary, but also at the tile grid. That's why the wavelet features go into a learned adapter rather than being thresholded directly." %}

We chose Haar for three reasons:

- **It's nearly free.** Additions and subtractions on 2×2 blocks, with no learned parameters.
- **It keeps sharp discontinuities.** Haar's basis functions are step functions, so a hard shadow edge produces a strong, localised response instead of being smeared.
- **It's multi-scale.** Applied repeatedly, it separates coarse brightness changes from fine edges. That helps tell a soft penumbra, which spreads over many pixels, from a hard cast edge.

The figure also shows the catch: wavelets react to *any* edge, including texture. On their own they would make a poor shadow detector. As extra input to a model that already understands regions, they tell it precisely where intensity jumps, and the model works out which jumps are shadow boundaries.

## Part 2: removing it, with priors and global context

ShadowFormer is a transformer-based removal network whose *Shadow-Interaction Module* uses the mask to let shadowed pixels attend to lit pixels with similar context. It's strong but slow to train. We made two changes.

**Masked-autoencoder (MAE) priors.** An MAE is trained to fill in large masked regions of an image. One trained on **Places2**, a big dataset of scenes, has a good sense of what a pavement, a lawn or a wall usually looks like. We give it the shadowed image and our predicted mask and take its output $$I'$$ as a rough guess of the shadow-free scene. That guess is concatenated with the input to ShadowFormer. The removal network no longer starts from nothing inside the shadow: it starts from a plausible reconstruction and refines it.

**Fast Fourier Convolutions (FFC).** Ordinary convolutions see only a small neighbourhood. FFC blocks, popularised by the LaMa inpainting model, add a branch that works in the frequency domain, so each output depends on the whole image. Relighting a shadow correctly needs global context (what's the lighting and colour of the lit part of this surface?), so we put FFC blocks inside ShadowFormer's shadow-interaction module.

## Results

{% include figure.html path="assets/img/projects/wavshadow/results.png" class="img-fluid rounded z-depth-1" zoomable=true caption="DESOBA examples. Columns: shadowed input, ground-truth mask, our predicted mask, ground-truth shadow-free image, our output." %}

The predicted masks follow the ground truth closely, including thin structures like the strap shadow in the first row. The removed shadows blend into the surrounding texture without obvious halos.

Quantitatively (PSNR and SSIM higher is better, RMSE lower is better):

| Model | Dataset | Shadow PSNR | Shadow RMSE | Non-shadow RMSE | All PSNR | All RMSE |
|---|---|---|---|---|---|---|
| ShadowFormer (L) | DESOBA | 37.46 | 13.00 | 0.311 | 36.29 | 0.963 |
| **MAE + FFC + ShadowFormer** | DESOBA | **37.96** | **10.90** | **0.208** | **36.67** | **0.753** |
| MAE + ShadowFormer | DESOBA | 37.14 | 13.55 | 0.208 | 36.67 | 0.886 |
| ShadowFormer (L) | ISTD | 37.07 | 4.82 | 4.42 | 30.58 | 4.82 |
| MAE + FFC + ShadowFormer | ISTD | 36.78 | 7.60 | 4.45 | 30.33 | 4.90 |

Three things stand out:

- **On DESOBA, the full model wins on every metric.** The biggest gain is inside the shadow, where RMSE falls from 13.0 to 10.9 (about 16%). That's the region the MAE prior was meant to help.
- **FFC matters.** MAE alone improves the whole image but not the shadow region. Adding FFC's global context is what fixes the shadow interior.
- **On ISTD it's roughly a tie**, with vanilla ShadowFormer slightly ahead. ISTD's simple scenes leave little for a scene prior or global context to add. That's consistent with our reason for focusing on DESOBA.

The clearest practical win is **training speed**. With the MAE prior and FFC blocks, the removal network converged in about **250 epochs instead of about 450** for the original, a 45% saving in training time, for equal or better quality. Adding wavelet features also made the SAM adapter converge faster and segment better, though we didn't measure that speed-up as precisely. A good prior means the network has less to learn from scratch.

## What I'd do differently

- **Train jointly.** The SAM adapter and the removal network were trained separately, so mask errors aren't corrected by the removal loss. An end-to-end version could learn masks that are best for removal, not just for segmentation.
- **Learn the wavelets.** Haar is a fixed, hand-picked basis. Learnable or multi-level wavelets could separate shadow edges from texture better than the single level we used.
- **Run proper ablations on segmentation.** Our numbers isolate the removal changes well, but the wavelet contribution to mask quality deserves its own metrics, such as balanced error rate.

## Takeaway

None of the parts are exotic: a fixed wavelet transform, a pretrained segmenter, a pretrained inpainter, and a convolution with a global receptive field. The lesson for me was about where to put prior knowledge. Each component handles one thing the base model was weak at (sharp edges, region understanding, scene plausibility, global lighting), and together they make a strong model train faster and do better on the hard cases.

**Links:** [Paper (arXiv)](https://arxiv.org/abs/2411.05747) · [Project page](/projects/wavshadow/)
