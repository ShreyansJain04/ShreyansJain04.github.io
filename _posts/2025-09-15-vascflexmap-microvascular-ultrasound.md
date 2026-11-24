---
layout: post
title: "Mapping Blood Vessels from a Few Hundred Ultrasound Frames"
date: 2025-09-15
description: "VascFlexMap: skipping microbubble localization entirely, and mapping brain microvasculature from sparse 2–50 FPS ultrasound with up to 500x less data than ULM."
tags: [ultrasound, super-resolution, ULM, transformers, medical-imaging]
categories: project-writeups
related_posts: false
toc:
  sidebar: left
---
<!-- Date approximate: manuscript in preparation, no public preprint. Numbers taken from the project page / manuscript figures. -->

Ultrasound is cheap, portable and safe, but it's blurry. Its resolution is limited by diffraction to roughly half a wavelength, a few hundred microns at clinical frequencies, so the smallest vessels in an organ simply blur together. **Ultrasound localization microscopy (ULM)** gets round this, and resolves vessels below 50 µm. But it asks for things a normal scanner can't give.

This post is about **VascFlexMap**, a deep-learning method we've been developing at the MUSE Lab, IIT Gandhinagar (Prof. Himanshu Shekhar), with Ruchika Dhawan and Mihir Agarwal as equal-contribution first authors. The idea is to give up some of ULM's resolution in exchange for working from the kind of sparse, slow data a clinical scanner can actually collect.

## How ULM beats diffraction, and what it costs

ULM borrows its trick from optical super-resolution microscopy (PALM/STORM). You inject **microbubbles**, tiny gas-filled contrast agents that flow through the blood. Each bubble is far smaller than the ultrasound resolution, so it appears as a blurry spot. But if the bubbles are sparse enough that spots don't overlap, you can find the *centre* of each spot far more precisely than its width. Record many frames, localize every bubble in every frame, track them from frame to frame, and add up all the tracks. The result is a map of where blood flows, at a resolution set by localization precision rather than diffraction.

The catch is in "many frames":

- **Ultrafast imaging.** Tracking needs bubbles to move only a little between frames, so ULM runs at about **1,000 frames per second**, using plane-wave imaging that most clinical machines don't offer.
- **Lots of data.** Because bubbles must be sparse, each frame contributes only a few localizations. Filling in a vessel tree takes **tens of thousands of frames**: 170,400 in the rat-brain dataset we used.
- **Slow processing.** Localization and tracking over that much data can take hours.

For many clinical questions (is this tissue perfused? where do the main branches run?) the network's *topology* matters more than capillary-level detail. That's the gap VascFlexMap targets.

## The earlier step: a U-Net on sparse data

The project grew out of work we presented at **ISTU 2024**: a hybrid attention-based U-Net that reconstructs super-resolved vessel maps from sparse data. On simulated vessels, it cut the data needed by about **40×** and improved peak SNR by **14.73 dB** over ULM run on the same sparse data.

{% include figure.html path="assets/img/projects/ulm-super-resolution/simulation.png" class="img-fluid rounded z-depth-1" zoomable=true caption="The simulated case that motivated the work. Full ULM (left) traces the vessels. ULM on subsampled data (middle) collapses to a few isolated points. A learned model on the same subsampled data (right) recovers the vessel paths." %}

The middle panel shows the core problem. With too few frames, ULM has no tracks to accumulate, so it doesn't degrade gracefully: it falls apart. A learned model, though, can use a prior about what vessel networks look like. VascFlexMap takes that idea to real in-vivo data.

## VascFlexMap: skip localization altogether

Instead of finding bubbles and then drawing tracks, VascFlexMap maps a sparse sequence of frames **directly** to a vessel probability map.

{% include figure.html path="assets/img/projects/ulm-super-resolution/flowchart_5boxes.png" class="img-fluid rounded z-depth-1" zoomable=true caption="Pipeline: 1000 Hz B-mode data is subsampled to 2–50 Hz, cleaned with SVD clutter filtering and a band-pass filter, passed through VascFlexMap, then post-processed and upscaled." %}

### Simulating a slow scanner

We used the public **PALA** rat-brain bolus dataset, recorded at 1,000 FPS. To simulate slower scanners, we kept every N-th frame of each 800-frame block, giving effective rates of 50, 25, 15, 5, 3 and 2 FPS. Tissue signal is removed with **SVD clutter filtering**: tissue moves slowly and coherently, so it lives in the first few singular vectors of the frame stack, while moving bubbles don't. A second-order Butterworth band-pass then removes what's left, and frames are resized to 256 × 256.

### Learning a prior over vessel shapes

The most unusual design choice is in training. The network is trained with **Gaussian-noise tensors as input**, paired with full-data ULM vessel maps as targets. It doesn't learn to read particular features from noisy frames; it learns a strong *prior* over what plausible vessel maps look like. We think this makes it less sensitive to things that change between scans (gain, attenuation, bubble concentration), and it converges in just **2 epochs**.

### The architecture

{% include figure.html path="assets/img/projects/ulm-super-resolution/model_architecture.png" class="img-fluid rounded z-depth-1" zoomable=true caption="VascFlexMap: a linear projection compresses each frame, a temporal transformer encoder models how the sequence changes over time, and a transposed-convolution decoder produces the vessel map." %}

- Each frame's feature tensor (256 × 32 × 32, so 262,144 values) is **linearly projected to 128 dimensions**, so each frame becomes one token.
- A **3-layer, single-head transformer encoder** with sinusoidal positional encodings attends across the sequence. This is where information from many sparse frames is combined, much as ULM accumulates tracks over time.
- A second projection restores the spatial tensor, and **three transposed-convolution stages** (256 → 128 → 64 → 32 channels) with a sigmoid output produce a 256 × 256 probability map.
- Training uses binary cross-entropy and Adam at a learning rate of 3 × 10⁻⁴.

### Cleaning up the output

The raw probability map is then enhanced: total-variation denoising, contrast-limited adaptive histogram equalisation (CLAHE), unsharp masking and a small erosion to thin the vessels, followed by 32× upscaling for display.

{% include figure.html path="assets/img/projects/ulm-super-resolution/preandpostprocessedimages25fps4260frames.png" class="img-fluid rounded z-depth-1" zoomable=true caption="Raw network output (left) and after post-processing (right), at 25 FPS from 4,260 frames. Post-processing sharpens the branches and suppresses the diffuse background." %}

## Results

### How low can the frame rate go?

{% include figure.html path="assets/img/projects/ulm-super-resolution/lines5onallthefigures.png" class="img-fluid rounded z-depth-1" zoomable=true caption="Frame-rate ablation. Top: conventional ULM at 1,000 FPS. Below: VascFlexMap at 50, 25 and 15 FPS, and at 5, 3 and 2 FPS. White lines mark the five vessels used to measure width." %}

The main cortical branches and the larger microvessels stay visible **all the way down to 2 FPS**. Finer capillaries blur as the frame rate drops. Conventional ULM run on the same sparse data doesn't produce a continuous network at all.

At 2 FPS the reconstruction uses **341 frames**, against **170,400** for the full ULM map: about a **500× reduction in data**.

### The resolution cost

We measured vessel width as full width at half maximum (−3 dB) across five vessels:

| Method | Vessel width, µm (mean ± std) |
|---|---|
| Conventional ULM (1,000 FPS) | 34.9 ± 30.5 |
| VascFlexMap, 50 FPS | 108.8 ± 43.3 |
| VascFlexMap, 25 FPS | 115.0 ± 35.9 |
| VascFlexMap, 15 FPS | 127.3 ± 24.7 |
| VascFlexMap, 2 FPS | 110.9 ± 15.2 |

Vessels come out about **3× wider** than in ULM. That's the honest price of working from so little data. Interestingly, width barely depends on frame rate between 50 and 2 FPS, and the spread actually narrows at 2 FPS. This fits the idea that the network leans on its learned vessel prior: fewer frames make the map less detailed, not less consistent.

### How many frames do you need?

We also varied *how many* of the final frames are used, at a fixed frame rate.

<div class="row">
  <div class="col-sm mt-3 mt-md-0">{% include figure.html path="assets/img/projects/ulm-super-resolution/comparisonofdifffps.png" class="img-fluid rounded z-depth-1" zoomable=true caption="Using only the last N frames, at 25 FPS (top) and 5 FPS (bottom). The vessel tree is readable with a few hundred frames." %}</div>
  <div class="col-sm mt-3 mt-md-0">{% include figure.html path="assets/img/projects/ulm-super-resolution/timing_plot.png" class="img-fluid rounded z-depth-1" zoomable=true caption="Reconstruction time grows roughly linearly with frame count: about 28 s for 200 frames up to 133 s for 4,260 frames on an NVIDIA H100." %}</div>
</div>

Informative maps appear with roughly **200 to 2,200** final frames, and end-to-end reconstruction takes **28 to 133 seconds** on one GPU. That's minutes instead of hours, from data a standard scanner could record.

## Where it fits, and its limits

I think of VascFlexMap as a **first look**, not a replacement for ULM. A quick, low-resolution perfusion map can show whether perfusion is present, where the main branches are, and where a slow, high-fidelity ULM scan would be worth doing.

The limitations are real:

- **Wider vessels.** About 3–3.6× broader than ULM, so it can't measure capillary sizes.
- **No flow information.** The output is a static probability map. ULM's tracks also give flow speed and direction; this doesn't.
- **Motion-free data only.** PALA comes from an anaesthetised, fixed rat brain. Breathing and heartbeat motion in a patient are an open question.
- **A strong prior cuts both ways.** Training on noise inputs makes the network robust, but it also means it could draw "typical" vessels where the data are weak. Testing on unusual vascular anatomy, such as tumours, is an important next step.

## Takeaway

ULM's insight is that you can beat the resolution limit by accumulating many sparse observations. VascFlexMap asks how far a learned prior can stand in for some of those observations. On this data, the answer is: far enough to recover the vessel tree from 2 FPS and a few hundred frames, as long as you accept vessels about three times wider. For a clinical scanner that can't do 1,000 FPS, that's a trade worth having.

This line of work is also covered by an Indian patent on which I'm an equal first inventor: *A System and Method for Super-Resolution Ultrasound Reconstruction with Representation Learning on Sparse Data* (Application No. 202521001823, filed January 2025, published February 2026).

**Links:** [Project page](/projects/vascflexmap/) · Manuscript in preparation
