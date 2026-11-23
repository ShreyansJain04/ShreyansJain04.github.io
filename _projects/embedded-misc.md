---
layout: page
title: "Embedded Builds"
description: "Three small hardware projects: a fall-detecting helmet, an STM32 pocket oscilloscope and a DC anemometer."
img: assets/img/projects/embedded-misc/thumb.jpg
importance: 3
category: "Hardware & Embedded"
links:
  code: https://github.com/ShreyansJain04?tab=repositories
tags: [Arduino, STM32, sensors, embedded-C, hardware]
---

<div class="tldr" markdown="1">
Three hands-on builds from coursework, each with its own repository. Details below come from the repositories; anything not documented there is left out.
</div>

## Accident Alert Helmet

An Arduino-style sketch (`FallAlertHelmet.ino`) reads an MPU-6050 accelerometer and gyroscope over I2C, integrates pitch and roll, and sounds a buzzer when the combined tilt exceeds a 75 degree threshold. A piezo sensor on an analog pin provides a second, impact-based trigger. The repository also contains the presentation. [Code](https://github.com/ShreyansJain04/AccidentAlertHelmet)

## Portable Oscilloscope and Function Generator

Firmware for an STM32L4R5 board (CubeIDE project). It samples signals with the ADC into a 128-point buffer and draws them on an SSD1306 OLED, with push-button controls for amplitude and time-axis zoom and axis toggling. A menu-driven function generator uses the DAC for sine, square, triangular and sawtooth waves with selectable amplitude, frequency and offset. [Code](https://github.com/ShreyansJain04/Portable-Oscilloscope-Function-Generator)

## DC Anemometer

A DC-motor-based anemometer (wind-speed sensor) project. The repository contains only a report PDF written with a project partner; no source files or README are published. <!-- TODO: verify measurement principle and results from the report PDF in the repo. --> [Code and report](https://github.com/ShreyansJain04/DC_Anemometer)
