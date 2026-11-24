---
layout: post
title: "The life of an order: a film-length tour of the execution business"
date: 2026-11-24 22:00:00 +0530
description: "Follow one 1.2-million-share order from a portfolio manager's decision to the next morning's cost report: the buy-side desk, FIX, risk checks, the algo, the smart order router, exchanges, dark pools, market makers, the closing auction, settlement and TCA. Every actor, every incentive, with a simulated day and real market-structure numbers."
tags: [execution, market-microstructure, explainer, quant]
categories: markets
related_posts: false
featured: 1
og_image: https://ShreyansJain04.github.io/assets/img/blog/life-of-an-order/fig2-the-day.png
toc:
  sidebar: left
---

> **TL;DR.** Buying 1.2 million shares of a stock is not one decision. It is a day-long chain of handoffs: portfolio manager → buy-side trader → broker → algorithm → smart order router → dozens of venues → market makers and other investors on the other side → clearing → a report card the next morning. Each link has its own incentives and its own way of leaking money. This post follows one fictional order through all of it, scene by scene. The numbers about market structure are real and sourced. The order and the stock are invented, and its day is a simulation, so you can see every moving part at once.

---

## Cold open — 3:59:59 p.m.

A trading floor that is mostly screens. On one of them, a number flickers: *imbalance to buy, 412,000 shares*. Across the US, index funds, ETF market makers and pension rebalancers have spent the last ten minutes sending orders into the **closing auction**, the single largest liquidity event of the day. On the NYSE alone it matches roughly $44 billion on a normal day, and far more on index rebalance days. ([NYSE](https://www.nyse.com/research/insights/the-busiest-room-on-wall-street))

Our order will not be in it. To understand why, we have to go back to 7:02 this morning.

---

## The cast

Every execution story has the same characters. Here is the map we will walk:

<div style="margin:1.5rem 0;overflow-x:auto;">
<svg viewBox="0 0 900 640" style="width:100%;min-width:640px;height:auto;font-family:inherit;" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Map of an order's journey from portfolio manager to venues and back">
  <defs>
    <marker id="arB" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="#2a78d6"/></marker>
    <marker id="arO" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="#eb6834"/></marker>
  </defs>
  <style>
    .bx{fill:none;stroke:currentColor;stroke-opacity:.35;stroke-width:1.5}
    .band{fill:currentColor;fill-opacity:.04;stroke:none}
    .t{fill:currentColor;font-size:15px;font-weight:600}
    .s{fill:currentColor;fill-opacity:.7;font-size:12px}
    .lab{fill:currentColor;fill-opacity:.55;font-size:12px;letter-spacing:.08em}
    .fB{stroke:#2a78d6;stroke-width:2;fill:none}
    .fO{stroke:#eb6834;stroke-width:2;fill:none;stroke-dasharray:6 4}
  </style>
  <rect class="band" x="10" y="10" width="880" height="120" rx="10"/><text class="lab" x="22" y="30">BUY SIDE</text>
  <rect class="band" x="10" y="145" width="880" height="140" rx="10"/><text class="lab" x="22" y="165">BROKER (SELL SIDE, AGENCY)</text>
  <rect class="band" x="10" y="300" width="880" height="140" rx="10"/><text class="lab" x="22" y="320">VENUES</text>
  <rect class="band" x="10" y="455" width="880" height="80" rx="10"/><text class="lab" x="22" y="475">THE OTHER SIDE OF THE TRADE</text>
  <rect class="band" x="10" y="550" width="880" height="80" rx="10"/><text class="lab" x="22" y="570">AFTER THE TRADE</text>

  <rect class="bx" x="40" y="45" width="210" height="70" rx="8"/><text class="t" x="55" y="73">Portfolio manager</text><text class="s" x="55" y="95">decides what to own</text>
  <rect class="bx" x="340" y="45" width="230" height="70" rx="8"/><text class="t" x="355" y="73">Buy-side trader</text><text class="s" x="355" y="95">OMS / EMS, picks broker and algo</text>
  <rect class="bx" x="660" y="45" width="210" height="70" rx="8"/><text class="t" x="675" y="73">Pre-trade TCA</text><text class="s" x="675" y="95">"what will this cost?"</text>

  <rect class="bx" x="40" y="185" width="200" height="85" rx="8"/><text class="t" x="55" y="212">Sales trader</text><text class="s" x="55" y="232">human coverage, blocks,</text><text class="s" x="55" y="250">risk bids</text>
  <rect class="bx" x="270" y="185" width="190" height="85" rx="8"/><text class="t" x="285" y="212">Risk checks</text><text class="s" x="285" y="232">limits, collars,</text><text class="s" x="285" y="250">"fat finger" stops</text>
  <rect class="bx" x="490" y="185" width="180" height="85" rx="8"/><text class="t" x="505" y="212">Algo engine</text><text class="s" x="505" y="232">parent → child orders,</text><text class="s" x="505" y="250">when and how much</text>
  <rect class="bx" x="700" y="185" width="170" height="85" rx="8"/><text class="t" x="715" y="212">Smart order</text><text class="t" x="715" y="230">router</text><text class="s" x="715" y="252">where to send</text>

  <rect class="bx" x="40" y="340" width="190" height="85" rx="8"/><text class="t" x="55" y="367">Lit exchanges</text><text class="s" x="55" y="387">NYSE, Nasdaq, Cboe, IEX,</text><text class="s" x="55" y="405">MEMX, TXSE …</text>
  <rect class="bx" x="250" y="340" width="190" height="85" rx="8"/><text class="t" x="265" y="367">Dark pools (ATSs)</text><text class="s" x="265" y="387">midpoint, no displayed</text><text class="s" x="265" y="405">quotes</text>
  <rect class="bx" x="460" y="340" width="190" height="85" rx="8"/><text class="t" x="475" y="367">Single-dealer</text><text class="t" x="475" y="385">platforms</text><text class="s" x="475" y="405">a dealer's own liquidity</text>
  <rect class="bx" x="670" y="340" width="200" height="85" rx="8"/><text class="t" x="685" y="367">Auctions</text><text class="s" x="685" y="387">open, close, periodic,</text><text class="s" x="685" y="405">conditional blocks</text>

  <rect class="bx" x="40" y="482" width="260" height="44" rx="8"/><text class="t" x="55" y="509">Market makers / HFT</text>
  <rect class="bx" x="320" y="482" width="260" height="44" rx="8"/><text class="t" x="335" y="509">Other institutions</text>
  <rect class="bx" x="600" y="482" width="270" height="44" rx="8"/><text class="t" x="615" y="509">Retail flow (via wholesalers)</text>

  <rect class="bx" x="40" y="578" width="250" height="44" rx="8"/><text class="t" x="55" y="605">Clearing &amp; settlement</text>
  <rect class="bx" x="320" y="578" width="250" height="44" rx="8"/><text class="t" x="335" y="605">Regulatory reporting</text>
  <rect class="bx" x="600" y="578" width="270" height="44" rx="8"/><text class="t" x="615" y="605">Post-trade TCA</text>

  <path class="fB" d="M250,80 H336" marker-end="url(#arB)"/>
  <path class="fB" d="M455,115 V150 H365 V181" marker-end="url(#arB)"/>
  <path class="fB" d="M460,227 H486" marker-end="url(#arB)"/>
  <path class="fB" d="M670,227 H696" marker-end="url(#arB)"/>
  <path class="fB" d="M240,227 H266" marker-end="url(#arB)"/>
  <path class="fB" d="M785,270 V300 H135 V336" marker-end="url(#arB)"/>
  <path class="fB" d="M345,300 V336" marker-end="url(#arB)"/>
  <path class="fB" d="M555,300 V336" marker-end="url(#arB)"/>
  <path class="fB" d="M770,300 V336" marker-end="url(#arB)"/>
  <path class="fO" d="M735,600 H880 V80 H874" marker-end="url(#arO)"/>
  <text class="s" x="620" y="293" style="fill:#2a78d6;fill-opacity:1">orders flow down</text>
  <text class="s" x="742" y="570" style="fill:#eb6834;fill-opacity:1">… the report card flows back up</text>
</svg>
</div>

One distinction to hold onto: the **broker** in this story is acting as an **agent**. It works the client's order and earns a commission, but it does not own the risk of the shares. That is different from a broker acting as **principal**, trading against the client from its own book. Much of the drama comes from that line being crossed, or not.

---

## Scene 1 — 7:02 a.m. The decision

*INT. NORTHFIELD PENSION FUND (FICTIONAL). A portfolio manager reads overnight research.*

The PM decides to raise the fund's position in Meridian Robotics (a fictional ticker, MRDN) by **1.2 million shares**. Yesterday's close was **$84.00**, so on paper this is a $100.8 million purchase. That paper number is called the **decision price**, and it is the anchor for everything that follows.

Here is the problem. MRDN trades about **6 million shares a day**, so the order is **20% of a full day's volume**. If you try to buy that much at once, you *are* the market. Every share you take uses up the cheapest available sellers, and the price walks away from you.

The most robust empirical regularity in this business, the **square-root law of market impact**, puts a rough number on it:

$$\text{impact} \;\approx\; Y \,\sigma_{\text{daily}} \sqrt{\frac{Q}{V}}$$

Here $$Q$$ is the order size, $$V$$ is daily volume, $$\sigma$$ is daily volatility, and $$Y$$ is a constant of order one. With σ = 2% and Q/V = 0.2, that is about **89 basis points**, or around **75 cents a share**, which is **$750,000** of cost on this one order. Nobody has written a cheque for it, but it will come out of the fund's return all the same.

The PM writes the order: *buy 1.2M MRDN, limit $85.00, get it done today if you can*. The limit is the PM's line in the sand: above $85 the trade stops being worth it. Remember it.

---

## Scene 2 — 8:15 a.m. The buy-side desk

*INT. NORTHFIELD TRADING DESK. Two screens: the OMS and the EMS.*

The order lands in the **OMS** (order management system), the fund's book of record for positions, compliance and allocations. The buy-side trader pulls it into the **EMS** (execution management system), the cockpit that connects to brokers and their algorithms.

The trader now makes the choices that will matter most, and most of them happen before a single share trades:

- **Which broker?** Many funds run a **broker review** or an **algo wheel**, which routes orders across a panel of brokers and scores them on results. It keeps everyone honest and generates data.
- **High-touch or low-touch?** High-touch means a human **sales trader** at the broker works the order, hunts for natural blocks and can offer to take risk. Low-touch means the trader picks an algorithm and sends the order electronically.
- **Which benchmark?** This choice determines what "good" will mean tomorrow morning:
  - **Arrival price / implementation shortfall (IS):** the price when the order arrived. It rewards urgency, and it is what the PM actually cares about.
  - **VWAP:** the volume-weighted average price over the day. It rewards blending in, and it is easy to beat by simply trading in line with the volume curve.
  - **Close:** what index funds care about, because their benchmark is valued at the close.
- **How urgent?** Information decays. If the PM's idea is right, the price will move with or without our help. That is the **alpha** we will be racing.

Our trader chooses an IS-style algorithm at medium urgency, caps participation at **25% of volume** so the order does not dominate the tape, and tells the broker's sales trader to watch for blocks.

> *A note on what clients pay for.* In Europe, MiFID II forced research payments to be separated from execution commissions in 2018, so an execution commission increasingly has to be justified by execution quality alone. That is one reason transaction cost analysis grew from a back-office report into a product.

---

## Scene 3 — 9:41 a.m. The wire

*EXT. A FIX SESSION. Text scrolls.*

The order travels from the fund to the broker as a **FIX** message, the lingua franca of electronic trading. A simplified *New Order – Single*:

```
8=FIX.4.4 | 35=D | 49=NORTHFIELD | 56=BROKER | 11=NF-20261125-0042
55=MRDN | 54=1 | 38=1200000 | 40=2 | 44=85.00 | 59=0
6401=IS | 6403=MEDIUM | 6404=25      <- broker-specific algo parameters
```

Tag 35=D means "new order". 54=1 is "buy", 38 is the quantity, 40=2 is "limit", 44 is the limit price and 59=0 is "day". The 6000-range tags are where each broker defines its own algo parameters. Every fill will come back as an **execution report** (35=8), carrying the fill quantity (tag 32), price (31) and the venue where it happened (30). That stream of execution reports *is* the trade, as far as the fund's systems are concerned.

Before the broker sends a single share to market, the order passes **pre-trade risk checks**. In the US these are required by the SEC's **Market Access Rule (15c3-5)**: credit limits, maximum order sizes, price collars, restricted lists, duplicate-order detection. They exist because of days like **1 August 2012**, when Knight Capital's faulty deployment sent millions of unintended orders in 45 minutes and lost about $440 million. In execution, the most expensive bug is the one that trades.

By 9:41 the stock has drifted to **$84.21**. We have not bought anything and are already 21 cents behind the decision price. That gap has a name, **delay cost**, and it will show up on tomorrow's report.

---

## Scene 4 — The algorithm's brain

*INT. A DATA CENTRE IN NEW JERSEY. Racks of servers hum.*

The algorithm receives one **parent order**, 1.2 million shares. It will never send that order to the market. Instead it slices it into thousands of **child orders**, typically a few hundred shares each, and it answers three questions continuously.

**1. How much should I have done by now? (The scheduler.)** Volume in US stocks follows a **U-shape**: heavy at the open, quiet at lunch, very heavy into the close. A VWAP-style scheduler forecasts that curve for MRDN today and aims to trade in proportion to it. An IS-style scheduler bends the curve forward to reduce exposure to price drift. This is the Almgren–Chriss trade-off between impact and timing risk, which I built an [interactive explorer]({% post_url 2026-11-23-almgren-chriss-explorer %}) for. A participation cap (25% here) stops the schedule from ever dominating the market.

**2. Passive or aggressive? (The micro-placer.)** For each slice: should I post a bid and wait to be filled, earning the spread but risking not getting filled, or cross the spread and pay it for certainty? The answer depends on what the order book is doing right now:
- If buying pressure at the top of the book is building, prices are about to move up and waiting is expensive. That is the [order flow imbalance]({% post_url 2026-11-22-order-flow-imbalance %}) signal.
- If the bid queue is small and the ask queue is big, the price is likely to tick down to you, so be patient. That is the [queue imbalance]({% post_url 2026-11-21-queue-imbalance-next-tick %}) signal.
- If you are behind schedule, you have to catch up.

**3. Am I being watched? (Anti-gaming.)** A predictable algorithm is a gift to anyone hunting for large orders. Real algos randomise child-order sizes and timing, avoid posting the same size at the same price every 30 seconds, and stop sending to venues where their fills are consistently followed by adverse price moves.

---

## Scene 5 — The router and the map of venues

*INT. SAME DATA CENTRE. A single child order, 300 shares, needs a destination.*

The algo decides *when* and *how much*. The **smart order router (SOR)** decides *where*. In the US that is a hard question, because a single stock trades in dozens of places at once.

**Lit exchanges.** These are the venues with displayed quotes: the NYSE family, the Nasdaq family, the Cboe family, IEX, MEMX, and since July 2026 the Texas Stock Exchange, the first new fully integrated US exchange to launch in decades. ([Venable](https://www.venable.com/insights/publications/2026/07/texas-stock-exchange-opens-for-trading)) They are tied together by **Regulation NMS**:

- The best displayed bid and offer across all exchanges form the **NBBO**.
- The **order protection rule (Rule 611)** forbids trading through a better displayed price elsewhere.
- An **intermarket sweep order (ISO)** lets a router hit several venues at once while taking responsibility for clearing the better prices itself.

**Fees shape the routing.** Most exchanges run **maker–taker** pricing: pay to take liquidity, get a rebate for providing it. "Inverted" venues flip that. Rebates change where liquidity rests, so they change where a router should look. In 2024 the SEC cut the cap on access fees for stocks above $1 to **$0.001 a share** (10 mils) and introduced a **half-penny tick** for tightly quoted stocks. Both became mandatory on **3 November 2025**. ([SEC](https://sec.gov/newsroom/press-releases/2024-137), [Deloitte](https://www2.deloitte.com/content/dam/Deloitte/us/Documents/Advisory/us-advisory-sec-reg-nms-updates-october-2024.pdf))

**Off-exchange.** This is where the US differs most from the textbook picture. In 2025, for the first time, trades reported away from exchanges made up **50.6%** of all US equity volume. ([Cboe](https://www.cboe.com/insights/posts/2025-u-s-equities-year-in-review)) That off-exchange half has very different parts:

- **Dark pools (ATSs):** about **17.7%** of total volume in 2025. Nothing is displayed; orders usually match at the NBBO midpoint, so both sides save half the spread. ([Rosenblatt](https://www.rblt.com/market-structure-reports/let-there-be-light-us-edition-75))
- **Single-dealer platforms:** a broker or market maker offering its own liquidity directly to clients.
- **Retail wholesalers:** firms that buy retail brokers' order flow and fill it themselves, often with small price improvement. In the first half of 2025, this was roughly three quarters of all off-exchange volume. ([Cacciatore](https://ejcacciatore.github.io/ATS-Charts/off_exchange_bifurcation_h1_2025.html))

**Speed matters, and so does the data feed.** The NBBO is published by the public **SIP** feed, but professionals take **direct feeds** from each exchange, which arrive faster. IEX's famous **350-microsecond speed bump** exists precisely to stop faster traders from picking off orders priced on slightly stale information.

So our router weighs, for each child: displayed price, fees and rebates, fill probability, queue position, latency, and one more thing that matters most, which is **what happens to the price after you trade there**.

That last measure is the **markout**: the move in the mid-price a few seconds or minutes after your fill. If buys on a venue are reliably followed by the price *falling*, the people you traded with there knew something. That venue is **toxic** for you. Markouts are how routers learn, venue by venue, who they are really trading against.

---

## Scene 6 — 11:20 a.m. The block

*INT. BROKER'S TRADING FLOOR. A sales trader's screen flashes: CONDITIONAL MATCH.*

Since 9:41 the algo has been resting **conditional orders** in block-crossing venues: a non-binding signal that says *I would buy a large size here*. Somewhere, another institution — maybe a fund trimming its own MRDN position — has done the same on the sell side. The venue matches the two conditionals and asks both sides to **firm up**. Both do, within milliseconds.

**150,000 shares** trade at the midpoint, $84.50, in a single print. That is an eighth of our order in one fill, with zero spread paid and almost no footprint on the lit market.

This is the best thing that can happen to a large order, and it is getting rarer: block-focused dark pools hit record-low market share in 2025. ([Rosenblatt](https://www.rblt.com/market-structure-reports/let-there-be-light-us-edition-75)) Natural counterparties are scarce, and every conditional order is a small leak of information. A venue that lets participants "fish" with conditionals they never intend to firm up is a venue the router learns to avoid.

The algo **re-plans**: with 150,000 fewer shares to buy, the rest of the schedule shrinks.

---

## Scene 7 — The other side of the trade

*INT. A MARKET MAKER'S OFFICE. Rows of quiet engineers.*

Every share we buy, someone sells. Most of the time, on lit markets, that someone is a **market maker**: a firm posting bids and offers all day, earning the spread while trying to end the day flat.

Why does the spread exist at all? Microstructure theory's classic answer (Glosten and Milgrom, Kyle, both 1985) is **adverse selection**. Some traders know more than the market maker. The spread is the toll that uninformed traders pay so that the market maker can afford to lose to informed ones. Add inventory risk and operating costs, and you have the price of immediacy.

From the market maker's chair, our pension fund looks *informed*: a large, persistent buyer whose buying will push the price up. If they can detect us, they will quote less size on the offer, move their offers up, and lean their inventory long. That is not illegal and not even malicious. It is simply rational pricing of a buyer who has not finished buying. Everything our algo does — randomisation, venue selection, conditional orders, the participation cap — is an attempt not to look like what we are.

There is a subtler point too. The same market makers are an enormous help on an ordinary day: they are why a 300-share child order costs a fraction of a cent instead of a nickel. Execution is less a war against them than a negotiation over how much our information is worth.

---

## Scene 8 — 1:00 p.m. The quiet middle

*INT. BROKER'S TRADING FLOOR. Lunch. Volume is at its daily low.*

The sales trader calls the client:

> "You're 53% done at an average of $84.46. The stock's up 56 cents since arrival, and the block put you ahead of a straight VWAP schedule. Do you want to stay at this pace, slow down to see if it comes back, or speed up?"

This is the human layer that algorithms have not replaced. The trader also knows a few things the algo cannot: there is a sector conference this afternoon, and the PM really does want the full position.

There is one more tool. The broker can offer a **risk bid**: take the remaining shares onto its own book *right now* at a guaranteed price, say a few cents over the current offer, and then work them out itself. At that moment the broker switches from agent to **principal**. The client pays for certainty, and the broker is paid for absorbing risk. Program-trading desks do this for whole portfolios at once.

Northfield declines. The algo carries on.

---

## Scene 9 — 3:04 p.m. The limit

*INT. NORTHFIELD TRADING DESK. A price ticks to $85.01.*

MRDN finally crosses the PM's **$85.00 limit**. The algo stops buying. Every share it has not bought is now **opportunity cost**: the return the fund wanted and will not get. The price wobbles back below $85 for a few minutes and the algo picks up 20,800 more shares, then MRDN closes the day at **$85.10**.

{% include figure.html path="assets/img/blog/life-of-an-order/fig2-the-day.png" class="img-fluid rounded z-depth-1" zoomable=true %}

This is the whole day in one picture, simulated. The grey bars are the market's U-shaped volume. The blue bars are our child orders, tracking the curve at roughly 18% of volume, with the single tall spike of the 11:20 block. Above them is the price, and our fills are scattered along it.

Was stopping at the limit right? It depends entirely on *why* the price rose. If MRDN rose on the same thesis the PM had, chasing it would have been the right call and the limit cost money. If it rose because *we* were pushing it, chasing would have meant paying our own impact. The limit is the PM's answer to a question the trader cannot answer alone.

---

## Scene 10 — 3:50 p.m. The closing auction

*Back to the cold open. Imbalance messages every second.*

From 3:50 p.m. the listing exchanges publish **imbalance data** for the closing auction: how many shares are waiting to buy or sell at the close, and at what indicative price. ([BMLL](https://www.bmlltech.com/news/market-insight/into-the-close-unpacking-u-s-closing-auction-dynamics-and-the-impact-of-the-russell-reconstitution)) Participants respond with **market-on-close** and **limit-on-close** orders. On the NYSE, floor brokers' discretionary **D-orders** now account for more than half of closing-auction volume. ([NYSE](https://www.nyse.com/research/insights/the-busiest-room-on-wall-street))

The close matters because so much of the world is *priced* at it: index funds, NAVs, derivatives settlements, performance benchmarks. Passive investing has made it steadily bigger. As of December 2025, Developed Europe put about **35%** of daily volume through the closing auction, against about **15%** in the US. ([State Street](https://www.ssga.com/us/en/institutional/insights/how-passive-investing-reshaping-microstructure))

A VWAP or IS algorithm will usually plan to do a slice of the order in the close, because that is where the liquidity is. Ours had reserved about an eighth of the order for it. But the indicative closing price is above $85, so our limit keeps us out.

---

## Scene 11 — 4:00 p.m. onwards. The plumbing

*INT. OPERATIONS. Quieter, but no less important.*

The trading is over. The trade is not.

- **Allocations.** Northfield bought for several underlying funds, so the 905,500 shares are split across accounts and confirmed with the broker.
- **Clearing.** In the US, trades are novated to **NSCC**, the central counterparty. NSCC becomes the buyer to every seller and the seller to every buyer, so nobody bears the default risk of whoever happened to be on the other side.
- **Settlement.** Shares and cash change hands at **DTC**. Since May 2024 that happens one business day after the trade (**T+1**). India moved to T+1 in 2023.
- **Reporting.** Every order, route, modification and fill is reported to the **Consolidated Audit Trail**, so regulators can reconstruct the day to the microsecond.

---

## Scene 12 — The next morning. The report card

*INT. NORTHFIELD, 8:00 a.m. Coffee. A TCA report.*

**Transaction cost analysis (TCA)** asks what this trade actually cost, and why. The standard frame is **implementation shortfall** (Perold, 1988): the difference between the return of the *paper* portfolio, filled instantly at the decision price, and the *real* one.

{% include figure.html path="assets/img/blog/life-of-an-order/fig3-shortfall.png" class="img-fluid rounded z-depth-1" zoomable=true %}

For our simulated order, the shortfall breaks into three pieces:

| Component | What it measures | Cost |
|---|---|---|
| **Delay** | Price moved from $84.00 (decision) to $84.21 (arrival at broker) | 18.9 bp |
| **Execution** | Average fill $84.573 against the $84.21 arrival price, on 905,500 shares | 32.6 bp |
| **Opportunity** | 294,500 shares never bought, while the stock closed at $85.10 | 32.1 bp |
| **Total** | Against $100.8M of decision value | **83.6 bp** |

Now look at the same trade through a different lens. The day's VWAP was **$84.650**. Our average was **$84.573**. **Against VWAP, the broker beat the benchmark by 9.2 basis points.** The broker's report card is green.

Both statements are true at once. Against VWAP the execution was good. Against the decision, the fund lost 83.6 basis points, and a third of that came from shares it never bought. This is the most important idea in the business:

> **A benchmark is a choice about what counts as your fault.** VWAP forgives you for the market moving and for not finishing. Implementation shortfall forgives you for nothing. Choose it before you trade, not after.

Good TCA goes further. It looks at **markouts by venue**: which venues' fills went bad. It compares **realised against predicted cost**: was 83.6 bp better or worse than the pre-trade model's 89 bp for this kind of order? And it **aggregates over hundreds of orders**, because a single order's result is mostly luck. Brokers are judged on that aggregate, and under US rules (FINRA Rule 5310) and European ones, brokers owe their clients **best execution** and have to be able to show it.

---

## Epilogue — the same film in other cities

**London and Europe.** Trading is fragmented across national exchanges, multilateral venues, **systematic internalisers** (bank dealing books acting as venues) and **periodic auctions** that match orders every few milliseconds. Dark trading under the reference-price waiver has been capped since October 2025 at a **single 7% volume cap** per stock, replacing the old double cap. The same reform bans **payment for order flow**. ([ESMA](https://www.esma.europa.eu/node/220817), [PwC](https://legal.pwc.de/en/news/articles/mifir-mifid-ii-review-making-sense-of-the-key-amendments)) As in the US, the closing auction is huge.

**Mumbai.** India's cash market is concentrated on NSE, and almost everything is lit. Large trades go through **block-deal windows**: since December 2025, 8:45–9:00 a.m. and 2:05–2:20 p.m., with a **₹25 crore** minimum. ([Business Standard](https://www.business-standard.com/markets/news/sebi-eases-block-deal-norms-introduces-same-day-settlement-125100801173_1.html)) The open is a call auction, and since **3 August 2026** F&O stocks close through a **closing auction** instead of a 30-minute VWAP. ([Zerodha](https://support.zerodha.com/category/trading-and-markets/trading-faqs/market-sessions/articles/what-are-pre-market-and-post-market-sessions-and-orders)) I found the old opening auction systematically printing rich for a decade, in [Nifty made all its money while the market was closed]({% post_url 2026-11-24-nifty-overnight-returns %}). Retail algorithmic trading through broker APIs has been under a formal SEBI framework since **1 April 2026**. ([BSE circular summary](https://rhnvrm.github.io/stock-market-circulars/circulars/bse/2025/bse-2025-11-24-e6eac9e12bd239db-adherence-to-milestones-and-the-rules-related-to-retail-algo))

**Where machine learning actually helps.** Not in replacing the structure above, but in each forecast inside it: tomorrow's volume curve, the chance a passive order fills before the price moves, which venue is toxic right now, how a stock's closing imbalance will resolve. Each is a narrow, well-defined prediction with a measurable cost of being wrong — which is exactly the kind of problem models are good at.

---

## Glossary

- **ADV:** average daily volume.
- **Agency / principal:** trading on the client's behalf vs. trading against the client from your own book.
- **ATS / dark pool:** a trading venue that does not display quotes.
- **Conditional order:** a non-binding indication of block interest that must be "firmed up" to trade.
- **IS (implementation shortfall):** cost measured against the decision or arrival price.
- **Markout:** the price move after a fill; the main measure of adverse selection.
- **NBBO:** the national best bid and offer across US exchanges.
- **Parent / child order:** the client's full order / the small slices actually sent to market.
- **POV:** percentage-of-volume, an algo that trades a fixed share of market volume.
- **SOR:** smart order router.
- **VWAP:** volume-weighted average price.

## Further reading

- Larry Harris, *Trading and Exchanges* (2003): still the best map of who trades and why.
- Barry Johnson, *Algorithmic Trading and DMA* (2010): the practitioner's manual for algos, routing and FIX.
- Jean-Philippe Bouchaud, Julius Bonart, Jonathan Donier and Martin Gould, *Trades, Quotes and Prices* (2018): impact, the square-root law and order books, from the physics side.
- Álvaro Cartea, Sebastian Jaimungal and José Penalva, *Algorithmic and High-Frequency Trading* (2015): the stochastic-control view.
- André Perold, "The implementation shortfall: paper versus reality", *Journal of Portfolio Management* (1988).

*The fund, stock and broker in this post are fictional, and the day is a simulation built for illustration. Code: [`order_sim.py`](https://github.com/ShreyansJain04/ShreyansJain04.github.io/tree/master/assets/code/life-of-an-order). Market-structure figures are from the sources linked. Nothing here is investment advice or describes any specific firm's systems.*
