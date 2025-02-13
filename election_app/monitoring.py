# election_app/monitoring.py
import psutil
import time


def get_cpu_memory_usage():
    # Возвращает текущий процент загрузки CPU и использование памяти в МБ
    process = psutil.Process()
    cpu_percent = psutil.cpu_percent(interval=1)  # измеряем за 1 секунду
    mem_info = process.memory_info()
    mem_usage_mb = mem_info.rss / (1024 * 1024)  # rss – используемая память в байтах
    return cpu_percent, mem_usage_mb


def benchmark_tracing_operation(operation, *args, **kwargs):
    """
    Функция для измерения времени выполнения, загрузки CPU и использования памяти
    операции трассировки/мониторинга.
    """
    start_time = time.time()
    cpu_before, mem_before = get_cpu_memory_usage()

    result = operation(*args, **kwargs)

    cpu_after, mem_after = get_cpu_memory_usage()
    elapsed = time.time() - start_time
    cpu_delta = cpu_after - cpu_before
    mem_delta = mem_after - mem_before
    return {
        "result": result,
        "elapsed_time": elapsed,
        "cpu_delta": cpu_delta,
        "memory_delta_mb": mem_delta
    }
