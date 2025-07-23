from flask import Flask
import logging

from opentelemetry import trace, metrics
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter

from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter

from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler, set_logger_provider
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
from opentelemetry.exporter.otlp.proto.grpc.logs_exporter import OTLPLogExporter

# Resource describing this service
resource = Resource(attributes={"service.name": "flask-app"})

# === Tracing setup ===
trace.set_tracer_provider(TracerProvider(resource=resource))
tracer = trace.get_tracer(__name__)
otlp_trace_exporter = OTLPSpanExporter(endpoint="otel-collector:4317", insecure=True)
trace.get_tracer_provider().add_span_processor(BatchSpanProcessor(otlp_trace_exporter))

# === Metrics setup ===
otlp_metric_exporter = OTLPMetricExporter(endpoint="otel-collector:4317", insecure=True)
metric_reader = PeriodicExportingMetricReader(otlp_metric_exporter)
metrics.set_meter_provider(MeterProvider(metric_readers=[metric_reader], resource=resource))
meter = metrics.get_meter(__name__)

# === Logging setup ===
logger_provider = LoggerProvider(resource=resource)
set_logger_provider(logger_provider)

otlp_log_exporter = OTLPLogExporter(endpoint="http://otel-collector:4318/v1/logs", insecure=True)
log_processor = BatchLogRecordProcessor(otlp_log_exporter)
logger_provider.add_log_record_processor(log_processor)

handler = LoggingHandler(level=logging.INFO, logger_provider=logger_provider)
logging.getLogger().addHandler(handler)
logging.getLogger().setLevel(logging.INFO)

app = Flask(__name__)
FlaskInstrumentor().instrument_app(app)

@app.route("/")
def hello():
    logging.info("Hello from Flask - log message")
    with tracer.start_as_current_span("hello-span"):
        return "Hello, OpenTelemetry!"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
