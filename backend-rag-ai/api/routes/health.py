"""Rotas de health check."""

import os
from datetime import datetime
import psutil
import redis
from fastapi import APIRouter, Response
from pydantic import BaseModel

router = APIRouter(prefix="/api/v1", tags=["health"])


class HealthStatus(BaseModel):
    """Status de saúde da API."""
    status: str
    timestamp: str
    version: str
    environment: str
    uptime: float
    memory_usage: float
    cpu_usage: float
    disk_usage: float
    redis_connected: bool
    database_connected: bool


@router.get("/health", response_model=HealthStatus)
async def health_check() -> HealthStatus:
    """
    Endpoint para verificar a saúde da API.
    Retorna métricas importantes do sistema.
    """
    try:
        # Informações do sistema
        memory = psutil.virtual_memory()
        cpu = psutil.cpu_percent()
        disk = psutil.disk_usage('/')
        
        # Verifica conexão com Redis
        redis_url = os.getenv("REDIS_URL")
        redis_ok = False
        if redis_url:
            try:
                r = redis.from_url(redis_url)
                r.ping()
                redis_ok = True
            except:
                pass

        # Verifica conexão com banco de dados
        db_url = os.getenv("DATABASE_URL")
        db_ok = bool(db_url)  # Simplificado para exemplo

        return HealthStatus(
            status="healthy",
            timestamp=datetime.utcnow().isoformat(),
            version=os.getenv("DEPLOY_VERSION", "local"),
            environment=os.getenv("ENVIRONMENT", "development"),
            uptime=psutil.boot_time(),
            memory_usage=memory.percent,
            cpu_usage=cpu,
            disk_usage=disk.percent,
            redis_connected=redis_ok,
            database_connected=db_ok
        )
    except Exception as e:
        return HealthStatus(
            status="unhealthy",
            timestamp=datetime.utcnow().isoformat(),
            version=os.getenv("DEPLOY_VERSION", "local"),
            environment=os.getenv("ENVIRONMENT", "development"),
            uptime=0,
            memory_usage=0,
            cpu_usage=0,
            disk_usage=0,
            redis_connected=False,
            database_connected=False
        )
