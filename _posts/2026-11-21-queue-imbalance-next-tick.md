---
layout: post
title: "Will the next tick be up? Queue imbalance, a random-walk race, and the liquidity you can't see"
date: 2026-11-21
description: "The Cont–de Larrard view of the next price move as a race between two queues, tested on Binance BTC and ETH perpetuals: queue sizes call the next tick 66–68% of the time, the textbook model is overconfident, and one parameter, about one typical queue of unseen liquidity, fixes its calibration out of sample."
tags: [market-microstructure, order-book, execution, stochastic-processes, quant]
categories: markets
related_posts: false
featured: 3
og_image: https://ShreyansJain04.github.io/assets/img/blog/queue/fig1-pup.png
toc:
  sidebar: left
---

> **TL;DR.** In a market where the spread is one tick, the next price move is decided by which queue runs out first: the bid or the ask. Model the two queues as independent random walks and the probability of an up-move has a closed form, $$1 - \tfrac{2}{\pi}\arctan(q^a/q^b)$$. On Binance BTC and ETH perpetuals, queue sizes alone call the direction of the next mid move **68%** and **66%** of the time. The model gets the shape right but is far too confident at the extremes. Adding a single "hidden queue" of size $$k$$ to both sides fixes most of the miscalibration out of sample, and the fitted $$k$$ comes out almost exactly equal to the **median visible queue size**. An order book looks emptier than it is.

## The race

Take a large-tick market: the spread is one tick and the best bid and ask each have a queue of resting orders. The mid-price can only change when one of those queues is used up. If the ask queue is depleted, by buyers lifting it or sellers cancelling, the price ticks up. If the bid empties first, it ticks down.

Rama Cont and Adrien de Larrard (2013) built a whole theory of price dynamics on this idea. Each queue is a birth–death process: limit orders arrive, while cancellations and market orders remove size. With balanced order flow, each queue is roughly a random walk.

{% include figure.html path="assets/img/blog/queue/fig2-race.png" class="img-fluid rounded z-depth-1" zoomable=true %}

Plot the pair (bid size, ask size) as a point in the quarter-plane and the order book becomes a two-dimensional random walk. The next tick is determined by which axis the walk hits first.

## The closed form

For large queues, a random walk looks like Brownian motion, and the question becomes a classic one: starting at $$(q^b, q^a)$$, what is the probability that 2-D Brownian motion leaves the quarter-plane through the horizontal axis (ask empty) rather than the vertical one (bid empty)?

That probability is a harmonic function inside the quadrant, equal to 1 on one boundary and 0 on the other. The function that does this is linear in the polar angle $$\theta = \arctan(q^a/q^b)$$: it equals 1 at $$\theta = 0$$ and 0 at $$\theta = \pi/2$$. So

$$\mathbb{P}(\text{next move up}) = 1 - \frac{2}{\pi}\arctan\!\left(\frac{q^a}{q^b}\right).$$

Two properties make this attractive. It depends only on the *ratio* of the queues, so it needs no units. And it has no free parameters at all.

## The test

I used every best-bid/best-ask update for Binance's BTCUSDT and ETHUSDT perpetual futures on 26 and 27 March 2024. Once a second, whenever the spread was exactly one tick, I recorded the two queue sizes and then looked ahead to the next change in the mid-price: up or down. That gives about 171,000 observations per contract. The next move typically comes within a second (median 0.9 s).

{% include figure.html path="assets/img/blog/queue/fig1-pup.png" class="img-fluid rounded z-depth-1" zoomable=true %}

The orange dots are what actually happened on 27 March, binned by the queue imbalance $$I = q^b/(q^b + q^a)$$. The grey dashed line is the random-walk model.

**The signal is real.** Predicting "up" whenever the bid queue is bigger is right **68.5%** of the time for BTC and **65.6%** for ETH, against 50% for a coin flip. Few public signals are that strong at any horizon.

**The model is overconfident.** When the bid holds 98% of the visible size, the model says an up-move is near-certain. The market delivers one 85% of the time for BTC and 83% for ETH. At the other extreme it is the same story mirrored.

## The liquidity you can't see

Why would a nearly empty queue so often survive? A few reasons, and they all point the same way:

- **Queues get refilled.** When the bid is thin, new buy orders are attracted to it: joining a short queue means getting filled quickly. Huang, Lehalle and Rosenbaum's *queue-reactive* model builds exactly this dependence of order flow on queue size into the dynamics.
- **Hidden and iceberg orders.** Some size at the best price is not displayed at all.
- **Market makers re-quote.** A cancelled order is often replaced at the same price within milliseconds.

The simplest way to capture all of this is to pretend each queue has an extra, invisible amount $$k$$ behind it:

$$\mathbb{P}(\text{up}) = 1 - \frac{2}{\pi}\arctan\!\left(\frac{q^a + k}{q^b + k}\right)$$

I fitted $$k$$ on 26 March only, by minimising the Brier score, then tested on 27 March (the blue line above).

| | Fitted $$k$$ | Median visible queue | Brier score, day 2 (coin flip = 0.250) |
|---|---|---|---|
| BTCUSDT | 2.09 BTC | 1.90 BTC | 0.224 → **0.205** |
| ETHUSDT | 20.1 ETH | 17.0 ETH | 0.239 → **0.217** |

The improvement in calibration holds out of sample. The fitted $$k$$ is not some arbitrary number, either. For both contracts it comes out 10–18% above the median visible queue. A rough way to read that: **every queue behaves as if about one typical queue's worth of liquidity is waiting behind it.** Hit rates do not change, because adding $$k$$ does not change which side is bigger. What changes is how much you should trust the call, and for sizing or deciding when to cross the spread, that is what matters.

## Try it

<div id="qi-app" style="margin:1.25rem 0;padding:1rem;border:1px solid rgba(128,128,128,0.3);border-radius:8px;">
  <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:0.75rem 1.5rem;">
    <label>Bid queue <b id="qi-b-v" style="float:right"></b><input id="qi-b" type="range" min="0.05" max="10" step="0.05" value="3" style="width:100%"></label>
    <label>Ask queue <b id="qi-a-v" style="float:right"></b><input id="qi-a" type="range" min="0.05" max="10" step="0.05" value="1" style="width:100%"></label>
    <label>Hidden queue k <b id="qi-k-v" style="float:right"></b><input id="qi-k" type="range" min="0" max="5" step="0.05" value="2.1" style="width:100%"></label>
  </div>
  <p style="margin:0.75rem 0 0;font-size:1.05rem;">Model, visible queues only: <b id="qi-p0"></b> &nbsp;·&nbsp; with hidden queue: <b id="qi-p1"></b> chance the next tick is up</p>
  <p style="margin:0.25rem 0 0;font-size:0.85rem;opacity:0.75;">Units are BTC; the default k is the value fitted on BTCUSDT.</p>
</div>
<script>
(function () {
  function $(i) { return document.getElementById(i); }
  function p(b, a, k) { return 1 - (2 / Math.PI) * Math.atan((a + k) / (b + k)); }
  function draw() {
    var b = +$("qi-b").value, a = +$("qi-a").value, k = +$("qi-k").value;
    $("qi-b-v").textContent = b.toFixed(2); $("qi-a-v").textContent = a.toFixed(2); $("qi-k-v").textContent = k.toFixed(2);
    $("qi-p0").textContent = (100 * p(b, a, 0)).toFixed(0) + "%"; $("qi-p1").textContent = (100 * p(b, a, k)).toFixed(0) + "%";
  }
  ["qi-b", "qi-a", "qi-k"].forEach(function (i) { $(i).addEventListener("input", draw); });
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", draw); else draw();
})();
</script>

## What an execution algorithm does with this

Say you need to buy. You can post on the bid and wait, or cross the spread and pay a tick.

- **Big bid, small ask (high $$I$$):** the price is likely to tick up before your passive order fills. Waiting risks chasing the price, so crossing is often cheaper.
- **Small bid, big ask (low $$I$$):** the price is likely to tick down to you. Posting, or simply waiting, is the better bet.

Cont and Kukanov (2017) turn this into a full optimal order-placement problem, splitting an order across limit and market orders and across venues. The queue race is the building block underneath it. The lesson from the data is to use a *calibrated* version: the textbook model would have you crossing far too eagerly when one queue looks empty.

## Caveats

- **Two days, two contracts, one venue.** Crypto perpetuals are a convenient public laboratory, but equities with different tick sizes and fee structures will give different numbers.
- **Top of book only.** Binance's file shows the best queues, not the depth behind them, and the diffusion formula ignores everything beyond level one.
- **Sampling.** I sampled the book once a second while the spread was one tick, so observations are not independent, but with 171,000 per contract the binned probabilities are tight.

Code to download the data and reproduce every number and chart is [on GitHub](https://github.com/ShreyansJain04/ShreyansJain04.github.io/tree/master/assets/code/lob).

**References:** Rama Cont and Adrien de Larrard, "Price dynamics in a Markovian limit order market", *SIAM Journal on Financial Mathematics* 4(1), 2013. Weibing Huang, Charles-Albert Lehalle and Mathieu Rosenbaum, "Simulating and analyzing order book data: the queue-reactive model", *Journal of the American Statistical Association* 110(509), 2015. Rama Cont and Arseniy Kukanov, "Optimal order placement in limit order markets", *Quantitative Finance* 17(1), 2017.
