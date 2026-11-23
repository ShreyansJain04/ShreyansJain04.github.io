---
layout: page
title: "Visualizations for Machine Learning"
description: "Quarto blogs and Streamlit apps that make optimization, information theory and probability concepts interactive."
img: assets/img/projects/vis-ml/thumb.jpg
importance: 5
category: "ML & Data Projects"
period: "2023-24"   # TODO: verify; report figures are dated Sep-Nov 2023
team: "Vannsh Jani, Shreyans Jain, Viraj Vekaria (with Kishan Ved on some topics)"
advisor: "Prof. Nipun Batra, IIT Gandhinagar"
links:
  report: https://intensedrop.notion.site/Visualizations-for-ML-951994a20ee447268626a82e4659c41f
  demo: https://optiviz.streamlit.app/
  blog: /blog/2024/visualizations-for-ml/
tags: [education, Streamlit, optimization, information-theory, visualization]
---

<div class="tldr" markdown="1">
**Problem.** Machine learning algorithms are hard to understand from equations alone.  
**Approach.** For each concept, write a Quarto blog post with from-scratch code and build a Streamlit app where the reader can change parameters and watch the algorithm run. Done as a CS299 project advised by Prof. Nipun Batra.  
**Result.** More than a dozen live blogs and Streamlit apps covering optimization, information theory and probability. The gallery below has the highlights.
</div>

## Overview

The project is part of Prof. [Nipun Batra](https://nipunbatra.github.io/)'s teaching effort. The CS299 report states the goal as bridging "the gap between machine learning intricacies and educational accessibility". Each topic got a blog explaining the maths plus code, and, where useful, an app. The full write-up lives on the [project notion page](https://intensedrop.notion.site/Visualizations-for-ML-951994a20ee447268626a82e4659c41f).

## Method

Topics covered by the team include first-order optimizers (SGD, RMSProp, Adam), second-order methods (Newton, L-BFGS), Taylor series, constrained optimization with KKT conditions, computational graphs and autodiff, Huffman and Shannon-Fano coding, JPEG compression, SIREN-based audio and image compression, mutual information, noisy channel coding, Markov chains, Fisher information, change of variables and CORDIC.

A design lesson from the optimizer app: it first redrew the plot after every epoch, which was prohibitively slow. Storing the path in a list and plotting once at the end fixed speed, and animation was added later.

<div class="row">
  <div class="col-sm mt-3 mt-md-0">{% include figure.html path="assets/img/projects/vis-ml/contour.png" class="img-fluid rounded z-depth-1" zoomable=true caption="Stepping an optimizer with momentum on a contour plot" %}</div>
  <div class="col-sm mt-3 mt-md-0">{% include figure.html path="assets/img/projects/vis-ml/cordic.png" class="img-fluid rounded z-depth-1" zoomable=true caption="CORDIC app: the red vector converges on the target angle" %}</div>
</div>

## Demo gallery

Each card opens a live app or blog. All of them are listed on the [project Notion page](https://intensedrop.notion.site/Visualizations-for-ML-951994a20ee447268626a82e4659c41f).

<div class="demo-grid">
{% assign demos = "notion_adam.png|Adam optimizer: animated learning path|https://optiviz.streamlit.app/;notion_contour.png|Contour plots: updates after every epoch|https://sgdmomentum.streamlit.app/;notion_velocity.png|Velocity visualization for momentum|https://velocityviz.streamlit.app/;notion_optpath.png|Optimization path explorer|https://foptim.streamlit.app/;notion_cordic.png|CORDIC algorithm|https://cordic.streamlit.app/;notion_constraint.png|Constrained optimization (blog)|https://vannshjani.github.io/Blogs/posts/constraints.html;notion_compgraph.png|Computational graphs and autodiff (blog)|https://vannshjani.github.io/Blogs/posts/autodiff.html" | split: ";" %}
{% for d in demos %}{% assign f = d | split: "|" %}
  <a class="demo-card" href="{{ f[2] }}" target="_blank" rel="noopener">
    <div class="demo-img"><img src="{{ '/assets/img/projects/vis-ml/' | append: f[0] | relative_url }}" alt="{{ f[1] }}" loading="lazy"></div>
    <div class="demo-title">{{ f[1] }} <i class="fas fa-external-link-alt"></i></div>
  </a>
{% endfor %}
</div>

## More apps

| Topic | App | Authors |
|---|---|---|
| Fisher information | [fisher.streamlit.app](https://fisher.streamlit.app/) | Shreyans |
| Huffman coding | [huffman.streamlit.app](https://huffman.streamlit.app/) | Kishan and Shreyans |
| JPEG: coding the DCT matrix | [jpegcoding.streamlit.app](https://jpegcoding.streamlit.app/) | Kishan and Shreyans |
| CORDIC algorithm | [cordic.streamlit.app](https://cordic.streamlit.app/) | Viraj and Shreyans |
| Change of variables (Jacobian) | [changeofvariables.streamlit.app](https://changeofvariables.streamlit.app/) | Shreyans |
| Noisy channel coding | [noisychannelcoding.streamlit.app](https://noisychannelcoding.streamlit.app/) | Vannsh |

## Results

<div class="row">
  <div class="col-sm mt-3 mt-md-0">{% include figure.html path="assets/img/projects/vis-ml/fischer.jpg" class="img-fluid rounded z-depth-1" zoomable=true caption="Fisher information app" %}</div>
  <div class="col-sm mt-3 mt-md-0">{% include figure.html path="assets/img/projects/vis-ml/huffapp.png" class="img-fluid rounded z-depth-1" zoomable=true caption="Huffman tree built step by step" %}</div>
  <div class="col-sm mt-3 mt-md-0">{% include figure.html path="assets/img/projects/vis-ml/siren_ss.png" class="img-fluid rounded z-depth-1" zoomable=true caption="Image reconstructed by a SIREN" %}</div>
</div>

One small measured result from the report: a from-scratch RMSProp contributed to the open-source wimpyML library reached 97.11% on MNIST, against 97.31% for `torch.optim.RMSprop`, with similar training time (115.7 s versus 113.3 s for 10 iterations).

## My role

- **Optimizers.** With Viraj, built the Streamlit app comparing SGD, Adam and RMSProp, plus the contour-plot momentum demo and the velocity app.
- **Information theory.** With Kishan, the Huffman coding blog and app, and a Colab walk-through of the JPEG pipeline (YCbCr, chroma subsampling, DCT, quantization, Huffman).
- **Maths concepts.** Blogs and apps on Fisher information and on change of variables with the Jacobian; with Viraj, the CORDIC app.
