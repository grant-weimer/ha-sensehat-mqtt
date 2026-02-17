#!/usr/bin/env python3
"""
Sense HAT → MQTT bridge for Home Assistant OS.
Reads temperature, humidity, and pressure from the Sense HAT and publishes
to MQTT. Supports MQTT discovery so sensors appear automatically in HA.
"""
import json
import os
import sys
import time

try:
    import paho.mqtt.client as mqtt
except ImportError:
    print("Error: paho-mqtt not installed", file=sys.stderr)
    sys.exit(1)

try:
    from sense_hat import SenseHat
except ImportError as e:
    print(f"Error: sense_hat not available: {e}", file=sys.stderr)
    sys.exit(1)


CONFIG_PATH = "/data/options.json"
DEVICE_ID = "sensehat"
DEVICE_NAME = "Sense HAT"
MANUFACTURER = "Raspberry Pi"
MODEL = "Sense HAT"


def load_config():
    if not os.path.isfile(CONFIG_PATH):
        raise SystemExit(f"Config not found: {CONFIG_PATH}")
    with open(CONFIG_PATH) as f:
        return json.load(f)


def on_connect(client, userdata, flags, reason_code, properties=None):
    if reason_code != 0:
        print(f"MQTT connection failed: {reason_code}", file=sys.stderr)
        return
    print("Connected to MQTT broker")
    userdata["connected"] = True


def on_disconnect(client, userdata, flags, reason_code, properties=None):
    userdata["connected"] = False
    print(f"Disconnected from MQTT broker: {reason_code}")


def publish_discovery(client, prefix, topic_prefix):
    """Publish Home Assistant MQTT discovery messages so sensors auto-configure."""
    device = {
        "identifiers": [DEVICE_ID],
        "name": DEVICE_NAME,
        "manufacturer": MANUFACTURER,
        "model": MODEL,
    }
    base_topic = f"{topic_prefix}/status"

    sensors = [
        {
            "name": "Temperature (from humidity)",
            "unique_id": f"{DEVICE_ID}_temp_humidity",
            "state_topic": base_topic,
            "value_template": "{{ value_json.temperature_from_humidity }}",
            "unit_of_measurement": "°C",
            "device_class": "temperature",
            "state_class": "measurement",
        },
        {
            "name": "Temperature (from pressure)",
            "unique_id": f"{DEVICE_ID}_temp_pressure",
            "state_topic": base_topic,
            "value_template": "{{ value_json.temperature_from_pressure }}",
            "unit_of_measurement": "°C",
            "device_class": "temperature",
            "state_class": "measurement",
        },
        {
            "name": "Humidity",
            "unique_id": f"{DEVICE_ID}_humidity",
            "state_topic": base_topic,
            "value_template": "{{ value_json.humidity }}",
            "unit_of_measurement": "%",
            "device_class": "humidity",
            "state_class": "measurement",
        },
        {
            "name": "Pressure",
            "unique_id": f"{DEVICE_ID}_pressure",
            "state_topic": base_topic,
            "value_template": "{{ value_json.pressure }}",
            "unit_of_measurement": "hPa",
            "device_class": "pressure",
            "state_class": "measurement",
        },
    ]

    for s in sensors:
        uid = s.pop("unique_id")
        discovery_topic = f"{prefix}/sensor/{DEVICE_ID}/{uid}/config"
        payload = {
            **s,
            "device": device,
        }
        client.publish(discovery_topic, json.dumps(payload), retain=True)
        print(f"Published discovery: {discovery_topic}")


def main():
    config = load_config()
    mqtt_host = config.get("mqtt_host", "core-mosquitto")
    mqtt_port = int(config.get("mqtt_port", 1883))
    mqtt_user = (config.get("mqtt_username") or "").strip()
    mqtt_pass = (config.get("mqtt_password") or "").strip()
    topic_prefix = (config.get("topic_prefix") or "home/sensehat").strip().rstrip("/")
    update_interval = int(config.get("update_interval", 60))
    discovery_prefix = (config.get("discovery_prefix") or "homeassistant").strip()

    sense = SenseHat()
    sense.clear()

    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id=f"{DEVICE_ID}-bridge")
    userdata = {"connected": False}
    client.user_data_set(userdata)
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect

    if mqtt_user:
        client.username_pw_set(mqtt_user, mqtt_pass if mqtt_pass else None)

    try:
        client.connect(mqtt_host, mqtt_port, 60)
    except Exception as e:
        print(f"Cannot connect to MQTT broker at {mqtt_host}:{mqtt_port}: {e}", file=sys.stderr)
        sys.exit(1)

    client.loop_start()
    # Wait for first connection
    for _ in range(30):
        if userdata["connected"]:
            break
        time.sleep(0.5)
    if not userdata["connected"]:
        print("MQTT connection timeout", file=sys.stderr)
        sys.exit(1)

    status_topic = f"{topic_prefix}/status"
    discovery_done = False

    while True:
        try:
            if not userdata["connected"]:
                time.sleep(5)
                continue

            # Read sensors (from_humidity and from_pressure are the two temp sources on Sense HAT)
            temp_h = sense.get_temperature_from_humidity()
            temp_p = sense.get_temperature_from_pressure()
            humidity = sense.get_humidity()
            pressure = sense.get_pressure()

            payload = {
                "temperature_from_humidity": round(temp_h, 2),
                "temperature_from_pressure": round(temp_p, 2),
                "humidity": round(humidity, 2),
                "pressure": round(pressure, 2),
            }
            client.publish(status_topic, json.dumps(payload), retain=True)

            if not discovery_done:
                publish_discovery(client, discovery_prefix, topic_prefix)
                discovery_done = True

        except Exception as e:
            print(f"Error reading Sense HAT or publishing: {e}", file=sys.stderr)

        time.sleep(update_interval)


if __name__ == "__main__":
    main()
