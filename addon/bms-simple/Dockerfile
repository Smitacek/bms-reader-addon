ARG BUILD_FROM
FROM $BUILD_FROM

# Install Python packages
RUN apk add --no-cache python3 py3-pip

# Create app directory
WORKDIR /app

# Simple test script
RUN echo 'print("BMS Simple Add-on is running!")' > /app/main.py

CMD ["python3", "/app/main.py"]
