"""Sistema base de monitoramento."""

import json
import logging
import time
from pathlib import Path
from typing import Any

import psutil
import yaml

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
        self.api_url = self.monitoring_config.get('api_url', 'http://localhost:10000')
        self.check_interval = self.monitoring_config.get('check_interval', 60)
    
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
            abertos = resolvidos = 0
            tempos_resolucao = []
            concordancias = []
            tags = {}
            
            for arquivo in self.embates_dir.glob("embate_*.json"):
                with open(arquivo) as f:
                    dados = json.load(f)
                
                # Status
                if dados['status'] == 'aberto':
                    abertos += 1
                else:
                    resolvidos += 1
                    
                    # Tempo de resolução
                    if 'data_inicio' in dados and 'data_resolucao' in dados:
                        inicio = time.strptime(dados['data_inicio'], "%Y-%m-%dT%H:%M:%S")
                        fim = time.strptime(dados['data_resolucao'], "%Y-%m-%dT%H:%M:%S")
                        horas = (time.mktime(fim) - time.mktime(inicio)) / 3600
                        tempos_resolucao.append(horas)
                
                # Concordância
                if dados.get('decisao') and dados.get('argumentos'):
                    votos_favor = sum(1 for arg in dados['argumentos'] if 'concordo' in arg['conteudo'].lower())
                    concordancia = votos_favor / len(dados['argumentos'])
                    concordancias.append(concordancia)
                
                # Tags
                for tag in dados.get('tags', []):
                    tags[tag] = tags.get(tag, 0) + 1
            
            # Log métricas
            logger.info("Métricas de embates", extra={
                'embates_abertos': abertos,
                'embates_resolvidos': resolvidos,
                'tempo_medio_resolucao': sum(tempos_resolucao)/len(tempos_resolucao) if tempos_resolucao else 0,
                'taxa_concordancia': sum(concordancias)/len(concordancias) if concordancias else 0,
                'tags': tags
            })
            
        except Exception as e:
            logger.error(f"Erro ao verificar embates: {e}")
    
    def check_sistema(self) -> None:
        """Monitora recursos do sistema."""
        if not self.monitoring_config.get('metrics', {}).get('system', {}).get('enabled', True):
            return
            
        try:
            cpu = psutil.cpu_percent()
            memoria = psutil.virtual_memory().percent
            disco = psutil.disk_usage('/').percent
            
            logger.info("Métricas do sistema", extra={
                'cpu_percent': cpu,
                'memoria_percent': memoria,
                'disco_percent': disco
            })
        except Exception as e:
            logger.error(f"Erro ao monitorar sistema: {e}")
    
    def run(self) -> None:
        """Executa o loop principal de monitoramento."""
        logger.info("Iniciando monitoramento...")
        
        while True:
            try:
                if self.test_settings.get('auto_proceed', True):
                    self.check_embates()
                    self.check_sistema()
                else:
                    # Modo interativo (não usado no momento)
                    pass
                
                time.sleep(self.check_interval)
                
            except KeyboardInterrupt:
                logger.info("Monitoramento interrompido pelo usuário")
                break
            except Exception as e:
                logger.error(f"Erro no loop de monitoramento: {e}")
                if not self.test_settings.get('fail_fast', False):
                    time.sleep(self.check_interval)
                else:
                    break

if __name__ == "__main__":
    monitor = Monitor()
    monitor.run()
