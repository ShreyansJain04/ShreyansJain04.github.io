---
layout: page
title: "Variational Diffusion Unlearning"
description: "Removing classes and styles from a trained diffusion model using only the data to forget. Published in TMLR 2026."
img: assets/img/projects/vdu/thumb.jpg
importance: 1
category: "Research"
status: "TMLR 2026"
advisor: "Prof. Prathosh A.P., IISc Bangalore"
period: "May 2024 – Nov 2024"
team: "Subhodip Panda, Varun M S, Shreyans Jain, Sarthak Kumar Maharana, Prathosh A.P."
links:
  blog: /blog/2026/variational-diffusion-unlearning/
  paper: https://openreview.net/forum?id=mAHRgieyOV
  report: https://arxiv.org/abs/2510.04058
tags: [diffusion models, machine unlearning, variational inference, Stable Diffusion]
highlights:
  - "Framed unlearning in diffusion models (DDPM, Stable Diffusion) as variational inference: approximate the retrained posterior using only the samples to forget."
  - "Two-term loss: a plasticity inducer pushes down the likelihood of unwanted data, and a stability regularizer prevents catastrophic forgetting."
  - "Up to 71.6% unlearning (PUL) on CIFAR-10 with over 10× better u-FID than baselines. Published in TMLR 2026, after a NeurIPS 2024 workshop paper."
---

<div class="tldr" markdown="1">
**Problem.** Diffusion models can generate content you need to remove after training, such as a class or an artist's style. Retraining without that data is expensive, and most unlearning methods assume access to the full training set.  
**Approach.** A one-step, data-constrained method that fine-tunes the model using **only the data to be forgotten**, with a loss derived from variational inference.  
**Result.** High unlearning rates with far better image quality than the baselines on MNIST, CIFAR-10 and tinyImageNet, and style and object removal in Stable Diffusion. Published in **TMLR 2026**.
</div>

## Overview

This was my research internship in Prof. Prathosh A.P.'s lab at IISc Bangalore. The question: if the original training set is not available, can we still make a pretrained diffusion model stop generating a class (say, "ship") or a feature (say, Van Gogh's style) without breaking everything else it knows?

## Method

Using Bayes' rule, the posterior over parameters after removing the forget set $$D_f$$ is

$$P(\theta \mid D_r) \propto \frac{P(\theta \mid D_r, D_f)}{P(D_f \mid \theta)},$$

so the ideal "retrained" model can be approximated starting from the current model, using $$D_f$$ alone. With a Gaussian mean-field variational posterior, the objective splits into two terms:

- **Plasticity inducer:** lowers the log-likelihood of the samples to forget.
- **Stability regularizer:** keeps the parameters close to the pretrained solution, weighted by their importance, so the model keeps its generation quality.

{% include figure.html path="assets/img/projects/vdu/method.png" class="img-fluid rounded z-depth-1" zoomable=true caption="VDU fine-tunes the pretrained model with a two-term loss, using only the user-identified samples to forget." %}

## Results

Class unlearning on unconditional DDPMs. PUL (percentage of unlearning) is higher-is-better and u-FID (quality of the remaining generations) is lower-is-better. The paper compares VDU with Selective Amnesia (SA), SalUn and ESD, which have the same data constraint:

| Dataset | Forgotten class | SA (PUL / u-FID) | SalUn | ESD | **VDU (ours)** |
|---|---|---|---|---|---|
| MNIST | Digit 1 | 15.01 / 301.26 | 45.28 / 68.75 | 56.66 / 66.15 | **75.06 / 14.43** |
| MNIST | Digit 8 | 48.95 / 161.09 | 32.53 / 50.18 | 32.68 / 55.67 | **68.96 / 38.20** |
| CIFAR-10 | Automobile | 2.25 / 92.89 | 12.01 / 66.47 | 8.97 / 73.48 | **60.87 / 30.86** |
| CIFAR-10 | Ship | 85.02 / 249.89 | 55.13 / 75.48 | 58.27 / 77.12 | 71.63 / **24.46** |
| tinyImageNet | Fish | 67.7 / 32.00 | 39.33 / 42.70 | 41.67 / 45.19 | 58.75 / **29.92** |
| tinyImageNet | Butcher shop | 6.7 / 24.00 | 2.87 / 33.47 | 8.76 / 39.48 | **66.67 / 24.17** |

The baselines either barely unlearn or wreck image quality (u-FID in the hundreds). VDU keeps both under control.

<div class="row">
  <div class="col-sm mt-3 mt-md-0">{% include figure.html path="assets/img/projects/vdu/cifar_initial.png" class="img-fluid rounded z-depth-1" zoomable=true caption="CIFAR-10 samples from the pretrained DDPM" %}</div>
  <div class="col-sm mt-3 mt-md-0">{% include figure.html path="assets/img/projects/vdu/cifar_unlearn_ship.png" class="img-fluid rounded z-depth-1" zoomable=true caption="Same noise after unlearning 'ship'" %}</div>
</div>

{% include figure.html path="assets/img/projects/vdu/vangogh_grid.png" class="img-fluid rounded z-depth-1" zoomable=true caption="Feature unlearning in Stable Diffusion: removing the Van Gogh style." %}

## My role

- Worked on the variational formulation and the stability regularizer as a research intern (May–Nov 2024).
- Ran class-unlearning experiments on DDPMs and the comparisons with the baselines.
- Co-authored the NeurIPS 2024 Safe Generative AI workshop paper and the TMLR journal version.
