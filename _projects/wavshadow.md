---
layout: page
title: "WavShadow: Wavelet Based Shadow Segmentation and Removal"
description: "ShadowFormer + MAE priors, FFC blocks, Haar wavelets and a SAM Adapter: state-of-the-art shadow removal on DESOBA (ICVGIP 2024)."
img: assets/img/projects/wavshadow/thumb.jpg
importance: "5"
category: "Research"
advisor: "Prof. Shanmuganathan Raman, IITGN"
status: "ICVGIP 2024"
period: "Feb 2024 – Nov 2024"
team: "Shreyans Jain, Viraj Vekaria, Karan Gandhi, Aadya Arora (equal contribution)"
links:
  blog: /blog/2024/wavshadow-shadow-removal/
  paper: https://arxiv.org/abs/2411.05747
tags: [computer-vision, shadow-removal, wavelets, masked-autoencoder, segmentation]
highlights:
  - "End-to-end shadow segmentation and removal: Haar-wavelet features with a SAM adapter for masks, FFC blocks with MAE priors for removal."
  - "State-of-the-art 1.38 BER on ISTD; 36.7 PSNR on DESOBA (+0.7 over the 2023 state of the art)."
  - "First author (equal contribution), published at ICVGIP 2024."
---

<div class="tldr" markdown="1">
**Problem.** Shadow segmentation and removal are hard in complex real-world scenes, and existing removal models converge slowly.  
**Approach.** Improve ShadowFormer with Masked Autoencoder (MAE) priors trained on Places2 and Fast Fourier Convolution (FFC) blocks, add Haar wavelet features for edges and multi-scale analysis, and use a modified SAM Adapter for segmentation.  
**Result.** State-of-the-art results on the DESOBA dataset with faster convergence and better removal quality. Accepted at ICVGIP 2024.
</div>

## Overview

WavShadow is a two-part pipeline for shadow segmentation and removal, developed by four equally contributing authors at IIT Gandhinagar. The paper appeared at the Indian Conference on Computer Vision, Graphics and Image Processing (ICVGIP), December 2024, Bengaluru.

## Method

The system has three ideas, each tackling a distinct weakness.

1. **MAE priors.** A masked autoencoder trained on Places2 gives the removal model contextual understanding of what the scene should look like without the shadow. In the pipeline it produces a prior image $$I'$$ from the input $$I$$.
2. **Haar wavelets plus FFC.** Wavelet features sharpen edge detection and give multi-scale analysis (shadow boundaries are edges); FFC blocks provide global receptive fields, which together speed up convergence.
3. **Modified SAM Adapter.** The Segment Anything adapter, fed with wavelet features, predicts shadow masks. The masks then guide the MAE-based removal (MAE-FAR) stage to produce the final shadow-free image.

{% include figure.html path="assets/img/projects/wavshadow/arch.jpg" class="img-fluid rounded z-depth-1" zoomable=true caption="WavShadow overview: wavelets and the input image feed the SAM Adapter to produce masks; an MAE produces a prior image I'; MAE-FAR combines the masks and prior into the final output." %}

## Results

Experiments are on DESOBA, a challenging shadow dataset. The qualitative panel shows ground-truth and predicted masks and de-shadowed images side by side; predicted masks follow ground truth closely and the removed regions blend into the surrounding texture.

{% include figure.html path="assets/img/projects/wavshadow/results.png" class="img-fluid rounded z-depth-1" zoomable=true caption="Qualitative results on DESOBA: shadowed input, ground-truth mask, our mask, ground-truth de-shadowed image, our de-shadowed image." %}

**Segmentation:** the SAM backbone with wavelet features reaches a balanced error rate (BER) of **1.38 on ISTD**, which is state of the art.  
**Removal:** **36.7 PSNR on DESOBA**, +0.7 PSNR over the 2023 state of the art.

Whole-image removal results from the paper (SF = ShadowFormer backbone; higher PSNR/SSIM and lower RMSE are better):

| Method | Dataset | PSNR ↑ | SSIM ↑ | RMSE ↓ |
|---|---|---|---|---|
| ShadowFormer (L) | ISTD | 30.58 | 0.934 | 4.82 |
| MAE + SF (ours) | ISTD | 30.45 | 0.932 | **4.81** |
| ShadowFormer (L) | DESOBA | 36.29 | 0.972 | 0.963 |
| MAE + FFC + SF (ours) | DESOBA | **36.67** | **0.972** | **0.753** |

On DESOBA, adding MAE priors and FFC features improves every whole-image metric over the ShadowFormer baseline, cutting RMSE by about 22%. Per-region tables (shadow and non-shadow) are in the [paper](https://arxiv.org/abs/2411.05747).

## My role

- First author; all four authors (with Viraj Vekaria, Karan Gandhi and Aadya Arora) contributed equally.
