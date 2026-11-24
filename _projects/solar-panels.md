---
layout: page
title: "Solar Panel Detection from Satellite Imagery"
description: "End-to-end rooftop solar panel pipeline: EDA, georeferencing, from-scratch AP metrics and a YOLO detector reaching 0.95 mAP@0.5 on held-out tiles."
img: assets/img/projects/solar-panels/thumb.jpg
importance: 2
category: "ML & Data Projects"
tags: [object detection, YOLO, geospatial, remote sensing]
links:
  code: https://github.com/ShreyansJain04/AI-for-Satellite-Imaging
---

<div class="tldr" markdown="1">
**Problem.** Find rooftop solar panels in high-resolution satellite imagery and place them on a map.  
**Approach.** Exploratory analysis in metric units, georeferencing of YOLO boxes, from-scratch IoU and AP implementations, and an Ultralytics YOLO11 detector.  
**Result.** **0.948 mAP@0.5** and **0.798 mAP@0.5:0.95** on the held-out test tiles, with my own AP implementations checked against the `supervision` library, plus a check on new imagery from Gandhinagar and Germany.
</div>

## Overview

This project began as a multi-part assignment and is organised as three notebooks plus a bonus. It covers the full path from raw labels to a detector that runs on imagery it has never seen.

## 1. Exploring the data

The dataset is made of 416 × 416 px chips cut from large native satellite tiles, with YOLO-format labels. Almost every label belongs to one class, so the task is close to single-class detection. Most chips hold fewer than 20 panels, but a long tail of dense chips (solar farms, large rooftops) holds up to about 80.

<div class="row">
  <div class="col-sm mt-3 mt-md-0">{% include figure.html path="assets/img/projects/solar-panels/eda-category-counts.png" class="img-fluid rounded z-depth-1" zoomable=true caption="Label counts per category: class 0 dominates." %}</div>
  <div class="col-sm mt-3 mt-md-0">{% include figure.html path="assets/img/projects/solar-panels/eda-labels-per-image.png" class="img-fluid rounded z-depth-1" zoomable=true caption="Panels per image: most chips are sparse, with a long dense tail." %}</div>
</div>

Using the sensor's ground resolution, each box's area is converted from pixels to square metres. The distribution is heavily skewed: most installations are small rooftop arrays, and a few very large ones stretch the tail.

<div class="row justify-content-center">
  <div class="col-sm-8 mt-3 mt-md-0">{% include figure.html path="assets/img/projects/solar-panels/eda-area-histogram.png" class="img-fluid rounded z-depth-1" zoomable=true caption="Histogram of panel areas in m²." %}</div>
</div>

## 2. Georeferencing

Each normalised YOLO centre becomes a pixel coordinate using the chip size and offset, then a UTM coordinate through the tile's geotransform, then WGS84 longitude and latitude with `pyproj`. The detections are plotted on an interactive `leafmap` map. As a check, one location was compared against Google Earth: the same roads and rooftops line up.

<div class="row">
  <div class="col-sm mt-3 mt-md-0">{% include figure.html path="assets/img/projects/solar-panels/georef-dataset-tile.jpg" class="img-fluid rounded z-depth-1" zoomable=true caption="A chip from the dataset." %}</div>
  <div class="col-sm mt-3 mt-md-0">{% include figure.html path="assets/img/projects/solar-panels/georef-google-earth.jpg" class="img-fluid rounded z-depth-1" zoomable=true caption="The same location in Google Earth, found from the computed coordinates." %}</div>
</div>

## 3. Metrics from scratch

Before training, I implemented IoU using `shapely` and three Average Precision variants: Pascal VOC 11-point, COCO 101-point and area under the PR curve. My IoU matched `supervision` exactly (0.3913 on the test case). The three AP variants give different numbers on the same predictions, which shows how much the interpolation scheme alone can move a reported score. As a sanity check, on randomly placed predicted and ground-truth boxes all three give near-zero AP50 (0.02 to 0.07), as they should.

## 4. Training the detector

An Ultralytics YOLO11 model was trained for 50 epochs at 416 px. Training and validation box loss fall together, with no sign of overfitting by the end.

<div class="row justify-content-center">
  <div class="col-sm-9 mt-3 mt-md-0">{% include figure.html path="assets/img/projects/solar-panels/yolo-box-loss.png" class="img-fluid rounded z-depth-1" zoomable=true caption="Train and validation box loss over 50 epochs." %}</div>
</div>

On the validation set (254 chips, 2,999 panels) the final model reaches **0.987 precision, 0.786 recall, 0.869 mAP@0.5 and 0.71 mAP@0.5:0.95**. High precision with lower recall means it rarely invents panels; what it misses tends to be small or partly hidden arrays.

On the held-out test set:

| Metric | Value |
|---|---|
| mAP@0.5 (`supervision`) | 0.948 |
| mAP@0.75 (`supervision`) | 0.908 |
| mAP@0.5:0.95 (`supervision`) | 0.798 |
| AP, VOC 11-point (mine) | 0.907 |
| AP, area under PR curve (mine) | 0.966 |
| AP, COCO 101-point (mine) | 0.980 |

Ground truth (green) and predictions (blue) overlap closely, from a dense solar farm to sparse rural rooftops:

<div class="row">
  <div class="col-sm mt-3 mt-md-0">{% include figure.html path="assets/img/projects/solar-panels/pred-dense.jpg" class="img-fluid rounded z-depth-1" zoomable=true caption="Dense chip: 48 panels detected." %}</div>
  <div class="col-sm mt-3 mt-md-0">{% include figure.html path="assets/img/projects/solar-panels/pred-rooftops.jpg" class="img-fluid rounded z-depth-1" zoomable=true caption="Scattered residential rooftops." %}</div>
  <div class="col-sm mt-3 mt-md-0">{% include figure.html path="assets/img/projects/solar-panels/pred-farm.jpg" class="img-fluid rounded z-depth-1" zoomable=true caption="Large farm-building roofs." %}</div>
</div>

## 5. Testing on new places

To test transfer, I downloaded new satellite imagery for four places, split each image into tiles and ran the trained checkpoint on them. The places were the IIT Gandhinagar hostels, a solar car port on campus, a random spot in Gandhinagar and a residential area in Germany.

<div class="row">
  <div class="col-sm mt-3 mt-md-0">{% include figure.html path="assets/img/projects/solar-panels/bonus-solar-carport.jpg" class="img-fluid rounded z-depth-1" zoomable=true caption="IITGN solar car port." %}</div>
  <div class="col-sm mt-3 mt-md-0">{% include figure.html path="assets/img/projects/solar-panels/bonus-gandhinagar.jpg" class="img-fluid rounded z-depth-1" zoomable=true caption="Rooftops elsewhere in Gandhinagar." %}</div>
</div>

{% include figure.html path="assets/img/projects/solar-panels/bonus-iitgn-hostel.jpg" class="img-fluid rounded z-depth-1" zoomable=true caption="IITGN hostel rooftops." %}

{% include figure.html path="assets/img/projects/solar-panels/bonus-germany.jpg" class="img-fluid rounded z-depth-1" zoomable=true caption="A residential area in Germany." %}

The model picks out the car-port rows and Gandhinagar rooftop arrays well, even though it was trained on different terrain. The German tile is harder. The model boxes panels on two roofs but misses clear panel strips on at least three others, and one box spills onto a lawn. Recall drops on this unfamiliar roof style and image quality, so more varied training data would help.

## Notes

The dataset is not included in the repository. The trained checkpoint (`best.pt`) is, so the inference and bonus notebooks can be rerun directly.
