---
layout: page
title: "Variational Autoencoder on FPGA"
description: "16-bit fixed-point VAE for MNIST on a Nexys 4 FPGA, checked against a PyTorch reference."
img: assets/img/projects/fpga-vae/thumb.jpg
importance: 1
category: "Hardware & Embedded"
period: "Spring 2024"   # TODO: verify; Vivado project files in the repo are dated April 2024
links:
  code: https://github.com/ShreyansJain04/DigitalSystemsVAE
tags: [FPGA, Verilog, VAE, quantization, digital-systems]
---

<div class="tldr" markdown="1">
**Problem.** Run generative-model inference on a small FPGA instead of a GPU or CPU.  
**Approach.** Train a small VAE on MNIST in PyTorch, quantize it to 16-bit fixed point, and implement the inference path in Verilog on a Nexys 4 board, with weights held in on-chip block RAM.  
**Result.** A hardware VAE whose reconstructions were verified against the software model, with latency low enough for near-instantaneous inference.
</div>

## Overview

This was a course project for Digital Systems, mentored by Prof. Joycee Mekie at IIT Gandhinagar. The aim was to see how much of a neural generative model fits in a hobbyist-class FPGA once weights and activations are reduced to fixed-point numbers.

<!-- The integrator will add a block diagram here. -->

## Method

**Software reference.** `VAE_ds.ipynb` defines the model in PyTorch: a 784-400-200 ReLU encoder, a **2-dimensional latent space** (separate mean and log-variance heads), and a mirrored 2-200-400-784 decoder with a sigmoid output. Training is on MNIST with batch size 100 and the Adam optimizer.

**Fixed-point conversion.** Parameters and activations are quantized to 16-bit fixed point, which maps naturally onto the 16-bit data width of the FPGA's block RAM.

**Hardware.** The repository holds Vivado 2019.2 projects. The `bram_final` project wraps a Block Memory Generator IP (16-bit data in and out, 3-bit address, initialised from a `.coe` file) behind a small `bram.v` module, which is the memory interface used for weight storage. A further project archive includes a Python serial script, used to talk to the board from a host PC. <!-- TODO: verify exact datapath (MAC array, serial IO protocol) and board resource usage; not documented in the repo. -->

**Verification.** Reconstructed images from the fixed-point design were compared with the floating-point PyTorch model to confirm that quantization did not visibly hurt fidelity.

## Results

- Reconstruction fidelity verified against the PyTorch reference.
- Latency reduced enough for near-instantaneous inference on the board. <!-- TODO: verify; no cycle counts or latency numbers appear in the sources. -->

## My role
<!-- TODO: verify these role bullets with Shreyans; sources do not itemise individual contributions. -->

- Built and trained the PyTorch reference VAE and chose the quantization scheme.
- Implemented and tested the Verilog design in Vivado, including BRAM-based weight storage.
- Compared hardware outputs with the software model.
