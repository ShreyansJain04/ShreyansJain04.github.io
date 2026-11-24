---
layout: page
title: "Whisker's Cafe: Teaching MDPs by Running a Cat Cafe"
description: "Streamlit app where value iteration and Q-learning optimise pricing and staffing for a 12-state cat cafe MDP."
img: assets/img/projects/whiskers-cafe/thumb.jpg
importance: 4
category: "ML & Data Projects"
team: "Utkarsh Srivastava, Rutvi Shah, Shreyans Jain, Mumuksh Jain"
links:
  demo: https://cat-cafe.streamlit.app
tags: [reinforcement-learning, MDP, Streamlit, education, value-iteration]
---

<div class="tldr" markdown="1">
**Problem.** Markov Decision Processes are abstract; students rarely get to feel how a discount factor changes a policy.  
**Approach.** Model a cat cafe as a 12-state MDP (price level x staff level), solve it with value iteration and Q-learning, and wrap it in a three-tab Streamlit app where you can also play manager.  
**Result.** A live interactive app that shows value heatmaps, optimal policies, convergence and learning curves, and lets users compare their own decisions against the AI.
</div>

## Overview

Every day the cafe owner picks one of five actions (raise price, lower price, hire, fire, maintain). Each choice changes today's profit and tomorrow's state, which is exactly the structure of an MDP. The app is live at [cat-cafe.streamlit.app](https://cat-cafe.streamlit.app).

## Method

**State and actions.** A state is a pair of price level (low, medium, high) and staff level (1-4 people), giving $$3\times 4 = 12$$ states.

**Reward.** Daily profit is customers times price, minus labour, minus a small penalty for changing state:

$$R(p,s,a) = N_{\text{cust}}\cdot \text{Price} - (s+1)\cdot 160 - \text{Penalty}$$

with $$N_{\text{cust}} = 25\,(1-0.13(p-1))\,(1+0.08\,s)$$ and a \$5 penalty when the action changes state.

**Solvers.** Value iteration applies the Bellman update until convergence, and the policy is the argmax over actions:

$$V(s) \leftarrow \max_a \Big[R(s,a) + \gamma \sum_{s'} P(s'|s,a)\,V(s')\Big]$$

Q-learning learns the same policy without the transition model, using an epsilon-greedy update $$Q(s,a)\leftarrow Q(s,a)+\alpha\,(r+\gamma\max_{a'}Q(s',a')-Q(s,a))$$.

**Three tabs.** *Configure & Solve* sets gamma, customer rate and staff cost and shows the value heatmap and policy table. *Cafe Simulation* lets you manage day by day against the AI's recommendations. *Learn & Explore* explains the maths.

The discount factor is the main teaching lever: gamma = 0.50 is a myopic owner, 0.95 plans 20+ days ahead, and 0.99 values the long-term future.

## Results

We walked through three parameter settings, each with four views: value-function heatmap, optimal policy, convergence tracker and Q-learning learning curve.

<div class="row">
  <div class="col-sm mt-3 mt-md-0">{% include figure.html path="assets/img/projects/whiskers-cafe/whiskers_1.1.png" class="img-fluid rounded z-depth-1" zoomable=true caption="Case 1: value function heatmap" %}</div>
  <div class="col-sm mt-3 mt-md-0">{% include figure.html path="assets/img/projects/whiskers-cafe/whiskers_1.2.png" class="img-fluid rounded z-depth-1" zoomable=true caption="Case 1: optimal policy" %}</div>
</div>
<div class="row">
  <div class="col-sm mt-3 mt-md-0">{% include figure.html path="assets/img/projects/whiskers-cafe/whiskers_1.3.png" class="img-fluid rounded z-depth-1" zoomable=true caption="Case 1: convergence tracker" %}</div>
  <div class="col-sm mt-3 mt-md-0">{% include figure.html path="assets/img/projects/whiskers-cafe/whiskers_1.4.png" class="img-fluid rounded z-depth-1" zoomable=true caption="Case 1: learning curve" %}</div>
</div>
<div class="row">
  <div class="col-sm mt-3 mt-md-0">{% include figure.html path="assets/img/projects/whiskers-cafe/whiskers_2.2.png" class="img-fluid rounded z-depth-1" zoomable=true caption="Case 2: optimal policy" %}</div>
  <div class="col-sm mt-3 mt-md-0">{% include figure.html path="assets/img/projects/whiskers-cafe/whiskers_3.2.png" class="img-fluid rounded z-depth-1" zoomable=true caption="Case 3: optimal policy" %}</div>
</div>

## My role

Team project. My part was **mathematics verification**: checking the reward model, the Bellman and Q-learning formulations and the convergence argument. Utkarsh Srivastava did the mathematics and code, Rutvi Shah the UI, and Mumuksh Jain the report.
