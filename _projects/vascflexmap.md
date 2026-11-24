---
layout: page
title: "VascFlexMap: Microvascular Ultrasound Imaging at Low Frame Rates Using Sparse Data and a Transformer-Decoder Network"
description: "Transformer-decoder maps microvessels from 2-50 FPS contrast ultrasound: up to 500x less data, 28-133 s reconstruction on one H100."
img: assets/img/projects/ulm-super-resolution/thumb.jpg
importance: "4"
category: "Research"
advisor: "Prof. Himanshu Shekhar, MUSE Lab, IITGN"
status: "Manuscript · ISTU 2024"
period: "2024 - 2025"
team: "Ruchika Dhawan, Mihir Agarwal, Shreyans Jain, Himanshu Shekhar"
tags: [ultrasound, super-resolution, ULM, transformer, microvasculature, sparse-data]
highlights:
  - "Transformer-decoder network that maps microvessels from contrast ultrasound acquired at only 2–50 FPS."
  - "Up to 500× less data than conventional ultrasound localization microscopy, with 28–133 s reconstruction on one H100."
  - "Earlier hybrid attention U-Net version presented at ISTU 2024 (40× data reduction, +14.73 dB peak SNR in simulation)."
---
<!-- TODO: verify (1) venue/status: manuscript header is formatted for IEEE Trans. Biomed. Eng. 2025 but no submission status is stated; (2) equal contribution is Dhawan and Agarwal per tex; (3) period; (4) earlier hybrid-attention U-Net abstract (ISTU 2024) numbers 40x / 14.73 dB are on simulated data. No code/paper link available in sources. -->

<div class="tldr" markdown="1">
**Problem.** Ultrasound localization microscopy (ULM) resolves vessels below 50 um, but needs ultrafast frame rates (about 1000 FPS), tens of thousands of frames, and hours of processing, which clinical scanners cannot provide.  
**Approach.** Skip bubble localization and tracking. A transformer-decoder network with learned linear projections maps a sparse low-frame-rate (2-50 FPS) contrast-enhanced sequence directly to a vessel probability map, followed by a post-processing enhancement stage.  
**Result.** On in-vivo rat brain bolus data (PALA), vascular topology is recovered with up to 500x data reduction (341 frames at 2 FPS vs. 170,400 frames for ULM). End-to-end reconstruction takes 28-133 s on an NVIDIA H100. The cost is resolution: vessels appear about 3x wider.
</div>

## Overview

Clinical microvascular imaging often needs topology fast (is perfusion present, where are the branches?) more than micron-scale capillary detail. VascFlexMap trades resolution for practicality: it works from data a standard scanner could actually acquire, and returns a map in under a few minutes. The idea is also a "first cut": a quick low-resolution perfusion map can say where a slow, high-fidelity ULM acquisition is worth doing.

The work grew out of an earlier hybrid attention-based U-Net (ISTU 2024), which reported a 40x reduction in data requirements and a peak SNR enhancement of 14.73 dB on simulated data. An intermediate draft (VascFlex Flow) used a hybrid U-Net with a temporal transformer encoder; the version described here is the transformer-decoder VascFlexMap.

## Method

{% include figure.html path="assets/img/projects/ulm-super-resolution/flowchart_5boxes.png" class="img-fluid rounded z-depth-1" zoomable=true caption="Pipeline: 1000 Hz B-mode data is subsampled to 2-50 Hz, cleaned by SVD clutter filtering and a Butterworth band-pass, passed through VascFlexMap, then post-processed and upscaled to 8192 x 8192." %}

- **Sparse input.** Every N-th frame of each 800-frame block is kept to simulate 50, 25, 15, 5, 3 and 2 FPS. SVD clutter suppression and a second-order Butterworth temporal band-pass remove tissue; envelopes are resized to 256 x 256.
- **Unconditional training.** A distinctive choice: the network is trained with Gaussian-noise tensors as input, paired with ground-truth vessel maps from full-data ULM. It therefore learns a vascular prior rather than features of noisy frames, which the paper argues removes sensitivity to gain, attenuation and bubble concentration, and lets it converge in 2 epochs.
- **Architecture.** The input (sequence x 256 x 32 x 32) is flattened to 262,144 dimensions and linearly projected to 128; a 3-layer, single-head transformer encoder with sinusoidal positional encoding models temporal dependencies; a second projection restores the tensor, and three transposed-convolution stages (256, 128, 64, 32 channels) with a sigmoid output give a 256 x 256 probability map. Loss is binary cross-entropy; optimizer Adam at $$3\times10^{-4}$$.
- **Post-processing.** Total-variation denoising, CLAHE, unsharp masking and a small erosion, then 32x upscaling.

{% include figure.html path="assets/img/projects/ulm-super-resolution/model_architecture.png" class="img-fluid rounded z-depth-1" zoomable=true caption="VascFlexMap architecture: linear projection, temporal transformer encoder, transposed-convolution decoder." %}

## Results

{% include figure.html path="assets/img/projects/ulm-super-resolution/lines5onallthefigures.png" class="img-fluid rounded z-depth-1" zoomable=true caption="Frame-rate ablation. Top row: conventional ULM at 1000 FPS. Lower rows: VascFlexMap at 50/25/15 and 5/3/2 FPS. White lines mark the five vessels used for FWHM." %}

Major cortical branches and higher-order microvessels stay visible down to 2 FPS; finer capillaries blur progressively. Conventional ULM applied to the same sparse data fails to give a continuous network.

| Method | -3 dB FWHM (um, mean +/- std, 5 vessels) |
|---|---|
| Conventional ULM | 34.91 +/- 30.46 |
| VascFlexMap, 50 FPS | 108.83 +/- 43.32 |
| VascFlexMap, 25 FPS | 114.99 +/- 35.86 |
| VascFlexMap, 15 FPS | 127.31 +/- 24.73 |
| VascFlexMap, 2 FPS | 110.88 +/- 15.23 |

<div class="row">
  <div class="col-sm mt-3 mt-md-0">{% include figure.html path="assets/img/projects/ulm-super-resolution/fig3_ulm_lastnframes_comparison_3x4.jpg" class="img-fluid rounded z-depth-1" zoomable=true caption="Last-N-frames analysis: informative maps from roughly 200-2200 final frames." %}</div>
  <div class="col-sm mt-3 mt-md-0">{% include figure.html path="assets/img/projects/ulm-super-resolution/timing_plot.png" class="img-fluid rounded z-depth-1" zoomable=true caption="Run time scales roughly linearly with frames: about 28 s (200 frames) to 133 s (4260 frames) on an H100." %}</div>
</div>

**Limitations (from the paper).** About 3-3.6x vessel broadening versus ULM; static probability maps without flow velocity or direction; evaluated on motion-free data, so robustness to respiration and cardiac motion is open.

## My role

- Co-author of the manuscript (equal-contribution first authors are Ruchika Dhawan and Mihir Agarwal).
- Contributed to the ISTU 2024 hybrid attention-based U-Net on sparse ULM data that preceded this work.
- Equal first inventor on a published Indian patent from this line of work: *A System and Method for Super-Resolution Ultrasound Reconstruction with Representation Learning on Sparse Data* (Application No. 202521001823, published Feb 2026).
<!-- TODO: add specific contributions (e.g. preprocessing, experiments, figures) once confirmed. -->
