# Sense HAT MQTT Add-on

Publishes Raspberry Pi Sense HAT sensors (temperature, humidity, pressure) to MQTT so Home Assistant can use them. Runs on the same Pi as Home Assistant OS with the Sense HAT attached.

## Requirements

- Home Assistant OS on a Raspberry Pi (e.g. Pi 4) with the Sense HAT physically attached
- **I2C enabled** on the host (see below)
- An MQTT broker reachable from add-ons (e.g. the official **Mosquitto broker** add-on)

## Enable I2C on Home Assistant OS

The Sense HAT uses I2C. Home Assistant OS does not enable I2C by default.

1. Install the **HassOS I2C Configurator** add-on (or use the official method if your HA version supports it):
   - **Settings → Add-ons → Add-on store** → ⋮ (top right) → **Repositories**
   - Add the repository that provides "HassOS I2C Configurator" (search the [Community forum](https://community.home-assistant.io/t/add-on-hassos-i2c-configurator/264167) for the repo URL)
   - Install **HassOS I2C Configurator**
   - Open its **Configuration** and **disable "Protection mode"** if needed, then **Start** the add-on and check the log
2. **Reboot the entire device twice** (full reboot, not just “Restart Home Assistant”). I2C often only works after the second reboot.
3. You can uninstall the I2C Configurator add-on after I2C is enabled.

## Installation

1. Add this add-on repository to Home Assistant:
   - **Settings → Add-ons → Add-on store** → ⋮ → **Repositories**
   - Add the URL of the repository that contains this add-on (e.g. your GitHub repo URL).
2. Install the **Sense HAT MQTT** add-on from the store.
3. Configure the add-on (see Configuration below).
4. Start the add-on and check the **Log** tab for “Connected to MQTT broker” and “Published discovery”.

## Configuration

| Option            | Description                                                                 | Default           |
|------------------|-----------------------------------------------------------------------------|-------------------|
| `mqtt_host`      | MQTT broker hostname (use `core-mosquitto` if you use the Mosquitto add-on) | `core-mosquitto`   |
| `mqtt_port`      | MQTT broker port                                                            | `1883`            |
| `mqtt_username`  | Broker username (leave empty if your broker has no auth)                     | (empty)           |
| `mqtt_password`  | Broker password                                                              | (empty)           |
| `topic_prefix`   | MQTT topic prefix for status                                                | `home/sensehat`   |
| `update_interval`| How often to publish sensor values (seconds)                                 | `60`              |
| `discovery_prefix` | MQTT discovery prefix (must match HA’s MQTT integration)                  | `homeassistant`   |

If you use the **Mosquitto broker** add-on with a username/password, set the same `mqtt_username` and `mqtt_password` here.

## Home Assistant

After the add-on is running:

1. **MQTT discovery**: If your Home Assistant MQTT integration has discovery enabled, the Sense HAT sensors should appear automatically under one device (e.g. “Sense HAT”) with entities for:
   - Temperature (from humidity)
   - Temperature (from pressure)
   - Humidity
   - Pressure
2. If they don’t appear, open **Settings → Devices & services → MQTT** and use **Configure** / **Add integration** if needed, and ensure the broker the add-on uses is the one configured in HA.
3. You can also use the published state topic manually: the add-on publishes a JSON payload to `{topic_prefix}/status` (e.g. `home/sensehat/status`) with keys: `temperature_from_humidity`, `temperature_from_pressure`, `humidity`, `pressure`.

## Troubleshooting

- **Add-on won’t start or logs “Error: sense_hat not available”**  
  Ensure I2C is enabled and you have **rebooted the host twice**. Check that the Sense HAT is firmly attached to the Pi’s GPIO header.

- **“Cannot connect to MQTT broker”**  
  Install and start the **Mosquitto broker** add-on (or your chosen broker). Use `core-mosquitto` as `mqtt_host` if the broker is the official add-on. If you set a username in Mosquitto, set the same in this add-on’s options.

- **Sensors not appearing in Home Assistant**  
  Confirm MQTT discovery is enabled for your MQTT integration. Check **Developer tools → MQTT** and listen to `homeassistant/sensor/#` to see if discovery messages are received.

- **Temperature reads high**  
  The Sense HAT sits above the Pi’s CPU and is heated by it. Prefer “Temperature (from humidity)” for room-like readings, or move the HAT away with a GPIO extension cable.
