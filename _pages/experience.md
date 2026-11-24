---
layout: page
permalink: /experience/
title: experience
description: Internships and research positions.
nav: true
nav_order: 2
---

## Internships & research positions

<div class="xp-item">
  <div class="xp-head"><span class="xp-role">Research Intern</span><span class="xp-date">May 2025 – Jul 2025</span></div>
  <div class="xp-org"><b>Purdue University</b>, West Lafayette, USA · Advisors: Prof. Dharmendra Saraswat &amp; Prof. Vaneet Aggarwal</div>
  <ul>
    <li>Designed and built <b>GeoTutor</b>, an intelligent tutoring system for personalized GIS education, on a hybrid RAG pipeline (BM25 + dense retrieval + cross-encoder reranking).</li>
    <li>Built an adaptive teaching engine with a learner-memory model that generates personalized learning plans, detects conceptual errors, and schedules reviews with the SuperMemo-2 spaced-repetition algorithm.</li>
    <li>Built the FastAPI + Pydantic backend with FAISS indexing and integrated it with a teammate's React frontend; journal manuscript in preparation.</li>
  </ul>
  <div class="project-links"><a class="btn-link-pill" href="/projects/geotutor/"><i class="fas fa-folder-open"></i> Project</a><a class="btn-link-pill" href="https://github.com/ShreyansJain04/GISLLM" target="_blank" rel="noopener"><i class="fab fa-github"></i> Code</a></div>
</div>

<div class="xp-item">
  <div class="xp-head"><span class="xp-role">Summer Research Intern</span><span class="xp-date">May 2024 – Nov 2024</span></div>
  <div class="xp-org"><b>Indian Institute of Science (IISc), Bangalore</b> · Advisor: Prof. Prathosh A.P.</div>
  <ul>
    <li>Developed <b>Variational Diffusion Unlearning (VDU)</b>, a framework that removes concepts from diffusion models (DDPM, Stable Diffusion) by treating unlearning as variational inference, approximating the retrained posterior using only the images to forget.</li>
    <li>Reached a <b>71.6% unlearning rate</b> (PUL) on CIFAR-10 and improved sample quality (u-FID) by <b>over 10×</b> versus baselines, using a new stability regularizer that prevents catastrophic forgetting.</li>
    <li>Published in <b>TMLR 2026</b>, after a NeurIPS 2024 workshop paper.</li>
  </ul>
  <div class="project-links"><span class="status-pill">TMLR 2026</span><a class="btn-link-pill" href="/projects/vdu/"><i class="fas fa-folder-open"></i> Project</a><a class="btn-link-pill" href="https://openreview.net/forum?id=mAHRgieyOV" target="_blank" rel="noopener"><i class="fas fa-file-alt"></i> Paper</a></div>
</div>

<div class="xp-item">
  <div class="xp-head"><span class="xp-role">Undergraduate Researcher, MUSE Lab</span><span class="xp-date">Dec 2023 – 2025</span></div>
  <div class="xp-org"><b>IIT Gandhinagar</b> · Advisor: Prof. Himanshu Shekhar</div>
  <ul>
    <li><b>Real-time streak suppression:</b> a two-stage pipeline (multi-channel U-Net segmentation, then Fourier-attention U-Net inpainting) that runs at <b>&gt;440 FPS</b> and improves reconstruction by <b>+13.7 dB</b> on synthetic streak data.</li>
    <li><b>BubbleSeg:</b> CNN segmentation of histotripsy bubble clouds with a combined Dice-Focal loss.</li>
    <li><b>VascFlexMap:</b> transformer-decoder network for microvascular ultrasound imaging at low frame rates.</li>
    <li>Two presentations at <b>ISTU 2024</b> (Taipei) and one at <b>IEEE SAUS 2024</b>.</li>
    <li><b>Patent filed</b> as co-inventor: <i>A System and Method for Super-Resolution Ultrasound Reconstruction with Representation Learning on Sparse Data</i>.</li>
  </ul>
  <div class="project-links"><a class="btn-link-pill" href="/projects/streak-suppression/"><i class="fas fa-folder-open"></i> Streak suppression</a><a class="btn-link-pill" href="/projects/bubbleseg/"><i class="fas fa-folder-open"></i> BubbleSeg</a><a class="btn-link-pill" href="/projects/vascflexmap/"><i class="fas fa-folder-open"></i> VascFlexMap</a></div>
</div>

<div class="xp-item">
  <div class="xp-head"><span class="xp-role">Undergraduate Researcher</span><span class="xp-date">Feb 2024 – Nov 2024</span></div>
  <div class="xp-org"><b>IIT Gandhinagar</b> · Advisor: Prof. Shanmuganathan Raman</div>
  <ul>
    <li>Designed <b>WavShadow</b>, an end-to-end shadow segmentation and removal framework: Haar-wavelet features for segmentation, FFC blocks with MAE priors for removal.</li>
    <li>State-of-the-art <b>1.38 BER on ISTD</b> and <b>36.7 PSNR on DESOBA</b> (+0.7 over the 2023 state of the art).</li>
  </ul>
  <div class="project-links"><span class="status-pill">ICVGIP 2024</span><a class="btn-link-pill" href="/projects/wavshadow/"><i class="fas fa-folder-open"></i> Project</a><a class="btn-link-pill" href="https://arxiv.org/abs/2411.05747" target="_blank" rel="noopener"><i class="fas fa-file-alt"></i> Paper</a></div>
</div>

## Industry

<div class="xp-item">
  <div class="xp-head"><span class="xp-role">AI Engineer</span><span class="xp-date">Dec 2023 – Mar 2024</span></div>
  <div class="xp-org"><b>KrishiMandir</b> · Mentors: Mr. Sumeet Mohanty &amp; Mr. Noel Kurien</div>
  <ul>
    <li>Built a ConvNeXt image classifier with heavy data augmentation that reaches <b>99.2% accuracy on 55 classes</b>, starting from only 4 images per class. It replaced the company's OCR-based system.</li>
    <li>Built a visual similarity search system at <b>96% accuracy</b>.</li>
    <li>Benchmarked open-source LLMs and RAG pipelines for Clojure function calling, comparing efficiency and accuracy.</li>
  </ul>
</div>
