ARG BUILD_FROM=ghcr.io/home-assistant/amd64-base-python:3.11-alpine3.18
FROM $BUILD_FROM

# Install system dependencies
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
COPY addon_config.py .
COPY multi_battery.py .

# Copy run script
COPY run.sh /
RUN chmod a+x /run.sh

# Direct execution without S6
CMD ["python3", "/app/main.py"]
