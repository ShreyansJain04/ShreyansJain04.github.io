---
layout: page
title: "Neglected Tropical Diseases in Africa: An Interactive Data Analysis"
description: "Dashboard and statistical analysis of lymphatic filariasis and STH treatment coverage across African countries, 2000-2023."
img: assets/img/projects/ntds-africa/thumb.jpg
importance: 3
category: "ML & Data Projects"
period: "2025"   # TODO: verify; assignment file is "CS 328 Writing assignment - 2025"
links:
  code: https://github.com/ShreyansJain04/NTDs-in-Africa
tags: [data-analysis, visualization, public-health, statistics, Plotly]
---

<div class="tldr" markdown="1">
**Problem.** Are mass drug administration programs for two neglected tropical diseases reaching the people who need them, and what drives differences between countries?  
**Approach.** Clean and merge public health, economic and sanitation data, test hypotheses with regressions, t-tests, correlations and ANOVA, and publish the findings as an interactive Plotly dashboard.  
**Result.** National coverage rose significantly over time (about +1.32 points per year for LF and +2.28 for STH), and treatment delivery tracks need, while economic wealth alone does not explain coverage.
</div>

## Overview

The project studies **Lymphatic Filariasis (LF)** and **Soil-Transmitted Helminthiases (STH)**, two of the 20 recognised neglected tropical diseases. They stand out for their prevalence, chronic impact and the feasibility of large-scale preventive chemotherapy. The work was done for the course CS 328 (data visualization), where it grew from a written analysis into a standalone web dashboard.

## Method

- **Data engineering.** Two decades of country-level data (population requiring preventive chemotherapy, people treated, programme and national coverage, GDP per capita, sanitation access, urban population share, health spending, development aid) were cleaned and joined.
- **Visualization.** Time series, scatter plots, choropleth maps and parallel coordinates built in Plotly. A script extracts the chart configurations from the analysis notebook into `assets/charts.json`, which the front end renders natively.
- **Dashboard.** A dark-mode static site (`index.html`, `main.js`, `style.css`) that fetches the chart JSON, so it runs with `python3 -m http.server`.
- **Hypothesis testing.** The notebook `wa.ipynb` holds the statistical tests behind each claim.

## Results

| Hypothesis | Finding |
|---|---|
| Coverage improves over time | Significant (p < 0.001): about +1.32 points per year (LF, R² 0.06) and +2.28 (STH, R² 0.15) |
| Treatment responds to need | Need and people treated correlate at r = 0.75 for LF; regression R² 0.578 |
| MDA drug combination matters | LF coverage differs by type of MDA (ANOVA F = 4.0, p = 0.0006) |
| Urbanisation helps | Significant for LF (p = 0.001), not for STH (p = 0.095) |
| Wealth lowers reported coverage | Lagged GDP per capita is negatively associated with coverage, consistent with programs scaling down as countries develop |

Residual analysis against GDP per capita flags over- and under-performers: Burkina Faso stands out for LF, while Angola and the Central African Republic fall well short. Low R² values throughout are a reminder that sanitation, targeted health spending and foreign aid also matter.

## My role

- Cleaned and integrated the datasets and ran the regressions and hypothesis tests.
- Built the Plotly charts and the dashboard front end.
- Wrote the interpretation of each result for the accompanying report.
