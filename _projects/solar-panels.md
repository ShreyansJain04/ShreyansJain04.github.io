---
layout: page
title: "Solar Panel Detection from Satellite Imagery"
description: "End-to-end rooftop solar panel pipeline: EDA, georeferencing, from-scratch AP metrics and YOLO detection on satellite tiles."
img: assets/img/projects/solar-panels/thumb.jpg
importance: 2
category: "ML & Data Projects"
tags: [object detection, YOLO, geospatial, remote sensing]
links:
  code: https://github.com/ShreyansJain04/AI-for-Satellite-Imaging
---

<div class="tldr" markdown="1">
**Problem.** Find rooftop solar panels in high-resolution satellite imagery and place them on a map.  
**Approach.** Exploratory analysis in metric units, georeferencing of YOLO boxes, from-scratch IoU and AP implementations, and an Ultralytics YOLO detector.  
**Result.** A reproducible set of notebooks and a trained checkpoint, with an interactive map of georeferenced detections.
</div>

## Overview

This compact project began as a multi-part assignment and is organised as three notebooks plus a bonus. It covers the full path from raw labels to a deployed-style detector.

{% include figure.html path="assets/img/projects/solar-panels/datset_image.png" class="img-fluid rounded z-depth-1" zoomable=true caption="Dataset exploration plot from the EDA notebook." %}

## Method

- **EDA and area in metres.** Label counts per image and panel area statistics, converted to metres using the sensor ground resolution.
- **Georeferencing.** Normalised YOLO centres become pixel coordinates using chip size, then UTM through the tile geotransform, then WGS84 lon/lat with `pyproj`. Results are shown on an interactive `leafmap` map.
- **Metrics from scratch.** IoU using `shapely` and three AP variants (VOC-11, COCO-101, AUPRC), compared against the `supervision` library; the two agree closely.
- **Detection.** An Ultralytics YOLO model trained on the dataset split (the README example uses a YOLO11-large start, 50 epochs, 416 px images) and evaluated with standard metrics.
- **Generalisation.** A bonus notebook runs tiled inference on new regions to check qualitative transfer.

{% include figure.html path="assets/img/projects/solar-panels/abc.png" class="img-fluid rounded z-depth-1" zoomable=true caption="Example figure from the project notebooks." %}

## Notes

The dataset is not included in the repository, and the README reports no headline detection metric, so none is quoted here. <!-- TODO: verify and add mAP from Question 3 notebook if desired -->
