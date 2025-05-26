# Toilet Occupancy Monitor

This project implements a system for monitoring the occupancy of toilet stalls and recording sanitation events within a faculty building.

## Features

- Detects stall occupancy using a combination of Hall sensors (door open/close) and PIR motion sensors.
- Records sanitation events using RFID tags.
- Sends collected data via WiFi to a web server.
- Web server stores data in SQLite and provides visualization of occupancy and sanitation history.
- User-friendly web interface with floor plans and detailed stall status.

## Hardware

- ESP32 microcontroller for control and WiFi communication.
- PN532 RFID reader module.
- Hall sensor (OH137) and PIR sensor (SR602) for presence detection.
- Li-ion battery (18650) with power management modules.

## Software

- Device firmware programmed for sensor reading, event detection, and JSON data transmission.
- Web server implemented in Python using Flask framework.
- Data visualization based on SVG floor plans.

