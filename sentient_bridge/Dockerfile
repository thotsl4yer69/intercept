# Standalone image for the iNTERCEPT -> Sentient Core MQTT bridge.
# Build context is THIS directory (sentient_bridge/), so the image stays tiny
# and never pulls the full upstream platform.
#
#   docker build -t mz1312/intercept-bridge ./sentient_bridge
#   docker run --rm -e SENTIENT_MQTT_HOST=... mz1312/intercept-bridge --dry-run
FROM python:3.12-slim

WORKDIR /app
COPY . ./sentient_bridge
RUN pip install --no-cache-dir paho-mqtt

ENV PYTHONUNBUFFERED=1
# Default: simulate active-spectrum contacts and publish them to the broker.
ENTRYPOINT ["python", "-m", "sentient_bridge"]
