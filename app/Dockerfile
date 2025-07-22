
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .

ENV OTEL_EXPORTER_OTLP_ENDPOINT=http://otel-collector:4318

CMD ["python", "app.py"]
