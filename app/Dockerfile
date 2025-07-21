FROM python:3.9-slim
WORKDIR /app
COPY app.py . 
RUN pip install flask opentelemetry-sdk opentelemetry-instrumentation-flask \
    opentelemetry-exporter-otlp prometheus_flask_exporter
CMD ["python", "app.py"]
