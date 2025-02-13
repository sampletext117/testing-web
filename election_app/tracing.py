# election_app/tracing.py

import os
from opentelemetry import trace
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
# Если используется Jaeger – импортируйте экспортёр Jaeger
from opentelemetry.exporter.jaeger.thrift import JaegerExporter

def configure_tracing():
    # Определяем имя сервиса через переменную окружения или задаем вручную
    service_name = os.getenv("SERVICE_NAME", "eVotingService")
    resource = Resource(attributes={
        SERVICE_NAME: service_name
    })

    # Создаем провайдер трассировки
    provider = TracerProvider(resource=resource)
    trace.set_tracer_provider(provider)

    # Настраиваем экспортер – например, вывод в консоль
    console_exporter = ConsoleSpanExporter()
    span_processor = BatchSpanProcessor(console_exporter)
    provider.add_span_processor(span_processor)


# Вызов конфигурации трассировки при запуске приложения
configure_tracing()
