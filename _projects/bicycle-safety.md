---
layout: page
title: "Bicycle Safety App for Android"
description: "Android app using phone sensors to flag overspeeding, falls and boundary breaches, with a 5-second safety-check fallback."
img: assets/img/projects/bicycle-safety/thumb.jpg
importance: 2
category: "Hardware & Embedded"
links:
  code: https://github.com/ShreyansJain04/BicycleSafetyApp   # TODO: verify; repo not reachable via gh (private or renamed)
tags: [Android, sensors, safety, mobile]
---

<div class="tldr" markdown="1">
**Problem.** Parents want to know when a child on a bicycle is speeding, has fallen or has left a safe area.  
**Approach.** An Android app that reads the phone's own sensors to detect these events in real time and notifies both the child's and the parent's devices.  
**Result.** A working app with three detectors and an automatic backup check if the child does not confirm safety within 5 seconds.
</div>

## Overview

The project was advised by Prof. Nithin V. George of Electrical Engineering at IIT Gandhinagar. It uses only what a phone already carries (motion sensors and location), so no extra hardware is needed on the bicycle.

## Method

The app watches for three conditions:

- **Overspeeding**, from the measured speed against a limit.
- **Falls**, from the motion sensors.
- **Geographic boundary breaches**, when the rider leaves a predefined area.

On any incident it sends notifications to both the child and parent devices. If the child does not confirm they are safe within **5 seconds**, a backup safety feature activates to monitor the surroundings.

<!-- TODO: verify implementation details (sensors used, thresholds, notification channel, what "monitor surroundings" does). Not in the sources beyond the original project summary. -->

## Results

The sources do not report quantitative evaluation. The deliverable is the working app, described above.

## My role
<!-- TODO: verify these role bullets with Shreyans; sources do not itemise individual contributions. -->

- Developed the Android application and its detection logic.
- Designed the notification flow between child and parent devices and the 5-second confirmation fallback.
