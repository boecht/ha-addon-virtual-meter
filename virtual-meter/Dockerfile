ARG BUILD_FROM=ghcr.io/home-assistant/amd64-base:latest
FROM ${BUILD_FROM}

ENV PYTHONUNBUFFERED=1
WORKDIR /app

RUN apk add --no-cache python3 py3-pip

COPY requirements.txt ./
RUN python3 -m pip install --no-cache-dir -r requirements.txt

COPY app ./app
COPY defaults.json ./defaults.json
COPY run.sh /run.sh

RUN chmod +x /run.sh

CMD ["/run.sh"]
