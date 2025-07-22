

from flask import Flask, jsonify
import time
import random
import logging

# OpenTelemetry
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.resources import SERVICE_NAME, Resource

# Logging
logging.basicConfig(level=logging.INFO)

app = Flask(__name__)

# Set up tracing
trace.set_tracer_provider(
    TracerProvider(resource=Resource.create({SERVICE_NAME: "demo-flask-app"}))
)
trace.get_tracer_provider().add_span_processor(
    BatchSpanProcessor(OTLPSpanExporter(endpoint="http://otel-collector:4318/v1/traces"))
)
FlaskInstrumentor().instrument_app(app)
RequestsInstrumentor().instrument()

@app.route("/")
def home():
    return jsonify({"message": "Hello, World!"})

@app.route("/slow")
def slow():
    time.sleep(random.uniform(1, 3))
    return jsonify({"message": "Slow response"})

@app.route("/error")
def error():
    return "Internal Error", 500

@app.route("/s1")
def s1():
    return jsonify({"message": "This is S1"})

@app.route("/s2")
def s2():
    return jsonify({"message": "This is S2"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
