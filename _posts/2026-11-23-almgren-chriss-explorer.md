---
layout: post
title: "Your TWAP is a trader with zero fear: optimal execution, interactively"
date: 2026-11-23
description: "An interactive Almgren–Chriss explorer. Drag risk aversion and watch the optimal schedule bend away from TWAP; see why the first slice of risk reduction is nearly free, and why front-loading beats simply trading faster."
tags: [execution, market-microstructure, optimal-control, quant]
categories: markets
related_posts: false
og_image: https://ShreyansJain04.github.io/assets/img/blog/almgren-chriss/preview.png
featured: 4
toc:
  sidebar: left
---

> **TL;DR.** Selling a large order means trading off two costs: market impact, which punishes speed, and timing risk, which punishes delay. Almgren and Chriss solved that trade-off in closed form, and TWAP falls out as the special case of a trader who does not care about risk at all. Two consequences are easy to see once you can drag the sliders. Near TWAP the first slice of risk reduction costs almost nothing. And for a fixed cost budget, front-loading over the full horizon carries less risk than running a TWAP over a shorter one.

## The problem

You have to sell $$X$$ shares by time $$T$$. Two things go wrong:

- **Trade fast and you pay impact.** Every share you push into the market moves the price against you. In the simplest model the temporary impact is linear in your trading rate $$v$$, so the cost rate is $$\eta v^2$$.
- **Trade slowly and you carry risk.** Shares you still hold are exposed to the price wandering. With volatility $$\sigma$$, holding $$x(t)$$ shares has P&L variance $$\sigma^2 \int_0^T x(t)^2\,dt$$.

Almgren and Chriss (2000) minimise expected cost plus $$\lambda$$ times variance. I normalise both terms per unit of the order, so costs read in basis points of notional. Then the calculus of variations gives

$$\ddot{x}(t) = \kappa^2 x(t), \qquad \kappa = \sqrt{\frac{\lambda \sigma^2}{\eta X}}$$

with solution

$$x(t) = X\,\frac{\sinh\big(\kappa (T - t)\big)}{\sinh(\kappa T)}.$$

Everything about the schedule is in one number, $$\kappa T$$. At $$\kappa T \to 0$$ the sinh becomes a straight line: that is TWAP. As $$\kappa T$$ grows, the schedule front-loads, and at $$\kappa T = 4$$ only 13% of the order is left at the halfway mark.

Both costs have closed forms, which is what makes the explorer below instant:

$$\text{cost} = \eta X \kappa^2 \frac{\tfrac{\sinh 2\kappa T}{4\kappa} + \tfrac{T}{2}}{\sinh^2 \kappa T}, \qquad \text{risk} = \sigma\,\frac{\sqrt{\tfrac{\sinh 2\kappa T}{4\kappa} - \tfrac{T}{2}}}{\sinh \kappa T}$$

with TWAP limits of $$\eta X / T$$ and $$\sigma\sqrt{T/3}$$. I checked both against direct numerical integration of the schedule; they agree to the last digit shown.

## The explorer

<div id="ac-app" style="margin: 1.5rem 0;">
  <style>
    #ac-app .ac-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(230px, 1fr)); gap: 0.6rem 1.5rem; margin-bottom: 1rem; }
    #ac-app label { display: block; font-size: 0.9rem; margin-bottom: 0.1rem; }
    #ac-app label b { float: right; font-variant-numeric: tabular-nums; }
    #ac-app input[type=range] { width: 100%; }
    #ac-app .ac-plots { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 1rem; }
    #ac-app canvas { width: 100%; height: 300px; border: 1px solid rgba(128,128,128,0.25); border-radius: 6px; }
    #ac-app .ac-stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr)); gap: 0.5rem; margin: 1rem 0; }
    #ac-app .ac-stat { border: 1px solid rgba(128,128,128,0.25); border-radius: 6px; padding: 0.5rem 0.75rem; }
    #ac-app .ac-stat span { display: block; font-size: 0.8rem; opacity: 0.75; }
    #ac-app .ac-stat strong { font-size: 1.2rem; font-variant-numeric: tabular-nums; }
    #ac-app .ac-note { font-size: 0.85rem; opacity: 0.8; }
  </style>
  <div class="ac-grid">
    <div><label>Risk aversion λ <b id="ac-lam-v"></b></label><input id="ac-lam" type="range" min="-7" max="0" step="0.05" value="-3"></div>
    <div><label>Order size, % of daily volume <b id="ac-X-v"></b></label><input id="ac-X" type="range" min="1" max="50" step="1" value="10"></div>
    <div><label>Horizon, trading days <b id="ac-T-v"></b></label><input id="ac-T" type="range" min="0.1" max="3" step="0.05" value="1"></div>
    <div><label>Daily volatility, bp <b id="ac-sig-v"></b></label><input id="ac-sig" type="range" min="50" max="400" step="5" value="150"></div>
    <div><label>Impact η, bp at 100% of ADV per day <b id="ac-eta-v"></b></label><input id="ac-eta" type="range" min="5" max="150" step="1" value="30"></div>
  </div>
  <div class="ac-stats">
    <div class="ac-stat"><span>Expected impact cost</span><strong id="ac-cost"></strong></div>
    <div class="ac-stat"><span>Timing risk (1 s.d.)</span><strong id="ac-risk"></strong></div>
    <div class="ac-stat"><span>Urgency κT</span><strong id="ac-kT"></strong></div>
    <div class="ac-stat"><span>Left at half time</span><strong id="ac-half"></strong></div>
  </div>
  <div class="ac-plots">
    <canvas id="ac-traj"></canvas>
    <canvas id="ac-front"></canvas>
  </div>
  <p class="ac-note">Left: shares remaining, optimal schedule (blue) against TWAP (grey, dashed). Right: the efficient frontier of risk against expected cost for this order; the blue dot is your λ and the grey ring is TWAP. Costs and risk are in basis points of the order's notional. Defaults are illustrative, not calibrated to any stock.</p>
</div>

<script>
(function () {
  function $(id) { return document.getElementById(id); }
  function sinh(z) { return (Math.exp(z) - Math.exp(-z)) / 2; }
  function solve(X, T, sig, eta, lam) {
    var k = Math.sqrt(lam * sig * sig / (eta * X));
    var kT = Math.min(k * T, 300);
    if (kT < 1e-6) return { cost: eta * X / T, risk: sig * Math.sqrt(T / 3), k: 0, kT: 0 };
    k = kT / T;
    var s = sinh(kT), s2 = sinh(2 * kT) / (4 * k);
    return { cost: eta * X * k * k * (s2 + T / 2) / (s * s), risk: sig * Math.sqrt(Math.max(s2 - T / 2, 0)) / s, k: k, kT: kT };
  }
  function remaining(t, T, kT) {
    if (kT < 1e-6) return 1 - t / T;
    var a = kT * t / T;
    return (Math.exp(-a) - Math.exp(-(2 * kT - a))) / (1 - Math.exp(-2 * kT));
  }
  function setup(c) {
    var r = window.devicePixelRatio || 1, w = c.clientWidth, h = c.clientHeight;
    c.width = w * r; c.height = h * r;
    var g = c.getContext("2d"); g.setTransform(r, 0, 0, r, 0, 0);
    return { g: g, w: w, h: h };
  }
  function ink() { return getComputedStyle(document.body).color || "#333"; }
  var BLUE = "#2a78d6", GREY = "#8a8985";
  function axes(o, x0, x1, y0, y1, xl, yl, title) {
    var g = o.g, L = 52, R = 14, Tp = 30, B = 40, col = ink();
    var W = o.w - L - R, H = o.h - Tp - B;
    g.clearRect(0, 0, o.w, o.h);
    g.font = "12px sans-serif"; g.fillStyle = col; g.strokeStyle = col; g.globalAlpha = 1;
    g.fillText(title, L, 18);
    g.globalAlpha = 0.15;
    for (var i = 0; i <= 4; i++) { var yy = Tp + H * i / 4; g.beginPath(); g.moveTo(L, yy); g.lineTo(L + W, yy); g.stroke(); }
    g.globalAlpha = 0.8;
    for (i = 0; i <= 4; i++) {
      g.fillText(fmt(y1 - (y1 - y0) * i / 4), 4, Tp + H * i / 4 + 4);
      var xv = x0 + (x1 - x0) * i / 4; g.fillText(fmt(xv), L + W * i / 4 - 8, Tp + H + 16);
    }
    g.fillText(xl, L + W / 2 - g.measureText(xl).width / 2, o.h - 6);
    g.save(); g.translate(12, Tp + H / 2 + g.measureText(yl).width / 2); g.rotate(-Math.PI / 2); g.restore();
    g.globalAlpha = 1;
    return { X: function (v) { return L + W * (v - x0) / (x1 - x0); }, Y: function (v) { return Tp + H * (1 - (v - y0) / (y1 - y0)); } };
  }
  function fmt(v) { var a = Math.abs(v); return a >= 10 ? v.toFixed(0) : a >= 1 ? v.toFixed(1) : v.toFixed(2); }
  function line(g, pts, color, dash, width) {
    g.save(); g.strokeStyle = color; g.lineWidth = width || 2; g.setLineDash(dash || []);
    g.beginPath(); for (var i = 0; i < pts.length; i++) { if (i) g.lineTo(pts[i][0], pts[i][1]); else g.moveTo(pts[i][0], pts[i][1]); }
    g.stroke(); g.restore();
  }
  function draw() {
    var lam = Math.pow(10, +$("ac-lam").value), X = +$("ac-X").value / 100, T = +$("ac-T").value, sig = +$("ac-sig").value, eta = +$("ac-eta").value;
    $("ac-lam-v").textContent = lam < 0.001 ? lam.toExponential(1) : lam.toPrecision(2);
    $("ac-X-v").textContent = (X * 100).toFixed(0) + "%"; $("ac-T-v").textContent = T.toFixed(2);
    $("ac-sig-v").textContent = sig.toFixed(0); $("ac-eta-v").textContent = eta.toFixed(0);
    var s = solve(X, T, sig, eta, lam), tw = solve(X, T, sig, eta, 0);
    $("ac-cost").textContent = s.cost.toFixed(2) + " bp"; $("ac-risk").textContent = s.risk.toFixed(1) + " bp";
    $("ac-kT").textContent = s.kT.toFixed(2); $("ac-half").textContent = (100 * remaining(T / 2, T, s.kT)).toFixed(0) + "%";
    var o = setup($("ac-traj")), ax = axes(o, 0, T, 0, 100, "time, trading days", "", "% of order still to trade");
    var p1 = [], p2 = [];
    for (var i = 0; i <= 120; i++) { var t = T * i / 120; p1.push([ax.X(t), ax.Y(100 * remaining(t, T, s.kT))]); p2.push([ax.X(t), ax.Y(100 * (1 - t / T))]); }
    line(o.g, p2, GREY, [6, 4]); line(o.g, p1, BLUE, [], 2.5);
    var f = setup($("ac-front")), pts = [], maxC = 0, maxR = tw.risk * 1.05;
    for (var e = -9; e <= 2.0001; e += 0.05) { var q = solve(X, T, sig, eta, Math.pow(10, e)); pts.push(q); }
    var cap = Math.max(tw.cost * 6, s.cost * 1.3);
    pts = pts.filter(function (q) { return q.cost <= cap; });
    pts.forEach(function (q) { maxC = Math.max(maxC, q.cost); });
    var minR = pts[pts.length - 1].risk * 0.9;
    var bx = axes(f, Math.min(minR, s.risk * 0.9), maxR, 0, maxC * 1.08, "timing risk, bp (1 s.d.)", "", "Expected cost, bp: the efficient frontier");
    line(f.g, pts.map(function (q) { return [bx.X(q.risk), bx.Y(q.cost)]; }), BLUE, [], 2);
    var g = f.g;
    g.beginPath(); g.strokeStyle = GREY; g.lineWidth = 2; g.arc(bx.X(tw.risk), bx.Y(tw.cost), 7, 0, 2 * Math.PI); g.stroke();
    g.beginPath(); g.fillStyle = BLUE; g.arc(bx.X(s.risk), bx.Y(s.cost), 6, 0, 2 * Math.PI); g.fill();
    g.fillStyle = ink(); g.font = "12px sans-serif"; g.fillText("TWAP", bx.X(tw.risk) - 44, bx.Y(tw.cost) - 10);
  }
  ["ac-lam", "ac-X", "ac-T", "ac-sig", "ac-eta"].forEach(function (id) { $(id).addEventListener("input", draw); });
  window.addEventListener("resize", draw);
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", draw); else draw();
})();
</script>

## Three things the sliders make obvious

All numbers below use the defaults: sell 10% of a day's volume over one day, 150 bp daily volatility, and η = 30 bp at 100% of ADV per day.

**1. TWAP is the zero-fear solution.** Drag λ all the way left and the blue curve sits on the dashed line. TWAP costs 3.0 bp of impact here and carries 86.6 bp of timing risk. That ratio is the first surprise: for an order this size, the risk you carry is almost 30 times the impact you pay. "Minimise impact" is the wrong goal when impact is the small number.

**2. The first slice of risk reduction is nearly free.** The frontier is flat where TWAP sits. That is the envelope theorem: TWAP minimises cost, so a small step away from it costs nothing to first order. Cutting timing risk by 20% (to 69 bp) raises expected cost from 3.0 to 3.7 bp. Cutting it by 30% costs 4.6 bp. Only near 50% does the bill really climb, to 9.0 bp. Any desk running plain TWAP on orders like this is leaving a cheap hedge on the table.

**3. Front-loading beats rushing.** Say you are willing to spend 6 bp. One way is a TWAP over half a day: 6.0 bp of cost, 61.2 bp of risk. The other is to keep the whole day and front-load with κT ≈ 4: also 6.0 bp, but 53.1 bp of risk, **13% less for the same money**. Rushing spreads your urgency evenly. Front-loading spends it where it buys the most: the early shares are the ones exposed for longest.

## What the model leaves out

- **Impact is not linear.** Measured impact grows roughly with the square root of participation, so the true frontier is shaped differently. Linear impact is what buys the closed form.
- **Volume is not flat.** Real markets have an intraday volume curve, with NSE heavy at the open and the close, so practical schedules are VWAP-shaped before any risk tilt.
- **Permanent impact does not change the schedule.** With linear permanent impact it adds a constant $$\tfrac{1}{2}\gamma X^2$$ whatever you do, so I left it out.
- **No drift, no alpha.** The model assumes prices have no predictable direction over your horizon. When they do, the answer changes, and it can change a lot. In [the overnight-returns post]({% post_url 2026-11-24-nifty-overnight-returns %}) the NSE opening auction printed rich on average for a decade. A model with that drift built in would tell a seller to lean into the open and a buyer to stay out of it.

## Reference

Robert Almgren and Neil Chriss, "Optimal execution of portfolio transactions", *Journal of Risk*, 3(2), 2000. My normalisation divides cost and variance by the order size, so $$\kappa$$ here carries a $$1/X$$ that the paper's version, written on total P&L, does not.
