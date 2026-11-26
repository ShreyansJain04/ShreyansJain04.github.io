---
layout: post
title: "Making a Diffusion Model Forget, Without the Training Data"
date: 2026-03-20
description: "Variational Diffusion Unlearning (TMLR 2026): treating unlearning as variational inference over the weights, so a diffusion model can drop a class or a style using only the images it should forget."
tags: [diffusion-models, machine-unlearning, variational-inference, stable-diffusion, generative-ai]
categories: project-writeups
related_posts: false
toc:
  sidebar: left
project: vdu
---
<div class="tldr" markdown="1">
**Problem.** Diffusion models can generate content you need to remove after training, such as a class or an artist's style. Retraining without that data is expensive, and most unlearning methods assume access to the full training set.  
**Approach.** A one-step, data-constrained method that fine-tunes the model using **only the data to be forgotten**, with a loss derived from variational inference.  
**Result.** High unlearning rates with far better image quality than the baselines on MNIST, CIFAR-10 and tinyImageNet, and style and object removal in Stable Diffusion. Published in **TMLR 2026**.
</div>

Suppose you have a trained diffusion model and you find out it can produce something it shouldn't: a copyrighted artist's style, a person's likeness, or just a class you no longer want it to generate. The clean fix is to retrain from scratch without that data. That is usually far too expensive, and often impossible, because you no longer have the full training set.

This post walks through **Variational Diffusion Unlearning (VDU)**, the method we developed during my research internship in Prof. Prathosh A.P.'s lab at IISc Bangalore. It started as a NeurIPS 2024 workshop paper (Safe Generative AI) and grew into a journal paper in *Transactions on Machine Learning Research* (2026), with Subhodip Panda, M S Varun, Sarthak Kumar Maharana and Prathosh A.P.

## The setting: you only have what you want to forget

Most unlearning methods for diffusion models quietly assume you still have the data you want to *keep*. Selective Amnesia replays generated samples of the remaining classes. Saliency Unlearning (SalUn) perturbs the most influential weights using the whole training set as a reference. That is reasonable in a lab, but in practice the full training set is often gone, private, or far too large to touch.

So we set a stricter rule. The only data available is $$D_f$$, a small set of images showing the thing to forget. The remaining data $$D_r$$ is off-limits. Under that rule, the obvious approach fails badly: if you simply push the model's likelihood down on $$D_f$$, it does forget, but it also forgets how to make good images of anything. This is *catastrophic forgetting*, and in this setting there is no remaining data to anchor the model.

The question becomes: **can we forget $$D_f$$ while keeping generation quality, using nothing but $$D_f$$ and the pretrained weights?**

## Unlearning as Bayesian bookkeeping

The key move is to think about the weights as a distribution rather than a single point.

A model trained on everything is a sample from the posterior $$P(\theta \mid D_r, D_f)$$. The model we wish we had, retrained without $$D_f$$, is a sample from $$P(\theta \mid D_r)$$. Bayes' rule links the two, because the data points are independent:

$$P(\theta \mid D_r) \;\propto\; \frac{P(\theta \mid D_r, D_f)}{P(D_f \mid \theta)}$$

In words: start from the full posterior and divide out the evidence that came from the forget set. We never need $$D_r$$ directly. We only need the full-data posterior, which the pretrained model gives us, and the likelihood of $$D_f$$, which we can compute.

That target is intractable, so we approximate it with a simpler distribution $$Q(\theta)$$ by minimising a KL divergence, the standard variational inference recipe:

$$Q^*(\theta) = \arg\min_{Q} \; D_{KL}\!\left(Q(\theta) \,\Big\|\, Z \cdot \frac{P(\theta \mid D_f, D_r)}{P(D_f \mid \theta)}\right)$$

With a Gaussian mean-field assumption on the weights, and the diffusion model's usual variational bound on log-likelihood, this works out to a loss with two parts.

## The loss: a push and a leash

{% include figure.html path="assets/img/projects/vdu/method.png" class="img-fluid rounded z-depth-1" zoomable=true caption="VDU fine-tunes the pretrained model with two terms: a plasticity inducer that lowers the likelihood of the forget set, and a stability regularizer that keeps the weights close to their pretrained values." %}

$$
\mathcal{L}_{VDU} =
\underbrace{-(1-\gamma)\,\mathbb{E}_{x_0 \sim D_f,\,\epsilon,\,t}\!\left[w_t \,\big\|\epsilon - \epsilon_\theta(x_t, t)\big\|^2\right]}_{\text{plasticity inducer}}
\;+\;
\underbrace{\gamma \sum_{i=1}^{d} \frac{(\theta_i - \mu^*_i)^2}{2\sigma^{*2}_i}}_{\text{stability regularizer}}
$$

- **The plasticity inducer is the push.** It is the ordinary denoising loss on the forget set, with the sign flipped. Minimising it makes the model *worse* at denoising images of the unwanted class, so it stops producing them.
- **The stability regularizer is the leash.** Each weight is pulled back towards its pretrained mean $$\mu^*_i$$, scaled by $$1/\sigma^{*2}_i$$. Weights the model is confident about (small variance) are held tightly; uncertain ones are free to move.
- **$$\gamma$$ sets the balance** between forgetting and staying put.

This looks like Elastic Weight Consolidation, which Selective Amnesia uses, but it comes from a different place and is cheaper. EWC weights its penalty with the Fisher information matrix, which needs gradient products over data. VDU gets $$\mu^*$$ and $$\sigma^*$$ directly from the spread of the weights across independently trained checkpoints: we trained five models per dataset and used their per-weight mean and variance. Once those are in hand, unlearning is a plain fine-tuning loop on $$D_f$$, usually for a single epoch.

## Does it work?

We tested two kinds of forgetting:

- **Class unlearning**: removing a class (a digit, "ship", "fish", "butcher shop") from unconditional DDPMs trained on MNIST, CIFAR-10 and tinyImageNet.
- **Feature unlearning**: removing a concept such as *Van Gogh's style* or *cars* from Stable Diffusion, pretrained on LAION-5B.

Two numbers matter. **PUL** (percentage of unlearning) counts how many fewer unwanted samples the model generates afterwards, judged by a classifier over 5,000 samples; higher is better. **u-FID** measures the quality of everything else the model still generates; lower is better. A method that wins only one of these isn't useful: you can get 100% PUL by breaking the model.

All baselines were held to the same rule (no access to $$D_r$$) and the same short compute budget. "Fine-tuning" is a reference point that *does* see $$D_r$$, so it shows roughly the best you could hope for.

| Dataset | Forgotten class | Fine-tuning (sees $$D_r$$) | SA | SalUn | ESD | **VDU** |
|---|---|---|---|---|---|---|
| MNIST | Digit 1 | 90.1 / 5.9 | 15.0 / 301.3 | 45.3 / 68.8 | 56.7 / 66.2 | **75.1 / 14.4** |
| MNIST | Digit 8 | 94.3 / 6.2 | 49.0 / 161.1 | 32.5 / 50.2 | 32.7 / 55.7 | **69.0 / 38.2** |
| CIFAR-10 | Automobile | 88.0 / 9.0 | 2.3 / 92.9 | 12.0 / 66.5 | 9.0 / 73.5 | **60.9 / 30.9** |
| CIFAR-10 | Ship | 92.9 / 10.7 | 85.0 / 249.9 | 55.1 / 75.5 | 58.3 / 77.1 | 71.6 / **24.5** |
| tinyImageNet | Fish | 82.6 / 13.8 | 67.7 / 32.0 | 39.3 / 42.7 | 41.7 / 45.2 | 58.8 / **29.9** |
| tinyImageNet | Butcher shop | 83.4 / 16.8 | 6.7 / 24.0 | 2.9 / 33.5 | 8.8 / 39.5 | **66.7 / 24.2** |

*Each cell is PUL (%) / u-FID, averaged over three seeds.*

The pattern is consistent. Among methods that respect the no-$$D_r$$ rule, VDU has the best image quality on every class, and the best or near-best forgetting. Where a baseline forgets more, it pays dearly for it. Selective Amnesia removes 85% of ships from CIFAR-10, but its u-FID of 250 means the rest of its output has collapsed. VDU removes 72% with a u-FID of 24.5, roughly ten times better.

<div class="row">
  <div class="col-sm mt-3 mt-md-0">{% include figure.html path="assets/img/projects/vdu/cifar_initial.png" class="img-fluid rounded z-depth-1" zoomable=true caption="Samples from the pretrained CIFAR-10 DDPM." %}</div>
  <div class="col-sm mt-3 mt-md-0">{% include figure.html path="assets/img/projects/vdu/cifar_unlearn_ship.png" class="img-fluid rounded z-depth-1" zoomable=true caption="After unlearning 'ship' with VDU: ships disappear, and the other classes stay sharp." %}</div>
</div>

It is also fast. VDU needed one epoch on MNIST and two on tinyImageNet, while SalUn and ESD needed five on every dataset.

{% include figure.html path="assets/img/projects/vdu/time.png" class="img-fluid rounded z-depth-1" zoomable=true caption="Unlearning cost in epochs. VDU matches plain fine-tuning on MNIST and stays well below SalUn and ESD." %}

## Forgetting a style in Stable Diffusion

The same loss scales to Stable Diffusion. Here the "forget set" is a handful of images showing the concept, and we watch what the model produces for a fixed prompt and seed as unlearning goes on.

{% include figure.html path="assets/img/blog/vdu/vangogh-portrait-epochs.jpg" class="img-fluid rounded z-depth-1" zoomable=true caption="Prompt: 'a portrait of van gogh', unlearning concept 'Van Gogh'. From left: original, then epochs 1 to 5. The swirling brushwork fades into a flat, painterly portrait while the composition is kept." %}

{% include figure.html path="assets/img/blog/vdu/car-downhill-epochs.jpg" class="img-fluid rounded z-depth-1" zoomable=true caption="Prompt: 'a car going downhill', unlearning concept 'car'. Over ten epochs the car dissolves and the road and landscape remain." %}

These grids also show the method's central trade-off. Every extra epoch of the plasticity inducer removes more of the concept, but also drifts the weights further from the original model.

## The trade-off in numbers

That trade-off is clear in the epoch ablation. Unlearning digit 1 from MNIST:

| Epochs | 1 | 2 | 3 | 4 | 5 |
|---|---|---|---|---|---|
| PUL (%) | 75.1 | 86.6 | 97.9 | 99.6 | 100.0 |
| u-FID | 14.4 | 33.7 | 56.2 | 106.2 | 218.8 |

By epoch 5 the digit is completely gone, but image quality is 15 times worse. The reason is built into the loss: the plasticity term has no lower bound, so if you keep minimising it, the model keeps moving away from where it started. In practice you stop early, after one or two epochs, where most of the forgetting has happened and quality is still close to the original.

$$\gamma$$ is the other control. At $$\gamma = 1$$ only the leash is active, so the model barely changes (PUL of 17% on MNIST, under 2% on CIFAR-10). At $$\gamma = 0$$ there is no leash. Values between 0.1 and 0.3 gave the best balance across datasets.

<div class="row">
  <div class="col-sm-6 mt-3 mt-md-0">{% include figure.html path="assets/img/blog/vdu/gamma-cifar-ship.png" class="img-fluid rounded z-depth-1" zoomable=true caption="Effect of γ when unlearning 'ship' on CIFAR-10: a stronger stability term lowers both PUL and u-FID." %}</div>
  <div class="col-sm-3 mt-3 mt-md-0">{% include figure.html path="assets/img/blog/vdu/mnist1-gamma0.png" class="img-fluid rounded z-depth-1" zoomable=true caption="γ = 0: digit 1 removed." %}</div>
  <div class="col-sm-3 mt-3 mt-md-0">{% include figure.html path="assets/img/blog/vdu/mnist1-gamma1.png" class="img-fluid rounded z-depth-1" zoomable=true caption="γ = 1: almost nothing forgotten." %}</div>
</div>

## Limitations

- **Gaussian mean-field weights.** This is what makes the loss simple, but real weight posteriors are correlated and not Gaussian. A richer posterior could help.
- **You need several checkpoints.** $$\mu^*$$ and $$\sigma^*$$ come from independently trained models. That is cheap for small DDPMs but not for a model the size of Stable Diffusion, unless the checkpoints already exist.
- **No natural stopping point.** Because the plasticity term is unbounded, the number of epochs is a real hyperparameter that needs tuning.

## Takeaway

The idea I find most satisfying here is the reframing: unlearning isn't "do gradient ascent and hope". Write down which posterior you actually want, see that Bayes' rule lets you reach it without the data you've lost, and let variational inference turn that into a loss. The two resulting terms, a push away from the forget set and a variance-weighted leash back to the original, explain both why the method works and where it breaks.

**Links:** [TMLR paper (OpenReview)](https://openreview.net/forum?id=mAHRgieyOV) · [arXiv](https://arxiv.org/abs/2510.04058)

## My role

- Worked on the variational formulation and the stability regularizer as a research intern (May–Nov 2024).
- Ran class-unlearning experiments on DDPMs and the comparisons with the baselines.
- Co-authored the NeurIPS 2024 Safe Generative AI workshop paper and the TMLR journal version.
