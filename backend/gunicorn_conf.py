bind = "0.0.0.0:8000"
worker_class = "uvicorn.workers.UvicornWorker"
workers = 2
timeout = 60
graceful_timeout = 30
accesslog = "-"
errorlog = "-"
