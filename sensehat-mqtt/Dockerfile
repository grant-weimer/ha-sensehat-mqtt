# Supervisor builds use ghcr.io/home-assistant/<arch>-base (Alpine). Default for local builds.
ARG BUILD_FROM=ghcr.io/home-assistant/aarch64-base:latest
FROM ${BUILD_FROM}

ARG BUILD_ARCH
ARG BUILD_VERSION

# Alpine: Sense HAT runtime + build deps (sense-hat and RTIMULib compile from source; no musl wheels)
RUN apk add --no-cache \
    i2c-tools \
    libjpeg-turbo \
    zlib \
    py3-pip \
    && apk add --no-cache --virtual .build-deps \
    gcc \
    g++ \
    cmake \
    python3-dev \
    linux-headers \
    libjpeg-turbo-dev \
    zlib-dev

# sense-hat requires RTIMU from RTIMULib (IMU fusion); install explicitly for Alpine/musl
RUN python3 -m pip install --no-cache-dir --break-system-packages \
    RTIMULib \
    sense-hat \
    paho-mqtt \
    && apk del .build-deps

WORKDIR /app
COPY sensehat_mqtt.py /app/
COPY run.sh /run.sh
RUN chmod +x /run.sh

LABEL \
    io.hass.version="${BUILD_VERSION}" \
    io.hass.type="addon" \
    io.hass.arch="${BUILD_ARCH}"

CMD [ "/run.sh" ]
