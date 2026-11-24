---
layout: post
title: "Nifty made all its money while the market was closed"
date: 2026-11-24
description: "Ten years of NSE data split into overnight and market-hours returns: ₹100 held only overnight became ₹1,722, held only during market hours it became ₹18. Why it is an auction effect rather than a risk premium, why you mostly cannot harvest it, and why it faded after 2024."
tags: [market-microstructure, india, execution, quant]
categories: markets
related_posts: false
og_image: https://ShreyansJain04.github.io/assets/img/blog/overnight/fig1-nifty-split.png
featured: 1
toc:
  sidebar: left
---

> **TL;DR.** From January 2016 to November 2026 the Nifty 50 roughly tripled. Split each day at the opening bell and the picture changes completely: ₹100 held only overnight (close to next open) grew to **₹1,722**. ₹100 held only during market hours (open to close) shrank to **₹18**. The pattern is stronger in smaller stocks. It does not grow when the market is shut for longer, which rules out the obvious "pay for holding risk overnight" story and points at the opening auction instead. Delivery taxes make the overnight leg impossible to harvest directly. The intraday leg looked tradeable on paper, and the whole effect weakened sharply after November 2024.

{% include figure.html path="assets/img/blog/overnight/fig1-nifty-split.png" class="img-fluid rounded z-depth-1" zoomable=true %}

## The split

Every daily return can be cut in two at the opening bell:

$$\underbrace{\frac{C_t}{C_{t-1}}}_{\text{day}} = \underbrace{\frac{O_t}{C_{t-1}}}_{\text{overnight}} \times \underbrace{\frac{C_t}{O_t}}_{\text{market hours}}$$

I downloaded every daily index file and every daily equity bhavcopy that NSE publishes for January 2016 to November 2026: 2,687 trading days, 5.1 million stock-days. Then I chained the two pieces separately.

For the Nifty 50 the average overnight return before November 2024 was **+12.8 bp a day** (t = 9.2) and the average market-hours return was **−7.3 bp** (t = −4.0). The index gapped up on 69% of mornings. Compounded over a decade that is the chart above: buy-and-hold ended at ₹314, the overnight leg at ₹1,722 and the market-hours leg at ₹18.

Two definitions matter here, because they are where this effect lives:

- **The open** is the equilibrium price of NSE's [pre-open call auction](https://www.nseindia.com/products-services/equity-market-pre-open) (orders collected from 9:00, matched just before 9:15), not a first trade.
- **The close**, for most of this sample, was the volume-weighted average price of the last 30 minutes, not the last trade. From 3 August 2026, F&O stocks close through a [closing auction](https://www.sebi.gov.in/sebi_data/attachdocs/jan-2026/1768576287344.pdf) instead.

So "overnight" here means from the 3:00 to 3:30 pm average to the 9:15 auction price.

## It is not just the Nifty 50

{% include figure.html path="assets/img/blog/overnight/fig2-by-index.png" class="img-fluid rounded z-depth-1" zoomable=true %}

Every broad index shows the same split, and it grows as you move down the size ladder. The Nifty Smallcap 100 averaged +26.8 bp overnight and −22.1 bp in market hours, with a gap-up on 78% of mornings.

It also holds stock by stock, so it is not an artefact of how the index is computed. Each day I took the 100 most-traded stocks by trailing 60-day traded value (so the universe uses no future information) and averaged them equally. Before November 2024 they averaged **+19.1 bp overnight** and **−12.5 bp in market hours**, and about 65% of them opened above the previous close on a typical day.

## Three nights earn no more than one

The first explanation people reach for is risk: news arrives overnight, you cannot trade out of it, so holders demand a premium for sitting through the gap. That story makes a clear prediction. A weekend is three nights of closed market and three nights of news, so it should earn roughly three times a weeknight.

{% include figure.html path="assets/img/blog/overnight/fig3-weekend.png" class="img-fluid rounded z-depth-1" zoomable=true %}

It does not. A single weeknight earned 13.2 bp on average and a weekend earned 9.8 bp. The weekend estimate is noisier, but it is clearly nowhere near the ~40 bp the risk story needs. Whatever the overnight return is paying for, it is not the hours.

## Where the money actually goes

If the premium is not about time, it is about the moment the price is set. Sorting the 100 liquid stocks every day by the size of their overnight gap shows what happens next:

{% include figure.html path="assets/img/blog/overnight/fig4-gap-quintiles.png" class="img-fluid rounded z-depth-1" zoomable=true %}

The biggest gap-ups (+106 bp on average) give back a third of it by the close (−35 bp). The biggest gap-downs recover a little (+10 bp). The fade is not symmetric, though. Even the middle bucket, a perfectly ordinary +19 bp open, drifts down 12 bp during the day. The opening price is systematically set a little too high, and the continuous session spends the day correcting it.

The cleanest evidence that the opening print carries a premium comes from index ETFs. An ETF's fair overnight move is its index's overnight move, so any extra is a premium paid by whoever buys at the open.

{% include figure.html path="assets/img/blog/overnight/fig6-etf-premium.png" class="img-fluid rounded z-depth-1" zoomable=true %}

Until 2018 the ETFs opened in line with their indices. Then the retail investing boom arrived: NIFTYBEES opened a median of 40 bp above its index in 2020, 186 bp in 2021, and still about 25 bp in 2025 and 2026. If you buy an index ETF with a market order at 9:15, this is roughly what you are paying.

My reading of all this, which is an interpretation rather than something the data proves: the opening auction is where overnight enthusiasm, mostly buy orders, meets a market that has not yet fully woken up. Buy-side pressure sets the auction price slightly rich, and the liquidity providers who sell into it are paid the difference as the day goes on. The academic literature on US stocks (Lou, Polk and Skouras, among others) finds a similar tug of war between overnight and intraday investor clienteles. NSE's version is larger.

## Can you harvest it?

This is the part most "overnight returns" threads skip, and it is really an execution question.

**Long overnight (buy the close, sell the open): no.** Holding overnight turns each round trip into a delivery trade. Using current [NSE statutory rates](https://www.interactivebrokers.com/en/accounts/fees/indiaStockExchangeFees.php), that costs 0.1% STT on each side, 0.015% stamp duty on the buy, plus small exchange, SEBI and GST charges: about **22 bp a round trip**. The Nifty's 12.8 bp overnight edge is gone before you count a single tick of slippage.

**Short market hours (sell in the opening auction, buy back at the close): on paper, yes.** An intraday round trip pays 0.025% STT on the sell side only and 0.003% stamp duty: about **3.5 bp** all in. Shorting the 100-stock basket every day at the auction price and covering at the official close made **+9.0 bp a day after those costs** before November 2024, an annualised Sharpe ratio of about 1.3, with a 14% maximum drawdown.

I would not call that free money, for reasons that are all about execution:

- **You do not get the printed prices for free.** Your own sell order moves the auction price you are trying to capture. The 30-minute VWAP close can be tracked with a VWAP schedule, but only approximately.
- **Many retail brokers square off intraday positions before the closing window**, so a retail trader often cannot get the official close at all.
- **Outside the securities-lending market, shorting cash equities in India is intraday-only.** There is no carrying a position through a bad day.
- **A 50% hit rate with a 110 bp daily standard deviation** means a long, uncomfortable path to the average.

## It faded after 2024

{% include figure.html path="assets/img/blog/overnight/fig5-rolling.png" class="img-fluid rounded z-depth-1" zoomable=true %}

The Nifty 50's trailing-year overnight edge fell from around 13 bp to about 2 bp. Since 20 November 2024 it has averaged +2.3 bp overnight and −0.4 bp in market hours. The share of liquid stocks gapping up on a typical morning fell from 65% to 56%. The net paper return on the intraday short halved, to +4.8 bp a day.

The timing lines up with SEBI's [F&O curbs](https://www.business-standard.com/amp/markets/news/sebi-announces-six-key-changes-to-curb-speculation-in-derivatives-trading-124100101316_1.html), which took effect on 20 November 2024. They cut weekly index expiries to one per exchange and raised the minimum index-derivative contract from ₹5–10 lakh to ₹15 lakh. That is a coincidence in timing, not a demonstrated cause: two years is a short sample, and plenty else changed over the same period. The other date to watch is 3 August 2026, when the closing auction replaced the 30-minute VWAP close for F&O stocks. That changes the definition of the "close" itself. With only 77 trading days since then, it is too early to say what it did.

## What I'd check next

- **Intraday data.** With minute bars you could see whether the fade happens in the first 15 minutes, which would mean the auction is mispriced, or slowly all day, which would point to a steady flow.
- **Who is on the other side.** NSE publishes client-category turnover. If retail is a net buyer in the pre-open, the auction story firms up.
- **The closing auction.** If the overnight edge was partly an artefact of the VWAP close, it should shrink further for F&O stocks after August 2026 and not for the rest.

## Method and caveats

- **Data:** NSE's daily `ind_close_all` index files and daily CM bhavcopies, January 2016 to 23 November 2026. Three index files (4 June, 4 October and 4 November 2023) contained stale prices that reverse the next day; I dropped them. Index series with gaps longer than six days are skipped rather than bridged.
- **Stock-level returns:** overnight is open over NSE's previous close (which is adjusted for splits and bonuses), and market hours is close over open. EQ series only. I dropped rows where the open sits outside the day's high-low range and stock-days with moves over 20%.
- **Price returns.** Dividends are not added back. Ex-dividend drops land in the overnight leg, so they work *against* the overnight result.
- **Paper strategy.** Costs use current statutory rates and exclude brokerage, auction impact and slippage. This is a description of history, not investment advice.

The analysis code is [on GitHub](https://github.com/ShreyansJain04/ShreyansJain04.github.io/tree/master/assets/code/overnight); it downloads the public NSE files and reproduces every number and chart here.
