ARG BUILD_FROM=python:3.11-alpine
FROM $BUILD_FROM

# Install Python and dependencies
RUN apk add --no-cache \
    python3 \
    py3-pip \
    py3-setuptools \
    py3-wheel \
    gcc \
    musl-dev \
    python3-dev

# Set working directory
WORKDIR /app

# Copy requirements
COPY requirements.txt .

# Install Python packages
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy application files
COPY run.sh /
COPY *.py /app/
COPY addon_config.py /app/config.py

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
