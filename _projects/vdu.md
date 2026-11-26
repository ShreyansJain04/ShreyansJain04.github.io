---
layout: redirect
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
redirect: /blog/2026/variational-diffusion-unlearning/
sitemap: false
---
