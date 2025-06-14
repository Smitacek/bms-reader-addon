# Use Home Assistant base image for multi-arch support
ARG BUILD_FROM
FROM $BUILD_FROM

# Install system dependencies for serial communication
RUN apk add --no-cache \
    gcc \
    musl-dev \
    linux-headers

# Set working directory
WORKDIR /app

# Copy requirements and install Python packages
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy application files
COPY main.py .
COPY bms_parser.py .
COPY modbus.py .
COPY mqtt_helper.py .

# Copy addon-specific configuration that supports both HA options and env vars
COPY addon_config.py ./config.py

# Copy run script
COPY run.sh /

# Make run script executable
RUN chmod a+x /run.sh

# Set labels
LABEL \
    io.hass.name="BMS Reader" \
    io.hass.description="Daren BMS Reader for LiFePO4 batteries" \
    io.hass.arch="${BUILD_ARCH}" \
    io.hass.type="addon" \
    io.hass.version=${BUILD_VERSION} \
    maintainer="BMS Reader Team"

CMD [ "/run.sh" ]
