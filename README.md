# Sense HAT MQTT – Home Assistant Add-on Repository

This repository contains a single add-on: **Sense HAT MQTT**, which publishes Raspberry Pi Sense HAT sensor data (temperature, humidity, pressure) to MQTT so Home Assistant can use it on the same Pi running Home Assistant OS.

## Adding this repository in Home Assistant

1. In Home Assistant go to **Settings → Add-ons → Add-on store**.
2. Click the **⋮** (three dots) in the top right, then **Repositories**.
3. Add this repository URL. Use one of:
   - **If you pushed this folder to GitHub:**  
     `https://github.com/YOUR_USERNAME/ha-sensehat-mqtt`
   - **If you use a different git host:**  
     the clone URL of the repo (e.g. `https://gitlab.com/...`).
4. Click **Add**, then **Close**.
5. Refresh the Add-on store if needed; you should see **Sense HAT MQTT** (under the name of this repo).
6. Install the add-on and configure it (see the add-on’s **Documentation** tab or `sensehat-mqtt/README.md`).

## Add-on documentation

See **[sensehat-mqtt/README.md](sensehat-mqtt/README.md)** for:

- Enabling I2C on Home Assistant OS
- Add-on configuration options
- Using the sensors in Home Assistant
- Troubleshooting

## Repository structure

```text
ha-sensehat-mqtt/
├── repository.yaml      # Repository metadata
├── README.md            # This file
└── sensehat-mqtt/       # Sense HAT MQTT add-on
    ├── config.yaml
    ├── build.yaml
    ├── Dockerfile
    ├── run.sh
    ├── sensehat_mqtt.py
    ├── README.md
    └── CHANGELOG.md
```

## Building the add-on locally (optional)

Home Assistant builds add-ons automatically when you install from a repository. To build the image yourself (e.g. for testing):

- Use the [Home Assistant add-on builder](https://github.com/home-assistant/addons-development#building-add-ons-locally), or
- From the `sensehat-mqtt` directory:  
  `docker build --build-arg BUILD_FROM=python:3.11-slim-bookworm --build-arg BUILD_ARCH=aarch64 --build-arg BUILD_VERSION=1.0.0 -t sensehat-mqtt .`
