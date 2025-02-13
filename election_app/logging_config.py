# election_app/logging_config.py
import logging
from opentelemetry.instrumentation.logging import LoggingInstrumentor

def configure_logging():
    logging.basicConfig(level=logging.INFO)
    # Инструментируем стандартное логирование, чтобы логи были связаны с трассировкой
    LoggingInstrumentor().instrument(set_logging_format=True)

configure_logging()