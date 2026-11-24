---
layout: post
title: "Fisher Information"
date: 2023-10-19
last_updated: 2026-11-24
description: "What Fisher information measures, why it is the variance of the score, and why a fair coin is the hardest coin to pin down."
tags: [statistics, probability, python]
categories: notes
giscus_comments: false
related_posts: false
toc:
  sidebar: left
---

*Updated November 2026. The first version of this note had the key relationship backwards: it said information falls as the variance of the score rises. It is the other way round. This version corrects that and adds a simulation that checks the claims.*

Fisher information measures how much a single observation $$y$$ tells you about an unknown parameter $$\theta$$ of the distribution that produced it. Toss a coin of unknown bias $$p$$ a hundred times: the count of heads carries information about $$p$$, and Fisher information puts a number on how much.

## The definition

Write the log-likelihood of one observation as $$\ell(\theta; y) = \log p(y \mid \theta)$$. Its derivative with respect to the parameter is the **score**:

$$s(\theta; y) = \frac{\partial}{\partial \theta} \log p(y \mid \theta)$$

The score depends on $$y$$, so before you observe anything it is a random variable. At the true parameter its mean is zero. Its variance is the Fisher information:

$$I(\theta) = \operatorname{Var}\big[s(\theta; Y)\big] = \mathbb{E}\big[s(\theta; Y)^2\big] = -\mathbb{E}\left[\frac{\partial^2}{\partial \theta^2} \log p(Y \mid \theta)\right]$$

The last form is the useful picture: information is the expected **curvature** of the log-likelihood at the true value. A sharply peaked log-likelihood pins the parameter down; a flat one does not.

For $$n$$ independent observations the information adds up to $$n I(\theta)$$.

## Two variances that are easy to mix up

This is where my first version went wrong. There are two different variances in play:

- the variance of the **data**, $$\operatorname{Var}(Y)$$, and
- the variance of the **score**, $$\operatorname{Var}(s)$$, which *is* the information.

For a Gaussian with known $$\sigma$$ and unknown mean $$\mu$$, the score is $$(y - \mu)/\sigma^2$$, so

$$I(\mu) = \frac{\operatorname{Var}(Y)}{\sigma^4} = \frac{1}{\sigma^2}$$

Noisier data means a *smaller* score variance and *less* information. A larger score variance means the log-likelihood reacts strongly to where the data landed, which is exactly what makes the data informative.

## Checking it numerically

{% include figure.html path="assets/img/blog/fisher-information/fig-02.png" class="img-fluid rounded z-depth-1" zoomable=true caption="Left: the score at the true mean has variance 1/σ², so the low-noise case (σ = 1) has nine times the information of σ = 3. Middle: log-likelihood curves from five datasets of 20 points each; low noise gives sharp peaks near the true μ = 0, high noise gives flat curves whose peaks wander. Right: for a coin, the variance of the estimated bias over 100,000 simulated runs sits on the Cramér–Rao bound." %}

The left panel samples 200,000 points for each $$\sigma$$ and computes the score at the true mean. The empirical variances come out at 1.002 and 0.111, against 1 and 1/9 from the formula.

The middle panel is the curvature view of the same fact. With $$\sigma = 1$$ every dataset gives a narrow log-likelihood peaked near zero. With $$\sigma = 3$$ the curves are flat and their maxima drift, so the data cannot tell you where $$\mu$$ is.

## What information buys you: the Cramér–Rao bound

Fisher information sets a floor on how well any unbiased estimator can do:

$$\operatorname{Var}(\hat\theta) \ge \frac{1}{n I(\theta)}$$

The inverse relationship lives here: more information, lower achievable **estimator** variance. I suspect that is where my original confusion came from.

## Back to the coin

For a single toss with bias $$p$$, the score is $$y/p - (1-y)/(1-p)$$ and the information works out to

$$I(p) = \frac{1}{p(1-p)}$$

This is smallest at $$p = 0.5$$. So a fair coin is the *hardest* coin to pin down: with 100 tosses the standard error of $$\hat p$$ is 0.05 at $$p = 0.5$$ but about 0.022 at $$p = 0.05$$. Each toss of a heavily biased coin is more surprising when it goes against the bias, and that surprise is information. The right panel confirms it: the simulated variance of $$\hat p = \text{heads}/n$$ matches $$p(1-p)/n$$ across the whole range, so for the coin the simple frequency estimate is as good as any unbiased estimator can be.

## Code

```python
import numpy as np

rng = np.random.default_rng(0)

# Gaussian with known sigma: the variance of the score at the true mean is 1/sigma^2
mu = 0.0
for sigma in (1.0, 3.0):
    y = rng.normal(mu, sigma, 200_000)
    score = (y - mu) / sigma**2
    print(f"sigma={sigma}: Var(score)={score.var():.3f}, 1/sigma^2={1 / sigma**2:.3f}")

# Coin: the variance of the MLE meets the Cramer-Rao bound p(1-p)/n
n = 100
for p in (0.05, 0.5):
    p_hat = rng.binomial(n, p, 100_000) / n
    print(f"p={p}: Var(p_hat)={p_hat.var():.5f}, bound={p * (1 - p) / n:.5f}")
```
