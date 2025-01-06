"""
Configurações do ambiente de execução.
"""

# Versão do Python
PYTHON_VERSION = "3.11"

# Configuração de Cache
CACHE_CONFIG = {
    "type": "distributed",
    "cleanup_interval": "1h",
    "max_size": "2GB",
    "backend": "redis",
    "options": {"host": "localhost", "port": 6379, "db": 0},
}

# Configuração do Banco de Dados
DB_CONFIG = {
    "type": "postgresql",
    "extensions": ["pgvector"],
    "indexes": {
        "embeddings": {
            "type": "cosine_similarity",
            "dimensions": 1536,  # OpenAI embeddings
        }
    },
    "pool": {"min_size": 10, "max_size": 20, "max_queries": 50000, "timeout": 30},
}

# Configurações de Logging
LOG_CONFIG = {
    "level": "INFO",
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "handlers": ["console", "file"],
    "rotation": "1 day",
    "retention": "1 week",
}

# Métricas e Monitoramento
METRICS_CONFIG = {
    "enabled": True,
    "collection_interval": "1m",
    "retention_period": "7d",
    "exporters": ["prometheus"],
    "labels": {"environment": "production", "service": "backend-rag"},
}

# Configurações de Segurança
SECURITY_CONFIG = {
    "cors": {
        "allowed_origins": ["*"],
        "allowed_methods": ["GET", "POST", "PUT", "DELETE"],
        "allowed_headers": ["*"],
        "expose_headers": ["*"],
        "max_age": 600,
    },
    "rate_limit": {"enabled": True, "requests": 100, "window": "1m"},
}

# Configurações de Deploy
DEPLOY_CONFIG = {
    "strategy": "rolling",
    "replicas": 3,
    "health_check": {"path": "/api/v1/health", "interval": "30s", "timeout": "5s", "retries": 3},
    "resources": {"cpu": "1", "memory": "2Gi"},
}
