from flask import Flask, render_template, jsonify

from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import (
    BatchSpanProcessor,
    ConsoleSpanExporter,
)

######
import logging
from opentelemetry._logs import set_logger_provider
from opentelemetry.exporter.otlp.proto.grpc._log_exporter import (
    OTLPLogExporter,
)
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
from opentelemetry.sdk.resources import Resource

logger_provider = LoggerProvider(
    resource=Resource.create(
        {
            "service.name": "shoppingcart",
            "service.instance.id": "instance-12",
        }
    ),
)
set_logger_provider(logger_provider)
exporter = OTLPLogExporter(insecure=True)
logger_provider.add_log_record_processor(BatchLogRecordProcessor(exporter))
handler = LoggingHandler(level=logging.NOTSET, logger_provider=logger_provider)

# Attach OTLP handler to root logger
logging.getLogger().addHandler(handler)

# Create different namespaced loggers
# It is recommended to not use the root logger with OTLP handler
# so telemetry is collected only for the application
logger = logging.getLogger("myapp.area1")
######

app = Flask(__name__)

provider = TracerProvider()
processor = BatchSpanProcessor(ConsoleSpanExporter())
provider.add_span_processor(processor)

# Sets the global default tracer provider
trace.set_tracer_provider(provider)

# Creates a tracer from the global tracer provider
tracer = trace.get_tracer("my.tracer.name")


def do_work1():
    with tracer.start_as_current_span("do_work1") as span:
        # do some work that 'span' will track
        logger.info("doing work1")
        do_work2()

def do_work2():
    with tracer.start_as_current_span("do_work2") as span:
        logger.info("doing work2")
        do_work3()

def do_work3():
    with tracer.start_as_current_span("do_work3") as span:
        logger.info("doing work3")

@app.route('/')
def index():
    logger.info("In / starting render template")
    with tracer.start_as_current_span("index_route"):
        return render_template("index.html")

@app.route('/api/data', methods=["GET"])
def get_data():
    logger.info("In /api/data starting render template")
    with tracer.start_as_current_span("get_data_route"):
        return jsonify({"message": "In /api/data"})

@app.route('/api/dowork', methods=["GET"])
def do_work():
    with tracer.start_as_current_span("get_data_route"):
        do_work1()
        return jsonify({"message": "Backend dowork() method executed"})

if __name__ == "__main__":
    app.run(debug=True)
    
