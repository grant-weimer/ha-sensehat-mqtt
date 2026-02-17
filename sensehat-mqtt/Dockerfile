# Supervisor builds use ghcr.io/home-assistant/<arch>-base (Alpine). Default for local builds.
ARG BUILD_FROM=ghcr.io/home-assistant/aarch64-base:latest
FROM ${BUILD_FROM}

ARG BUILD_ARCH
ARG BUILD_VERSION

# Read Sense HAT env sensors via I2C (HTS221/LPS25H) using smbus2; no sense-hat/RTIMULib.
RUN apk add --no-cache i2c-tools py3-pip \
    && python3 -m pip install --no-cache-dir --break-system-packages smbus2 paho-mqtt

WORKDIR /app
COPY sensehat_mqtt.py sensehat_sensors.py /app/
COPY run.sh /run.sh
RUN chmod +x /run.sh

LABEL \
    io.hass.version="${BUILD_VERSION}" \
    io.hass.type="addon" \
    io.hass.arch="${BUILD_ARCH}"

CMD [ "/run.sh" ]
