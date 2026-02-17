# Default so local builds and supervisor (if BUILD_FROM ever empty) use Debian Python image
ARG BUILD_FROM=python:3.11-slim-bookworm
FROM ${BUILD_FROM}

ARG BUILD_ARCH
ARG BUILD_VERSION

# Sense HAT needs I2C and some libs; keep image small
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        i2c-tools \
        libjpeg62-turbo \
        zlib1g \
    && rm -rf /var/lib/apt/lists/*

# Use python -m pip so the correct interpreter is used in all base images
RUN python3 -m pip install --no-cache-dir --break-system-packages \
    sense-hat \
    paho-mqtt

WORKDIR /app
COPY sensehat_mqtt.py /app/
COPY run.sh /run.sh
RUN chmod +x /run.sh

LABEL \
    io.hass.version="${BUILD_VERSION}" \
    io.hass.type="addon" \
    io.hass.arch="${BUILD_ARCH}"

CMD [ "/run.sh" ]
