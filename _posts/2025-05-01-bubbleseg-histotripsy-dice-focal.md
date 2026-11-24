---
layout: post
title: "Closing the Early-Stage Blind Spot in Histotripsy Monitoring with Dice-Focal Loss"
date: 2025-05-01
description: "How a loss-function change, more than a bigger network, fixed segmentation of sparse bubble clouds in B-mode ultrasound."
tags: [ultrasound, histotripsy, segmentation, focal-loss, deep-learning]
categories: project-writeups
related_posts: false
toc:
  sidebar: left
featured: 7
---

> **TL;DR.** The earlier model was nearly blind below 500 pulses, which is exactly when a clinician would adjust treatment. Switching to a Dice + Focal loss helped more than any architecture change: it improved every model we tried, and a 7.9M-parameter EfficientNet-B0 U-Net beat a 58.6M-parameter DeepLabV3 on Dice while tracking the true lesion area from the first frames.

Histotripsy is one of the more striking ideas in therapeutic ultrasound. Instead of heating tissue, it fires microsecond pulses with very high peak negative pressure into a target and creates a cloud of cavitation bubbles that mechanically liquefies it. No heat, no ionizing radiation, and no heat-sink problem near blood vessels. The catch is that you need to know what you have destroyed. This post is about the part of that problem I worked on at the MUSE Lab (IIT Gandhinagar): segmenting the ablation zone from B-mode ultrasound, and in particular, why our models first failed exactly when the clinician cares most.

## The problem: you cannot see the lesion

Histotripsy systems are usually paired with B-mode imaging for targeting. But the lesion's appearance changes over the treatment. Early on, the bubble cloud shows up as a hyperechoic region; later, once tissue is fragmented, it becomes hypoechoic. In between, contrast is low and the region is speckled. Right now, confirming that an ablation worked often means going to CT or MRI, which adds time, cost and complexity. A model that outlines the ablated region directly on the live ultrasound image could close that loop.

A previous paper from our collaborators (Miao et al., IEEE TBME 2024) trained a ResNet-18 with transfer learning to do this. It worked reasonably overall, but it had a blind spot: the Dice similarity coefficient was below 20% for fewer than 500 applied pulses. The early frames are precisely when you would want to adjust a treatment, so this was the gap we wanted to close.

## Setting up a fair comparison

I wanted every number in our study to be comparable to the earlier work, so we used the same experimental data. The data come from agarose phantoms containing a red-blood-cell layer. When histotripsy ablates the layer, it changes color, so a synchronized camera records ground truth while the ultrasound probe records B-mode images. Otsu-thresholding the optical images and co-registering them with fiducial markers gives masks in ultrasound coordinates.

The dataset is small: nine experimental runs, 880 ultrasound images (an image every 20 pulses). One run is held out for validation, and four fully independent phantoms (400 images) are used only for testing. That is the same test set as the prior paper. Small data has a real consequence: you need to be careful with leakage, so we used a leave-one-dataset-out strategy and dropped a few timestamps to avoid overlap.

Before changing anything, I re-implemented the ResNet-18 baseline in PyTorch. Its global accuracy (0.954 vs 0.956) and weighted IoU (0.916 vs 0.916) landed very close to the published numbers, which gave me confidence that later gains were not an artifact of a different pipeline.

## What we tried

We evaluated six architectures spanning 3.2M to 58.6M parameters:

- ResNet-18 (the baseline, adapted to segmentation)
- MobileNetV3 LR-ASPP
- SegFormer-B0
- MobileViT-v2 with a U-Net decoder
- EfficientNet-B0 U-Net
- DeepLabV3 with a ResNet-101 backbone, as a high-capacity reference

All were fine-tuned from public pretrained weights and trained with identical settings (AdamW, learning rate $$10^{-3}$$, cosine annealing with warm restarts, batch size 16, 128x512 input) so architecture was the only variable.

The more important variable turned out to be the loss.

### Why Dice alone struggles here

In early frames, ablated pixels are a minuscule fraction of the image. Cross-entropy is swamped by background. Dice loss helps with imbalance, but when the foreground is a few faint pixels its gradients are noisy, and the model can score decently by predicting almost nothing. We added a focal term:

$$\mathcal{L}_{\text{Focal}}(p_t) = -\alpha_t (1-p_t)^{\gamma} \log(p_t), \qquad \mathcal{L}_{\text{Total}} = \mathcal{L}_{\text{Dice}} + \mathcal{L}_{\text{Focal}}$$

with $$\alpha = 1$$ and $$\gamma = 2$$. The $$(1-p_t)^\gamma$$ factor shrinks the loss on pixels the model already classifies confidently, which in this problem is nearly all of the background. What is left is the hard, sparse foreground. Both terms are weighted 1.0.

## What worked

The loss change was the single most consistent improvement. For every architecture we tested, Dice-Focal beat Dice alone: ResNet-18 went from DSC 0.757 to 0.791, and EfficientNet-B0 from 0.748 to 0.831.

On the 400 independent test images, the headline comparison is:

| Method | Global Acc. | Mean IoU | Weighted IoU |
|---|---|---|---|
| Prior ResNet-18 | 0.956 | 0.765 | 0.916 |
| EfficientNet-B0 + Dice-Focal | 0.968 | 0.838 | 0.939 |
| DeepLabV3 + Dice-Focal | 0.960 | 0.812 | 0.927 |

{% include figure.html path="assets/img/projects/bubbleseg/fig_pulse_dependence.png" class="img-fluid rounded z-depth-1" zoomable=true caption="Dice similarity coefficient versus number of applied pulses. The shaded region is the clinically difficult early stage (under 500 pulses)." %}

The pulse-dependence curve is the one I care about most. With the prior training setup, the baseline sits near zero below 500 pulses. Both EfficientNet-B0 and DeepLabV3 with Dice-Focal loss rise steeply from around 300 pulses and plateau at about 0.83 and 0.88 respectively, versus 0.63 for the baseline.

The area plot shows a second, quieter failure of the baseline: it over-predicts the ablated area throughout treatment, around 130 mm$$^2$$ even when the true ablation is zero (Pearson r = 0.61, MAE 49.8 mm$$^2$$). EfficientNet-B0 tracks the true area from the outset (r = 0.967, MAE 5.98 mm$$^2$$), and DeepLabV3 is tightest (r = 0.978, MAE 5.03 mm$$^2$$). For a clinician, an area estimate that is right is more useful than a pretty mask.

{% include figure.html path="assets/img/projects/bubbleseg/fig_area_vs_pulses.png" class="img-fluid rounded z-depth-1" zoomable=true caption="Predicted versus ground-truth ablation area, full treatment (left) and early-stage zoom (right)." %}

### The small model wins

The pleasant surprise was efficiency. EfficientNet-B0 U-Net has 7.9M parameters, 7.4 times fewer than DeepLabV3 (58.6M), and still had the better Dice (0.831 vs 0.802) and mean IoU. It runs at roughly 13.5 ms per image on an A100. DeepLabV3's strength is the area-tracking correlation, which we attribute to its multi-scale atrous convolutions. As a reference upper bound it is useful; as a deployable model, the small U-Net makes more sense.

{% include figure.html path="assets/img/projects/bubbleseg/fig_efficiency.png" class="img-fluid rounded z-depth-1" zoomable=true caption="Dice versus parameter count. Blue: Dice-Focal loss; red: Dice-only loss." %}

## What did not work, or is not solved

- **Bigger was not better.** The 58.6M-parameter DeepLabV3 did not beat EfficientNet-B0 on Dice, and the lightweight options (MobileNetV3, MobileViT-v2) did not either.
- **Dice-only EfficientNet-B0 was unstable.** Its DSC looked moderate at 0.748, but its area correlation was negative (r = -0.668). That is a good reminder that a single overlap metric can hide a model that is not tracking the physical quantity you care about.
- **Under about 100 pulses is still hard.** The class imbalance there is extreme and we did not solve it. Targeted augmentation is the next thing I would try.
- **Phantoms are not tissue.** Everything is in-vitro agarose. Ex-vivo and in-vivo data will change speckle statistics and annotation quality; semi-supervised or domain-adaptation methods may reduce the labeling burden.
- **Labels are noisy.** Ground truth comes from thresholded optical images, and annotation variability was a recurring challenge noted in the project.

## Takeaways

1. When the signal you care about is a sparse minority of pixels, change the loss before you change the architecture. Of all the changes we made, this was the most consistent.
2. Re-implement the baseline and match the published numbers first. It is tedious, but it is what makes the comparison credible.
3. Track the physical quantity (here, lesion area) and not only an overlap score.
4. A 7.9M-parameter model that matches or beats a 58.6M one is the more interesting result for a system that has to run beside a therapy device.

## Links

- Project page: [Histotripsy bubble-cloud segmentation]({{ '/projects/bubbleseg/' | relative_url }})
- Code: [ShreyansJain04/BubbleSegmentation](https://github.com/ShreyansJain04/BubbleSegmentation)
