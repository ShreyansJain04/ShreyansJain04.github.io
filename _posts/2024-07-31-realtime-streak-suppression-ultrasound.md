---
layout: post
title: "Building a Real-Time, Two-Stage Streak Suppressor for Therapy-Guidance Ultrasound"
date: 2024-07-31
description: "Why we split streak removal into segmentation plus Fourier-attention inpainting, and how that got us past 440 FPS."
tags: [ultrasound, HIFU, artifact-removal, U-Net, fourier, diffusion]
categories: project-writeups
related_posts: false
toc:
  sidebar: left
project: streak-suppression
---
<!-- TODO: verify metrics. Sources disagree: CV says +13.7 dB and >440 FPS (two-stage pipeline); the old project page said +20 dB SNR; SAUS 2024 abstract says 6.0 +/- 3.4 dB SNR and IoU 0.698 (U-Net + diffusion, initial findings). Old "154 test cases" claim not found in other sources. -->

<div class="tldr" markdown="1">
**Problem.** When an imaging probe runs during focused-ultrasound therapy (HIFU, histotripsy), interference from the therapy field paints bright streaks across the B-mode image, hiding exactly what the clinician needs to watch.  
**Approach.** A two-stage pipeline: a multi-channel U-Net segments the streaks, and a Fourier-attention U-Net inpaints the masked regions. Training data comes from synthetic streaks with Gaussian intensity modulation across several ultrasound domains.  
**Result.** Real-time inference at more than 440 FPS and a +13.7 dB gain in reconstruction quality (CV figures). Presented at ISTU 2024 and the IEEE South Asian Ultrasonics Symposium (SAUS) 2024.
</div>

<!-- TODO: verify claims marked in the project page (dB figures differ across sources). Technical rationale below is explanatory; training details beyond the CV/README/abstracts are not in sources and are not claimed. -->

When a focused-ultrasound therapy such as HIFU or histotripsy runs, the same time-sensitive question hangs over every treatment: what is happening in the tissue right now? B-mode imaging is the live window, but the therapy field interferes with the imaging field, and the resulting image gets streaks. This post is the story of the work I did with Mihir Agarwal, Ruchika Dhawan, Nishita Mistry and Prof. Himanshu Shekhar at the MUSE Lab (IIT Gandhinagar) between December 2023 and July 2024 to remove them fast enough to be used during therapy.

## The constraint: it has to be live

Plenty of ways to clean up an ultrasound image exist if you can afford offline processing. Therapy guidance cannot. If a method is slower than the imaging frame rate, it is useless for the thing it is meant to guide. So from the start the design target was not just "good image quality" but "good quality at a speed no longer a bottleneck". That one requirement shaped almost every choice below.

## The problem has two different halves

Streaks are mostly vertical, bright, thin features that cover some of the image and leave the rest intact. Fixing them involves two different questions:

1. **Where are the streaks?** A detection problem, answered by a binary mask.
2. **What should be there instead?** An inpainting problem: fill in the masked pixels plausibly from the context.

A single network can try to do both, but each half has a different character. Detection is a segmentation task that U-Nets handle well. Inpainting is about reconstructing missing structure, where frequency-domain information is useful because the streak's periodic, vertical structure is easy to describe in Fourier space. Keeping the stages separate also means the second network is only asked to fill in masked regions rather than reinterpret the whole image.

## First attempt: U-Net plus diffusion

Our first version, presented at the IEEE South Asian Ultrasonics Symposium 2024, paired a U-Net with a diffusion model. The U-Net uses skip connections to find streaks, and the diffusion model, used with text-prompt conditioning, does the inpainting. The initial findings were encouraging: an SNR improvement of 6.0 +/- 3.4 dB, IoU 0.698 for the segmentation, and fast model convergence that hinted at real-time potential. But the abstract itself flags the open questions: validation on diverse datasets and performance optimization were future work.

{% include figure.html path="assets/img/projects/streak-suppression/unnamed.png" class="img-fluid rounded z-depth-1" zoomable=true caption="Latent-diffusion style architecture (denoising U-Net with cross-attention and conditioning) of the kind used in the first U-Net plus diffusion study. Diagram from the latent-diffusion literature, shown for illustration." %}

An iterative sampling process is intrinsically heavier than one forward pass, so for a >440 FPS target a feed-forward restoration network is the natural direction.

## The two-stage pipeline

The version in the repository, [Fourier-StreakNet](https://github.com/agarwal-mihir/Fourier-StreakNet), has these parts:

- **Streak segmentation.** A multi-channel U-Net (the repository also has a variant using a frequency-domain notch filter) outputs a streak mask.
- **Restoration.** A U-Net with Fourier attention layers inpaints the masked regions. The attention operates on frequency-domain features, which is where streak structure is concentrated.
- **Evaluation.** The toolkit reports IoU and Dice for the mask, and PSNR and signal-to-interference ratio (SIR) for the restored images.

On the CV-reported measurements, the full pipeline runs at over 440 FPS and improves reconstruction by 13.7 dB.

{% include figure.html path="assets/img/projects/streak-suppression/image.png" class="img-fluid rounded z-depth-1" zoomable=true caption="Input image with streaks, predicted mask, and restored output." %}

## The data problem and the synthetic-streak fix

The biggest practical obstacle was data. You rarely have a perfectly clean twin of an image that was streaked. Our fix was to manufacture the pairs. We isolated images that had no streaks, augmented them to increase the dataset size, and then added random streaks using heuristic functions. Because we create the streaks, we know exactly where they are, so the exact mask for training the segmentation U-Net comes for free, and the clean original is the restoration target. We then split the result into training and validation sets.

{% include figure.html path="assets/img/projects/streak-suppression/unnamed_1.png" class="img-fluid rounded z-depth-1" zoomable=true caption="The synthetic data pipeline." %}

The streak intensity profile mattered. Real streaks are not uniform bars, so we modulated their intensity with Gaussian profiles, and generated data across several ultrasound domains to encourage robust generalization instead of overfitting to a single imaging setup.

## Honest caveats

- **Numbers vary by stage of the work.** The SAUS abstract reports 6.0 +/- 3.4 dB for the early U-Net plus diffusion system, while the later two-stage pipeline is reported at +13.7 dB. These are different systems and should not be compared directly. 
- **Synthetic is not real.** A model trained on synthetic streaks can only be as good as the synthetic generator. The gap to real interference patterns is the main risk, which is why the abstract's "validate on diverse datasets" remains the key next step.
- **Speed is for the pipeline as measured, not a clinical guarantee.** Integrating with a live therapy system is another engineering step.

## Lessons

1. **Decompose by what each part is good at.** Detection and inpainting are different problems; separating them let each network stay small and fast.
2. **Let the speed requirement drive architecture early.** Iterative sampling is inherently heavier than a single forward pass, which matters when the target is real time.
3. **When you lack paired data, build the generator carefully.** The quality of your synthetic degradation model is the ceiling on what the restoration network learns.
4. **Report numbers with their context.** Three systems, three sets of metrics; tie each to a source.

## Key numbers

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

## Links

- Code: [agarwal-mihir/Fourier-StreakNet](https://github.com/agarwal-mihir/Fourier-StreakNet)
- Poster: [SAUS 2024]({{ '/assets/pdf/streak_poster_saus2024.pdf' | relative_url }})
