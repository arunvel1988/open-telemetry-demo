from flask import Flask
import logging, time, os

# OpenTelemetry tracing + metrics + logs
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.instrumentation.logging import LoggingInstrumentor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.exporter.otlp.proto.http.metrics_exporter import OTLPMetricExporter
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from prometheus_flask_exporter import PrometheusMetrics

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("flask-app")
LoggingInstrumentor().instrument(set_logging_format=True)

# Tracing setup
trace.set_tracer_provider(TracerProvider(resource=Resource.create({SERVICE_NAME: "flask-ecomm"})))
span_proc = BatchSpanProcessor(OTLPSpanExporter(endpoint=os.environ["OTEL_EXPORTER_OTLP_ENDPOINT"]))
trace.get_tracer_provider().add_span_processor(span_proc)

# Metrics setup
metric_reader = PeriodicExportingMetricReader(OTLPMetricExporter(endpoint=os.environ["OTEL_EXPORTER_OTLP_ENDPOINT"]))
meter_provider = MeterProvider(resource=Resource.create({SERVICE_NAME: "flask-ecomm"}), metric_readers=[metric_reader])
metrics = PrometheusMetrics(app=None)
metrics.set_app_name("flask-app")

app = Flask(__name__)
FlaskInstrumentor().instrument_app(app)

@app.route("/")
def home():
    logger.info("Home endpoint hit")
    return "Hello observability world!"

@app.route("/checkout")
def checkout():
    logger.info("Checkout started")
    time.sleep(0.5)
    logger.info("Checkout completed")
    return "Order placed!"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
