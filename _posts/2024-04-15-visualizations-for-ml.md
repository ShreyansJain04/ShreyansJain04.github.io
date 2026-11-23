---
layout: post
title: "Teaching Machine Learning Through Interactive Apps"
date: 2024-04-15   # TODO: verify; approximate project end date
description: "What we learned building blogs and Streamlit apps for Huffman coding, CORDIC, Fisher information and optimizers."
tags: [education, streamlit, optimization, information-theory]
categories: project-writeups
related_posts: false
toc:
  sidebar: left
---

Equations are a poor first contact with an algorithm. You can stare at the Adam update for an hour and still not know what changing $$\beta_2$$ does to the path of a ball rolling down a loss surface. In a CS299 project advised by Prof. [Nipun Batra](https://nipunbatra.github.io/), Vannsh Jani, Viraj Vekaria and I (with Kishan Ved on several topics) tried a different route: for each concept, write a blog post with from-scratch code, and build a small app so the reader can poke at it. This post collects what we built, what broke, and what we would do again. The project page is [here](/projects/vis-ml/).

## The recipe

Each topic followed the same loop:

1. Learn the concept well enough to implement it with NumPy only.
2. Write a Quarto blog post: motivation, maths, code, static plots.
3. Decide what the reader should be able to *change*, and expose exactly that in a Streamlit app.
4. Check the app against a trusted implementation.

Step 3 is the interesting one. A good app has two or three controls, not twelve. For the optimizer demo the controls are the optimizer, the learning rate, momentum and the starting point. Everything else is fixed so that the effect of each knob is legible.

## Optimizers: first lessons in being slow

Our first optimizer app redrew the loss curve after every epoch so the path would animate. It was unusable: plotting dominated the runtime and, worse, you only saw the final state because the screen refreshed too late. The fix was boring. Store the iterates in a list, plot once at the end, and give up the live animation. Later, a "Next Step" button on a contour plot restored the sense of motion by letting the reader advance the optimizer one step at a time:

$$\theta_{t+1} = \theta_t - \alpha\,\hat m_t / (\sqrt{\hat v_t}+\epsilon)$$

Seeing momentum overshoot a narrow valley and swing back teaches more than the paragraph describing it. We also added a one-dimensional function with a saddle, a local minimum and a global minimum, with a slider over learning rates that plays a video of Adam's path. Small learning rates get stuck; large ones skip the basin.

{% include figure.html path="assets/img/projects/vis-ml/contour.png" class="img-fluid rounded z-depth-1" zoomable=true caption="Stepping an optimizer with momentum on a contour plot." %}

As a sanity check we contributed from-scratch optimizers to the open-source wimpyML library and compared them against PyTorch. On MNIST, our RMSProp reached 97.11% test accuracy versus 97.31% for `torch.optim.RMSprop`, with nearly the same training time (about 115.7 s versus 113.3 s for 10 iterations). Matching a reference implementation is what lets you trust an explanatory app.

## Information theory: watching a tree grow

For Huffman coding, Kishan and I wrote the blog around a min-heap: repeatedly pop the two least frequent symbols, merge them, push the parent back. The app shows both the heap and the tree at each step, so a reader sees *why* frequent symbols end up near the root. The same machinery reappears in JPEG, where the quantized DCT coefficients are turned into (run, size) pairs and then Huffman-coded; a second app shows that encoding and decoding, and a Colab notebook walks through the whole pipeline: RGB to YCbCr, chroma subsampling, DCT, quantization, entropy coding.

{% include figure.html path="assets/img/projects/vis-ml/huffapp.png" class="img-fluid rounded z-depth-1" zoomable=true caption="The Huffman app at an intermediate step." %}

Vannsh took on the neighbouring topics: Shannon-Fano coding, noisy channel coding (with plots of bit error probability against message length and rate), mutual information, and SIREN, which stores an audio clip or an image as the weights of a small network with sinusoidal activations. SIRENs reconstruct beautifully and compress well, but the report is honest about the catch: training on one image takes on the order of an hour, so it is not practical without further optimization.

## Fisher information, Jacobians and CORDIC

My own topics were the ones where a picture changes the intuition most.

**Fisher information** measures how sensitive the likelihood is to a parameter $$\theta$$: high information means the data pins $$\theta$$ down tightly. The app lets you choose a distribution (normal, Poisson, binomial) and parameters and shows the resulting information.

**Change of variables** is the Jacobian determinant in

$$\iiint f(x,y,z)\,dx\,dy\,dz = \iiint f(u,v,w)\,|\det J|\,du\,dv\,dw .$$

The app takes a transformation and shows how a small patch of space is stretched, which makes $$|\det J|$$ feel like what it is: a local area (or volume) scale factor.

**CORDIC**, built with Viraj, rotates a vector toward a target angle by a sequence of shifts and adds, using no multiplications. The app draws the start vector, the current vector, a reference circle and the running sine and cosine; each press of "Next Iteration" applies one more rotation, and you can watch the red arrow close in on the blue one.

{% include figure.html path="assets/img/projects/vis-ml/cordic.png" class="img-fluid rounded z-depth-1" zoomable=true caption="CORDIC: the red vector converges on the target angle." %}

## What failed, and lessons

- **Too much interactivity.** Our design rule became two or three controls per app; every extra knob makes the effect of each one harder to see.
- **Speed is a feature.** Our per-epoch redraw showed that slow interaction kills exploration. Precompute, cache, and plot once.
- **The blog comes first.** In our view the apps work best with a written explanation that told the reader what to look for. An app without a question to answer is a toy.
- **Validate against a reference.** Autodiff, optimizers and Huffman codes were all checked against PyTorch or a library before we put them in front of readers.
- **Learning is the real output.** As the report notes, a lot of the early work on each task went into learning the concept before any visualization was possible.

## Links

- Project page: [Visualizations for Machine Learning](/projects/vis-ml/)
- Full write-up: [project notion page](https://intensedrop.notion.site/Visualizations-for-ML-951994a20ee447268626a82e4659c41f)
- Apps: [Fisher information](https://fisher.streamlit.app/), [Huffman](https://huffman.streamlit.app/), [JPEG coding](https://jpegcoding.streamlit.app/), [CORDIC](https://cordic.streamlit.app/), [change of variables](https://changeofvariables.streamlit.app/), [velocity viz](https://velocityviz.streamlit.app/), [noisy channel coding](https://noisychannelcoding.streamlit.app/)

Thanks to Prof. Nipun Batra for the opportunity to learn machine learning this way.
