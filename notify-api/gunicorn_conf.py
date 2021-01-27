import json
import multiprocessing
import os

max_workers = os.getenv("MAX_WORKERS", "2")
workers_per_core = os.getenv("WORKERS_PER_CORE", "1")
web_concurrency = os.getenv("WEB_CONCURRENCY", None)
host = os.getenv("HOST", "0.0.0.0")
port = os.getenv("PORT", "8080")
bind_env = os.getenv("BIND", None)

if bind_env:
    use_bind = bind_env
else:
    use_bind = f"{host}:{port}"

cores = multiprocessing.cpu_count()
workers_per_core = float(workers_per_core)
default_web_concurrency = workers_per_core * cores
if web_concurrency:
    web_concurrency = int(web_concurrency)
    assert web_concurrency > 0
else:
    web_concurrency = min(int(max_workers), int(default_web_concurrency))

# Gunicorn config variables
workers = web_concurrency
bind = use_bind
keepalive = 120
errorlog = "-"
