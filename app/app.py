import logging
from flask import Flask
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler, BatchLogProcessor
from opentelemetry.exporter.otlp.proto.http._log_exporter import OTLPLogExporter
from opentelemetry import trace
from opentelemetry._logs import set_logger_provider, get_logger

# ----- Tracing -----
resource = Resource(attributes={SERVICE_NAME: "flask-app"})

trace.set_tracer_provider(TracerProvider(resource=resource))
tracer = trace.get_tracer(__name__)
otlp_exporter = OTLPSpanExporter(endpoint="http://otel-collector:4318/v1/traces")
trace.get_tracer_provider().add_span_processor(BatchSpanProcessor(otlp_exporter))

# ----- Logging -----
log_exporter = OTLPLogExporter(endpoint="http://otel-collector:4318/v1/logs")
logger_provider = LoggerProvider(resource=resource)
logger_provider.add_log_processor(BatchLogProcessor(log_exporter))
set_logger_provider(logger_provider)
otel_logger = get_logger(__name__)

# Python logging setup
otel_handler = LoggingHandler(level=logging.INFO, logger=otel_logger)
logging.basicConfig(level=logging.INFO, handlers=[otel_handler, logging.StreamHandler()])
logger = logging.getLogger("flask-app")

# ----- Flask App -----
app = Flask(__name__)
FlaskInstrumentor().instrument_app(app)

@app.route("/")
def home():
    logger.info("Home page accessed")
    return "Hello from Flask!"

@app.route("/error")
def error():
    logger.error("Error occurred")
    return "Something went wrong", 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
