---
layout: post
title: "One number explains 70% of short-term price moves: order flow imbalance, replicated"
date: 2026-11-22
description: "Replicating Cont, Kukanov and Stoikov's order flow imbalance on 53 million Binance top-of-book updates: OFI explains a median 70% of 10-second BTC price changes, trades about half that, and impact scales almost exactly as 1/depth."
tags: [market-microstructure, order-book, execution, quant]
categories: markets
related_posts: false
featured: 3
og_image: https://ShreyansJain04.github.io/assets/img/blog/ofi/fig1-scatter.png
toc:
  sidebar: left
---

> **TL;DR.** Cont, Kukanov and Stoikov (2014) showed that a single quantity built from changes at the best bid and ask, *order flow imbalance* (OFI), explains most short-horizon price moves, and that its effect scales inversely with market depth. I rebuilt it from scratch on two days of every top-of-book update for Binance's BTC and ETH perpetual futures, about 53 million updates in all. Over 10-second intervals OFI explains a median **70%** of BTC's mid-price variance and **67%** of ETH's, against roughly **35%** for trade imbalance. Impact scales with depth to the power **−1.07** (BTC) and **−1.02** (ETH), where theory says −1. A one-parameter version fitted on day one explains **54–55%** of day two out of sample. One result differs from the paper, and I think the difference is instructive.

## Why trades are the wrong thing to look at

The intuitive model of price impact is about trades: buyers lift the offer, sellers hit the bid, and net buying pushes the price up. It works, but only partly. A large share of what moves the best quotes never prints as a trade:

- a market maker cancels the bid and the queue thins out;
- a new sell order joins the offer and the ask queue gets heavier;
- a buyer improves the bid by a tick.

All of these are order flow, and all of them shift the balance at the top of the book. OFI counts them all with one bookkeeping rule.

## The definition

Let $$P^b_n, q^b_n$$ be the best bid price and size after the $$n$$-th book update, and $$P^a_n, q^a_n$$ the same for the ask. Each update contributes

$$
e_n = \mathbb{1}\{P^b_n \ge P^b_{n-1}\}\,q^b_n - \mathbb{1}\{P^b_n \le P^b_{n-1}\}\,q^b_{n-1} - \mathbb{1}\{P^a_n \le P^a_{n-1}\}\,q^a_n + \mathbb{1}\{P^a_n \ge P^a_{n-1}\}\,q^a_{n-1}
$$

This reads more simply than it looks. If the bid price is unchanged, the bid term is just the change in bid size: orders joining count positive, cancellations and fills negative. If the bid moves up, the whole new queue counts as fresh buying interest. If it moves down, the whole old queue counts as lost. The ask side mirrors it with the sign flipped. OFI over an interval is the sum of $$e_n$$, and the model is just

$$\Delta P_k = \beta\,\mathrm{OFI}_k + \varepsilon_k, \qquad \beta \approx \frac{c}{\text{depth}}$$

The second relation is the stylised fact: the same imbalance moves a thin book further than a thick one.

## Data

Binance publishes every change to the best bid and ask of its USDⓈ-M perpetual futures, with sizes, plus every aggregated trade with its aggressor side. I used BTCUSDT and ETHUSDT on 26 and 27 March 2024: 30.1 million book updates for BTC and 22.7 million for ETH. Both contracts trade with a one-tick spread about 95% of the time (0.1 USDT for BTC at around $70,000, 0.01 for ETH), so they behave like *large-tick* assets. That is the regime where queue dynamics matter most.

Following the paper, I split each day into 30-minute windows, summed OFI and the change in mid-price (in ticks) over 10-second intervals, and ran one regression per window: 96 regressions per contract. Trade imbalance (aggressive buy volume minus aggressive sell volume) gets the same treatment.

## Result 1: book events beat trades by about two to one

{% include figure.html path="assets/img/blog/ofi/fig1-scatter.png" class="img-fluid rounded z-depth-1" zoomable=true %}

This is one typical window, the one with the median OFI fit. The left panel is close to a line. The right panel is a cloud with a slope. Across all windows:

{% include figure.html path="assets/img/blog/ofi/fig2-r2.png" class="img-fluid rounded z-depth-1" zoomable=true %}

| 10-second intervals | Median R², OFI | Median R², trades |
|---|---|---|
| BTCUSDT | 0.70 | 0.36 |
| ETHUSDT | 0.67 | 0.32 |

The paper reports an average R² of about 65% for US equities. Crypto perpetuals in 2024 land in almost the same place, which is a nice sign that this is about how a limit order book works rather than about any one market.

The fit also depends on the time scale. Median R² for BTC is 0.58 at 1 second, 0.70 at 10 seconds and 0.65 at 60 seconds. My guess is that at very short horizons much of the mid-price change is noise around a single queue, and at longer ones deeper levels of the book start to matter.

## Result 2: impact is one over depth

{% include figure.html path="assets/img/blog/ofi/fig3-beta-depth.png" class="img-fluid rounded z-depth-1" zoomable=true %}

Each dot is one half-hour window: the fitted β against the average size at the best quotes. On log scales both contracts fall on lines with slopes of −1.07 and −1.02. That is the paper's central structural claim, and it holds here almost exactly. Halve the depth and the same order flow moves the price twice as far.

That turns the model into something with a single free parameter: $$\Delta P \approx c \cdot \mathrm{OFI}/\text{depth}$$. I fitted $$c$$ on 26 March and applied it unchanged to 27 March. Out of sample it explains **53.5%** of BTC's 10-second mid-price variance and **55.0%** of ETH's, essentially the same as refitting on day two (53.6% and 55.2%). There is nothing to overfit.

## Where my result differs from the paper

In the original study, adding trade imbalance to OFI barely improves the fit, because trades are already counted inside OFI as reductions in queue size. Here it helps a lot. On day two, pooled across windows, R² rises from 0.54 (BTC) and 0.55 (ETH) with OFI alone to **0.70 and 0.72 with OFI and trades together**.

I think there are two reasons, and both are worth knowing if you work with this kind of data:

1. **Sweeps.** In fast crypto markets a single aggressive order often clears the best level and keeps going. Top-of-book OFI sees the first queue disappear but not the depth consumed behind it. Trade volume does see it. Multi-level OFI, which sums imbalance over several levels (Xu, Gould and Howison 2019), is the natural fix.
2. **The feed is the top of book only.** The Binance file gives best bid and ask updates, not full depth. With level-2 data I would expect OFI alone to recover most of that gap.

## Why this matters for execution

- **Impact models should be state-dependent.** The same child order costs roughly twice as much when the book is half as deep, so a scheduler that ignores live depth leaves money on the table.
- **OFI is the right real-time signal.** A buy algorithm that sees strongly negative OFI is watching the bid side erode, and can wait. Strongly positive OFI says the price is about to move away, so posting passively risks not getting filled.
- **Trades alone are a lagging, partial view** of what moves prices. The book moves first.

## Method notes

- OFI is computed update by update from Binance's `bookTicker` files, sorted by transaction time. Empty 10-second intervals carry zero OFI and an unchanged mid.
- Trade imbalance uses `aggTrades`: `is_buyer_maker = true` means the seller was the aggressor.
- R² is computed separately in each 30-minute window, with an intercept. The out-of-sample test uses a single coefficient, $$c$$, with depth averaged per window.
- Code to download the data and reproduce every number and chart is [on GitHub](https://github.com/ShreyansJain04/ShreyansJain04.github.io/tree/master/assets/code/lob).

**Reference:** Rama Cont, Arseniy Kukanov and Sasha Stoikov, "The price impact of order book events", *Journal of Financial Econometrics* 12(1), 2014.
