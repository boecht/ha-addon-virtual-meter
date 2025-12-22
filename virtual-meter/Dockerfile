ARG BUILD_FROM
FROM ${BUILD_FROM}

ENV PYTHONUNBUFFERED=1
WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app
COPY defaults.json ./defaults.json
COPY run.sh /run.sh

RUN chmod +x /run.sh

CMD ["/run.sh"]
