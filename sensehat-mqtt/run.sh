#!/bin/bash
# Start the Sense HAT MQTT bridge. Options are read from /data/options.json by the Python script.
set -e
exec python3 /app/sensehat_mqtt.py
