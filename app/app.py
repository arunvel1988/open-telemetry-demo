
from flask import Flask
import logging, time, os
from random import randint

# OpenTelemetry + Prometheus
from opentelemetry import trace
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.instrumentation.logging import LoggingInstrumentor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.exporter.otlp.proto.http.metrics_exporter import OTLPMetricExporter
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from prometheus_flask_exporter import PrometheusMetrics

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("flask-app")
LoggingInstrumentor().instrument(set_logging_format=True)

# Tracing
trace.set_tracer_provider(TracerProvider(resource=Resource.create({SERVICE_NAME: "flask-ecomm"})))
span_proc = BatchSpanProcessor(OTLPSpanExporter(endpoint=os.environ.get("OTEL_EXPORTER_OTLP_ENDPOINT", "http://otel-collector:4318/v1/traces")))
trace.get_tracer_provider().add_span_processor(span_proc)

# Metrics
metric_reader = PeriodicExportingMetricReader(OTLPMetricExporter(endpoint=os.environ.get("OTEL_EXPORTER_OTLP_ENDPOINT", "http://otel-collector:4318/v1/metrics")))
meter_provider = MeterProvider(resource=Resource.create({SERVICE_NAME: "flask-ecomm"}), metric_readers=[metric_reader])
metrics = PrometheusMetrics(app=None)
metrics.set_app_name("flask-app")

app = Flask(__name__)
FlaskInstrumentor().instrument_app(app)
metrics.init_app(app)

@app.route("/")
def home():
    logger.info("Home hit")
    return "Welcome to Home!"

@app.route("/checkout")
def checkout():
    logger.info("Checkout started")
    time.sleep(0.5)
    logger.info("Checkout complete")
    return "Order placed!"

@app.route("/slow")
def slow():
    time.sleep(randint(2, 4))
    return "This was slow!"

@app.route("/error")
def error():
    logger.error("An error occurred!")
    raise Exception("Test exception")

@app.route("/s1")
def s1():
    return "Service 1 response"

@app.route("/s2")
def s2():
    return "Service 2 response"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

