from flask import Flask
import logging

from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.logs import LoggingHandler, LoggerProvider
from opentelemetry.sdk.logs.export import BatchLogRecordProcessor
from opentelemetry.exporter.otlp.proto.http.logs_exporter import OTLPLogExporter
from opentelemetry.sdk._logs import set_logger_provider

# Set up OpenTelemetry logging
resource = Resource(attributes={"service.name": "flask-app"})
logger_provider = LoggerProvider(resource=resource)
set_logger_provider(logger_provider)

otlp_exporter = OTLPLogExporter(endpoint="http://otel-collector:4318/v1/logs", insecure=True)
log_processor = BatchLogRecordProcessor(otlp_exporter)
logger_provider.add_log_record_processor(log_processor)

handler = LoggingHandler(level=logging.INFO, logger_provider=logger_provider)
logging.getLogger().addHandler(handler)
logging.getLogger().setLevel(logging.INFO)

# Flask app
app = Flask(__name__)

@app.route("/")
def hello():
    logging.info("Hello from Flask!")
    return "Hello, OpenTelemetry!"



@app.route("/error")
def error():
    logger.error("Error occurred")
    return "Something went wrong", 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
