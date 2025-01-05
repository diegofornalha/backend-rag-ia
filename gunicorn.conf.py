"""
Configuração do Gunicorn para produção.
"""

import os
import multiprocessing

# Configurações do servidor
bind = f"{os.getenv('HOST', '0.0.0.0')}:{os.getenv('PORT', '10000')}"
workers = int(os.getenv('WORKERS', multiprocessing.cpu_count() * 2 + 1))
worker_class = os.getenv('WORKER_CLASS', 'uvicorn.workers.UvicornWorker')
timeout = int(os.getenv('TIMEOUT', 120))
keepalive = int(os.getenv('KEEPALIVE', 65))

# Limites e timeouts
max_requests = int(os.getenv('MAX_REQUESTS', 1000))
max_requests_jitter = int(os.getenv('MAX_REQUESTS_JITTER', 50))
graceful_timeout = int(os.getenv('GRACEFUL_TIMEOUT', 120))

# Logging
accesslog = '-'
errorlog = '-'
loglevel = os.getenv('LOG_LEVEL', 'info')

# SSL
ssl_redirect = os.getenv('SSL_REDIRECT', 'false').lower() == 'true'

# Hooks
def on_starting(server):
    """Log quando o servidor está iniciando."""
    server.log.info("Iniciando servidor Gunicorn...")

def on_exit(server):
    """Log quando o servidor está encerrando."""
    server.log.info("Encerrando servidor Gunicorn...") 