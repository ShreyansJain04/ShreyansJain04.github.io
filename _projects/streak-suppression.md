---
layout: page
title: "Real-Time Streak Artifact Suppression in Therapy-Guidance Ultrasound"
description: "Two-stage U-Net + Fourier-attention pipeline removes streak artifacts from HIFU/histotripsy B-mode at >440 FPS, +13.7 dB reconstruction."
img: assets/img/projects/streak-suppression/thumb.jpg
importance: "3"
category: "Research"
advisor: "Prof. Himanshu Shekhar, MUSE Lab, IITGN"
status: "IEEE SAUS 2024 · ISTU 2024 · Patent"
period: "Dec 2023 – Jul 2024"
team: "Shreyans Jain, Mihir Agarwal, Ruchika Dhawan, Nishita Mistry, Himanshu Shekhar"
links:
  code: https://github.com/agarwal-mihir/Fourier-StreakNet
  poster: /assets/pdf/streak_poster_saus2024.pdf
  blog: /blog/2024/realtime-streak-suppression-ultrasound/
tags: [ultrasound, HIFU, artifact-removal, U-Net, fourier, inpainting]
highlights:
  - "Designed a two-stage framework: multi-channel U-Net for streak segmentation, then a Fourier-attention U-Net for inpainting."
  - "Real-time inference at >440 FPS with +13.7 dB reconstruction gain on synthetic streak data generated with Gaussian intensity modulation."
  - "Presented at IEEE SAUS 2024 and ISTU 2024 (Taipei)."
---

<div class="tldr" markdown="1">
**Problem.** When an imaging probe runs during focused-ultrasound therapy (HIFU, histotripsy), interference from the therapy field paints bright streaks across the B-mode image, hiding exactly what the clinician needs to watch.  
**Approach.** A two-stage pipeline: a multi-channel U-Net segments the streaks, and a Fourier-attention U-Net inpaints the masked regions. Training data comes from synthetic streaks with Gaussian intensity modulation across several ultrasound domains.  
**Result.** Real-time inference at more than 440 FPS and a +13.7 dB gain in reconstruction quality (CV figures). Presented at ISTU 2024 and the IEEE South Asian Ultrasonics Symposium (SAUS) 2024.
</div>

## Overview

Therapeutic ultrasound is guided by B-mode imaging, but the therapy pulses interfere with the imaging field and leave vertical streak artifacts. Guidance needs to be live, so the method has to keep up with the imaging frame rate. I worked on this at the MUSE Lab (IIT Gandhinagar) with Prof. Himanshu Shekhar, together with Mihir Agarwal, Ruchika Dhawan and Nishita Mistry.

## Method

**Why two stages.** Splitting the problem gives each network a narrow job. Stage one produces a binary streak mask; stage two only has to fill in the masked regions using the surrounding context.

1. **Segmentation.** A multi-channel U-Net detects streak locations (the repository also includes a variant with a frequency-domain notch filter).
2. **Restoration.** A U-Net with Fourier attention layers uses frequency-domain information, where periodic and vertical structure is easy to separate, to inpaint the masked regions.

**Synthetic data.** Real streaked images with clean ground truth are scarce. We isolated streak-free frames, added random streaks with heuristic generators (Gaussian intensity modulation), extracted the exact mask for U-Net training, and split into train and validation sets. The same generator was used across several ultrasound domains to improve generalization.

{% include figure.html path="assets/img/projects/streak-suppression/unnamed_1.png" class="img-fluid rounded z-depth-1" zoomable=true caption="Synthetic data pipeline: isolate clean frames, augment, add random streaks, extract the mask, split train/validation." %}

**Earlier variant.** The first version (SAUS 2024) paired a U-Net with a diffusion model for inpainting. Initial findings were an SNR improvement of 6.0 +/- 3.4 dB and IoU 0.698, with fast convergence suggesting real-time potential.

## Results

<div class="row">
  <div class="col-sm mt-3 mt-md-0">{% include figure.html path="assets/img/projects/streak-suppression/image.png" class="img-fluid rounded z-depth-1" zoomable=true caption="Input with streaks, predicted streak mask, and restored output." %}</div>
</div>

| Quantity | Value | Source |
|---|---|---|
| Inference speed (two-stage pipeline) | more than 440 FPS | CV |
| Reconstruction improvement | +13.7 dB | CV |
| Streak segmentation IoU (initial U-Net + diffusion study) | 0.698 | SAUS 2024 abstract |

## My role

- Designed and implemented the two-stage framework (multi-channel U-Net segmentation, Fourier-attention U-Net inpainting).
- Built the synthetic streak generator (Gaussian intensity modulation) and the training data pipeline.
- First author on the ISTU 2024 abstract (Taipei) and co-author on the SAUS 2024 paper; poster linked above.
- Equal first inventor on the published Indian patent *A Real-Time Ultrasound Image Processing System and a Method Thereof* (Application No. 202621026094, published Apr 2026).

Code: [Fourier-StreakNet](https://github.com/agarwal-mihir/Fourier-StreakNet). Write-up: [Building a real-time two-stage streak suppressor]({{ '/blog/2024/realtime-streak-suppression-ultrasound/' | relative_url }}).
