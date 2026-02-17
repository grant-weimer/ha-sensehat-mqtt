ARG BUILD_FROM
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

RUN pip install --no-cache-dir --break-system-packages \
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
