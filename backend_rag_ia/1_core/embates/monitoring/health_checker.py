from typing import Dict, Any
from datetime import datetime, timedelta
import asyncio
import logging

from ..metrics.render_metrics import RenderMetrics
from ..logging.render_logger import RenderLogger
from ..cache.cache_manager import EmbateCache

logger = logging.getLogger(__name__)

class HealthChecker:
    """Monitor de saúde do sistema de embates"""
    
    def __init__(self):
        self.render_metrics = RenderMetrics()
        self.logger = RenderLogger("health_checker")
        self.cache = EmbateCache()
        self._last_check = None
        self._health_status = {"status": "starting"}
        self._check_interval = 60  # segundos
        
    async def start_monitoring(self):
        """Inicia o monitoramento contínuo"""
        self.logger.info("Iniciando monitoramento de saúde")
        asyncio.create_task(self._monitoring_loop())
        
    async def get_health_status(self) -> Dict[str, Any]:
        """Retorna o status atual de saúde do sistema"""
        if not self._last_check or \
           datetime.utcnow() - self._last_check > timedelta(seconds=self._check_interval * 2):
            await self._perform_health_check()
            
        return self._health_status
        
    async def _monitoring_loop(self):
        """Loop principal de monitoramento"""
        while True:
            try:
                await self._perform_health_check()
                await asyncio.sleep(self._check_interval)
            except Exception as e:
                self.logger.error(f"Erro no loop de monitoramento: {e}")
                await asyncio.sleep(5)  # Espera antes de tentar novamente
                
    async def _perform_health_check(self):
        """Realiza verificação completa de saúde"""
        try:
            checks = {
                "cache": await self._check_cache(),
                "metrics": await self._check_metrics(),
                "memory": await self._check_memory(),
                "response_time": await self._check_response_time()
            }
            
            # Atualiza status geral
            status = "healthy"
            if any(not check["healthy"] for check in checks.values()):
                status = "degraded"
            if all(not check["healthy"] for check in checks.values()):
                status = "unhealthy"
                
            self._health_status = {
                "status": status,
                "timestamp": datetime.utcnow().isoformat(),
                "checks": checks
            }
            
            # Registra métricas
            await self.render_metrics.record_gauge(
                "system_health_status",
                1.0 if status == "healthy" else 0.0
            )
            
            # Registra no log
            self.logger.info(
                f"Health check completado: {status}",
                {"health_status": self._health_status}
            )
            
            self._last_check = datetime.utcnow()
            
        except Exception as e:
            self.logger.error(f"Falha no health check: {e}")
            self._health_status = {
                "status": "error",
                "timestamp": datetime.utcnow().isoformat(),
                "error": str(e)
            }
            
    async def _check_cache(self) -> Dict[str, Any]:
        """Verifica saúde do cache"""
        try:
            test_key = "health_check_test"
            test_value = {"timestamp": datetime.utcnow().isoformat()}
            
            await self.cache.set(test_key, test_value)
            cached_value = await self.cache.get(test_key)
            await self.cache.delete(test_key)
            
            return {
                "healthy": cached_value is not None,
                "latency_ms": 0,  # TODO: Implementar medição de latência
                "message": "Cache operacional"
            }
            
        except Exception as e:
            return {
                "healthy": False,
                "error": str(e),
                "message": "Falha no cache"
            }
            
    async def _check_metrics(self) -> Dict[str, Any]:
        """Verifica sistema de métricas"""
        try:
            # Tenta registrar uma métrica de teste
            await self.render_metrics.record_counter(
                "health_check_test",
                1.0
            )
            
            return {
                "healthy": True,
                "message": "Sistema de métricas operacional"
            }
            
        except Exception as e:
            return {
                "healthy": False,
                "error": str(e),
                "message": "Falha no sistema de métricas"
            }
            
    async def _check_memory(self) -> Dict[str, Any]:
        """Verifica uso de memória"""
        try:
            import psutil
            
            process = psutil.Process()
            memory_info = process.memory_info()
            memory_percent = process.memory_percent()
            
            # Alerta se uso de memória > 80%
            is_healthy = memory_percent < 80.0
            
            return {
                "healthy": is_healthy,
                "memory_used_mb": memory_info.rss / (1024 * 1024),
                "memory_percent": memory_percent,
                "message": "Uso de memória normal" if is_healthy else "Uso de memória elevado"
            }
            
        except Exception as e:
            return {
                "healthy": False,
                "error": str(e),
                "message": "Falha ao verificar memória"
            }
            
    async def _check_response_time(self) -> Dict[str, Any]:
        """Verifica tempo de resposta do sistema"""
        try:
            start_time = datetime.utcnow()
            
            # Simula uma operação básica
            await asyncio.sleep(0.1)
            
            response_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            is_healthy = response_time < 500  # Alerta se > 500ms
            
            return {
                "healthy": is_healthy,
                "response_time_ms": response_time,
                "message": "Tempo de resposta normal" if is_healthy else "Tempo de resposta elevado"
            }
            
        except Exception as e:
            return {
                "healthy": False,
                "error": str(e),
                "message": "Falha ao verificar tempo de resposta"
            } 