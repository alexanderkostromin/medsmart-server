import multiprocessing as mp

bind = "0.0.0.0:8000"
workers = mp.cpu_count() * 2 + 1
worker_class = "uvicorn.workers.UvicornWorker"
logconfig_json = "src/log-config.json"
chdir = "src"
