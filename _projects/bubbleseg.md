---
layout: page
title: "Improved Segmentation of Histotripsy Bubble Clouds Using Modern CNN Architectures and Combined Dice-Focal Loss"
description: "EfficientNet-B0 U-Net with Dice-Focal loss segments histotripsy ablation in B-mode ultrasound: mean IoU 0.838 with 7.9M parameters."
img: assets/img/projects/bubbleseg/thumb.jpg
importance: "2"
category: "Research"
advisor: "Prof. Himanshu Shekhar (IITGN) & Prof. Kenneth B. Bader (UChicago)"
status: "Manuscript"
team: "Shreyans Jain, Soham Gaonkar, Aditya Borate, Ruchika Dhawan, Kenneth B. Bader, Himanshu Shekhar"
links:
  code: https://github.com/ShreyansJain04/BubbleSegmentation
  blog: /blog/2025/bubbleseg-histotripsy-dice-focal/
tags: [ultrasound, histotripsy, segmentation, deep-learning, focal-loss]
period: "2024 – 2025"
highlights:
  - "Built a semantic-segmentation framework for histotripsy bubble clouds in B-mode ultrasound, trained with a combined Dice + Focal loss for severe class imbalance."
  - "Benchmarked six modern architectures; EfficientNet-B0 U-Net reaches mean IoU 0.838 and accuracy 0.968 (prior ResNet-18: 0.765 / 0.956) with only 7.9M parameters."
  - "Fixed the prior model's early-treatment blind spot; ~13.5 ms per image on an A100. Collaboration with Prof. Kenneth Bader (UChicago)."
---
<!-- TODO: verify author list (tex author block is commented out; repo README lists a different set: adds Mihir Agarwal, Muskan Singh, drops Ruchika Dhawan). Publication status not stated in source. -->

<div class="tldr" markdown="1">
**Problem.** Histotripsy destroys tissue with cavitation bubble clouds, and B-mode ultrasound is the only real-time way to watch it. A prior ResNet-18 model was nearly blind during early treatment: Dice below 20% for fewer than 500 pulses.  
**Approach.** Treat it as semantic segmentation, train with a combined Dice + Focal loss to handle severe class imbalance, and benchmark six modern architectures on the same data as the prior work.  
**Result.** EfficientNet-B0 U-Net with Dice-Focal loss reaches mean IoU 0.838 and global accuracy 0.968 (prior: 0.765 / 0.956) with only 7.9M parameters, about 13.5 ms per image on an A100.
</div>

## Overview

Histotripsy is a non-thermal focused-ultrasound therapy: microsecond pulses with very high peak negative pressure create an inertial cavitation cloud that mechanically liquefies the target. Clinicians need to know how far the ablation has progressed, but on B-mode the lesion looks hyperechoic early (bubbles) and hypoechoic later (fragmented tissue), so the zone is hard to infer without CT or MRI.

A previous ResNet-18 transfer-learning model from our collaborators at UChicago worked well late in treatment but failed in the clinically interesting early phase, when bubble clouds are sparse and low-contrast. This project asks two questions: which architecture is best suited, and what loss fixes the early-stage blind spot?

## Method

**Data.** Agarose red-blood-cell phantoms let us record B-mode images (C5-2v probe on a Verasonics Vantage 128) together with synchronized optical images of the damage; Otsu-thresholded optical images, co-registered with fiducial markers, give the ground-truth masks. The dataset is nine in-vitro runs (880 images, one image every 20 pulses). One run is held out for validation, and four independent phantom experiments (400 images) form the test set, which is the same test set as the prior work, so comparisons are direct.

**Architectures.** Six models spanning 3.2M to 58.6M parameters: ResNet-18 (re-implementation of the prior approach), MobileNetV3 LR-ASPP, SegFormer-B0, MobileViT-v2 U-Net, EfficientNet-B0 U-Net, and DeepLabV3 (ResNet-101) as a high-capacity reference. All use identical hyperparameters (AdamW, learning rate $$10^{-3}$$, cosine annealing with warm restarts, batch size 16, 128x512 input).

**Loss.** Ablated pixels are a tiny fraction of early frames, so a plain Dice or cross-entropy loss is dominated by background. I used

$$\mathcal{L} = \lambda_{\text{Dice}}\,\mathcal{L}_{\text{Dice}} + \lambda_{\text{Focal}}\,\mathcal{L}_{\text{Focal}}, \qquad \mathcal{L}_{\text{Focal}} = -\alpha_t (1-p_t)^\gamma \log p_t$$

with both weights 1.0, $$\alpha = 1$$ and $$\gamma = 2$$. The focal term down-weights easy background pixels so gradients concentrate on the sparse, hard foreground.

{% include figure.html path="assets/img/projects/bubbleseg/fig_qualitative.png" class="img-fluid rounded z-depth-1" zoomable=true caption="Qualitative results across treatment stages (about 100 to about 2000 pulses). The ResNet-18 baseline is noisy and misses the early ablation zone; EfficientNet-B0 and DeepLabV3 with Dice-Focal loss find sparse bubble activity from the start." %}

## Results

| Method | Global Acc. | Mean Acc. | Mean IoU | Weighted IoU |
|---|---|---|---|---|
| Prior ResNet-18 (Miao et al.) | 0.956 | 0.810 | 0.765 | 0.916 |
| ResNet-18 + Dice (our re-impl.) | 0.954 | 0.851 | 0.780 | 0.916 |
| EfficientNet-B0 + Dice-Focal | **0.968** | 0.894 | **0.838** | **0.939** |
| DeepLabV3 + Dice-Focal | 0.960 | **0.898** | 0.812 | 0.927 |

Dice-Focal beats Dice-only for every architecture tested: for EfficientNet-B0 the Dice score goes from 0.748 to 0.831, for ResNet-18 from 0.757 to 0.791. EfficientNet-B0 has the best DSC (0.831) among efficient models and mean Hausdorff distance 10.2 px; DeepLabV3 has the best area-tracking correlation (Pearson r = 0.978).

<div class="row">
  <div class="col-sm mt-3 mt-md-0">{% include figure.html path="assets/img/projects/bubbleseg/fig_pulse_dependence.png" class="img-fluid rounded z-depth-1" zoomable=true caption="Dice vs. applied pulses. The baseline has a blind spot below 500 pulses." %}</div>
  <div class="col-sm mt-3 mt-md-0">{% include figure.html path="assets/img/projects/bubbleseg/fig_area_vs_pulses.png" class="img-fluid rounded z-depth-1" zoomable=true caption="Predicted vs. true ablation area. The baseline over-predicts even at zero true ablation." %}</div>
</div>

On area tracking, the baseline reports roughly 130 mm$$^2$$ even when true ablation is zero (Pearson r = 0.61, MAE 49.8 mm$$^2$$), while EfficientNet-B0 tracks the ground truth from the first pulses (r = 0.967, MAE 5.98 mm$$^2$$).

{% include figure.html path="assets/img/projects/bubbleseg/fig_efficiency.png" class="img-fluid rounded z-depth-1" zoomable=true caption="Dice vs. parameter count. EfficientNet-B0 gives the best accuracy-per-parameter trade-off; it is 7.4x smaller than DeepLabV3." %}

**Limitations.** Everything is trained on in-vitro agarose phantoms; ex-vivo and in-vivo generalization is untested, and the very early regime (under 100 pulses) is still hard.

## My role

<!-- TODO: verify role bullets against what Shreyans actually did; derived from repo README (listed contributor) and manuscript. -->
- First-listed contributor on the repo and manuscript; worked on the six-architecture benchmark and the Combined Dice-Focal loss.
- Re-implemented the prior ResNet-18 baseline in PyTorch and checked that it closely reproduces the published metrics (global accuracy 0.954 vs 0.956; weighted IoU 0.916 vs 0.916).
- Worked in the MUSE Lab at IIT Gandhinagar with Prof. Himanshu Shekhar; experimental data came from collaborators at the University of Chicago (Prof. Kenneth Bader).

Related write-up: [the story behind the Dice-Focal fix]({{ '/blog/2025/bubbleseg-histotripsy-dice-focal/' | relative_url }}).
