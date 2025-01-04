"""Sistema base de monitoramento."""

import json
import logging
import time
from pathlib import Path
from typing import Any

import psutil
import yaml

from core.embates_monitor import EmbatesMonitor

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class Monitor:
    """Classe principal de monitoramento."""
    
    def __init__(self, config_path: str = "config.yml"):
        """Inicializa o monitor com configurações."""
        self.config = self._load_config(config_path)
        self.test_settings = self.config.get('test_settings', {})
        self.monitoring_config = self.config.get('monitoring', {})
        
        self.embates_dir = Path(self.monitoring_config.get('embates_dir', 'embates'))
        self.check_interval = self.monitoring_config.get('check_interval', 60)
        
        # Inicializa o monitor de embates
        self.embates_monitor = EmbatesMonitor(self.config)
    
    def _load_config(self, config_path: str) -> dict[str, Any]:
        """Carrega configurações do arquivo YAML."""
        try:
            with open(config_path) as f:
                return yaml.safe_load(f)
        except Exception as e:
            logger.warning(f"Erro ao carregar config {config_path}: {e}")
            return {}
    
    def check_embates(self) -> None:
        """Verifica métricas relacionadas aos embates."""
        if not self.monitoring_config.get('metrics', {}).get('business', {}).get('enabled', True):
            return
            
        try:
            # Verifica se pode incrementar ferramentas
            if not self.embates_monitor.incrementar_tools():
                logger.warning("Sistema em contenção - Aguardando...")
                time.sleep(2)  # Pausa para contenção
                self.embates_monitor.retomar_embate()
                return
                
            # Coleta métricas do sistema
            cpu = psutil.cpu_percent(interval=1) / 100
            memoria = psutil.virtual_memory().percent / 100
            disco = psutil.disk_usage('/').percent / 100
            
            # Hidrata as métricas
            self.embates_monitor.hidratar_metrica("cpu", cpu)
            self.embates_monitor.hidratar_metrica("memoria", memoria)
            self.embates_monitor.hidratar_metrica("disco", disco)
            
            # Verifica limites e gera relatório
            limites = self.embates_monitor.verificar_limites()
            if any(limites.values()):
                logger.warning("Limites excedidos detectados!")
                
            # Salva relatório
            self.embates_monitor.salvar_relatorio(self.embates_dir)
            
        except Exception as e:
            logger.error(f"Erro ao verificar embates: {e}")
    
    def check_sistema(self) -> None:
        """Verifica métricas do sistema."""
        if not self.monitoring_config.get('metrics', {}).get('system', {}).get('enabled', True):
            return
            
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            mem_percent = psutil.virtual_memory().percent
            disk_percent = psutil.disk_usage('/').percent
            
            logger.info(f"CPU: {cpu_percent}% | Memória: {mem_percent}% | Disco: {disk_percent}%")
            
        except Exception as e:
            logger.error(f"Erro ao verificar sistema: {e}")
    
    def run(self) -> None:
        """Executa o loop principal de monitoramento."""
        logger.info("Iniciando monitoramento...")
        
        try:
            while True:
                self.check_embates()
                self.check_sistema()
                time.sleep(self.check_interval)
                
        except KeyboardInterrupt:
            logger.info("Monitoramento interrompido pelo usuário")
        except Exception as e:
            logger.error(f"Erro no loop de monitoramento: {e}")
        finally:
            # Salva relatório final
            self.embates_monitor.salvar_relatorio(self.embates_dir)

if __name__ == "__main__":
    monitor = Monitor()
    monitor.run()
