"""Sistema base de monitoramento."""

import time
from pathlib import Path
import psutil
import logging
from prometheus_client import start_http_server, Counter, Histogram, Gauge
import requests
from typing import Dict, Any, Optional
import json
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
        
        # Inicia servidor Prometheus
        start_http_server(self.monitoring_config.get('prometheus_port', 9090))
        
        # Inicializa métricas
        self._setup_metrics()
    
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Carrega configurações do arquivo YAML."""
        try:
            with open(config_path) as f:
                return yaml.safe_load(f)
        except Exception as e:
            logger.warning(f"Erro ao carregar config {config_path}: {e}")
            return {}
    
    def _setup_metrics(self) -> None:
        """Configura métricas do Prometheus."""
        # Métricas de Negócio
        self.embates_total = Counter('embates_total', 'Total de embates', ['status'])
        self.resolucao_tempo = Histogram('resolucao_tempo', 'Tempo de resolução em horas', 
                                       buckets=[1, 4, 12, 24, 48, 72])
        self.concordancia_taxa = Gauge('concordancia_taxa', 'Taxa de concordância em decisões')
        self.tags_uso = Counter('tags_uso', 'Uso de tags', ['tag'])

        # Métricas de Embedding
        self.embedding_tempo = Histogram('embedding_tempo', 'Tempo de processamento do embedding em segundos', 
                                       buckets=[0.1, 0.5, 1, 2, 5])
        self.embedding_memoria = Gauge('embedding_memoria', 'Uso de memória do processo de embedding em MB')
        self.embedding_cache = Counter('embedding_cache', 'Cache hits/misses', ['tipo'])
        self.embedding_erros = Counter('embedding_erros', 'Erros no processo de embedding', ['tipo'])

        # Métricas de API
        self.api_requests = Counter('api_requests', 'Requisições à API', ['endpoint', 'method'])
        self.api_latency = Histogram('api_latency', 'Latência da API em segundos', 
                                   buckets=[0.05, 0.1, 0.2, 0.5, 1])
        self.api_erros = Counter('api_erros', 'Erros na API', ['endpoint', 'code'])

        # Métricas de Sistema
        self.sistema_memoria = Gauge('sistema_memoria', 'Uso de memória do sistema em porcentagem')
        self.sistema_cpu = Gauge('sistema_cpu', 'Uso de CPU do sistema em porcentagem')
        self.sistema_disco = Gauge('sistema_disco', 'Uso de disco em porcentagem')
    
    def check_embates(self) -> None:
        """Verifica métricas relacionadas aos embates."""
        if not self.monitoring_config.get('metrics', {}).get('business', {}).get('enabled', True):
            return
            
        try:
            abertos = resolvidos = 0
            tempos_resolucao = []
            concordancias = []
            tags = {}
            
            for arquivo in self.embates_dir.glob('*.json'):
                with open(arquivo) as f:
                    embate = json.load(f)
                
                # Status
                if embate['status'] == 'aberto':
                    abertos += 1
                else:
                    resolvidos += 1
                    
                    # Tempo de resolução
                    if 'data_inicio' in embate and 'data_resolucao' in embate:
                        inicio = time.strptime(embate['data_inicio'], "%Y-%m-%dT%H:%M:%S")
                        fim = time.strptime(embate['data_resolucao'], "%Y-%m-%dT%H:%M:%S")
                        horas = (time.mktime(fim) - time.mktime(inicio)) / 3600
                        tempos_resolucao.append(horas)
                        self.resolucao_tempo.observe(horas)
                
                # Concordância
                if embate.get('decisao') and embate.get('argumentos'):
                    votos_favor = sum(1 for arg in embate['argumentos'] if 'concordo' in arg['conteudo'].lower())
                    concordancia = votos_favor / len(embate['argumentos'])
                    concordancias.append(concordancia)
                
                # Tags
                for tag in embate.get('tags', []):
                    tags[tag] = tags.get(tag, 0) + 1
            
            # Atualiza métricas
            self.embates_total.labels(status='aberto').inc(abertos)
            self.embates_total.labels(status='resolvido').inc(resolvidos)
            
            if concordancias:
                self.concordancia_taxa.set(sum(concordancias) / len(concordancias))
            
            for tag, count in tags.items():
                self.tags_uso.labels(tag=tag).inc(count)
            
        except Exception as e:
            logger.error(f"Erro ao verificar embates: {e}")
            self.api_erros.labels(endpoint='/embates', code='internal').inc()
    
    def check_embedding(self) -> None:
        """Monitora performance do embedding."""
        if not self.monitoring_config.get('metrics', {}).get('embedding', {}).get('enabled', True):
            return
            
        try:
            # Simula uma requisição de embedding
            start_time = time.time()
            response = requests.post(f"{self.api_url}/embedding", json={"text": "teste"})
            duration = time.time() - start_time
            
            self.embedding_tempo.observe(duration)
            
            if response.status_code == 200:
                self.embedding_cache.labels(tipo='hit' if response.headers.get('X-Cache') == 'HIT' else 'miss').inc()
            else:
                self.embedding_erros.labels(tipo='http').inc()
            
            # Monitora uso de memória
            process = psutil.Process()
            memoria_mb = process.memory_info().rss / 1024 / 1024
            self.embedding_memoria.set(memoria_mb)
            
        except Exception as e:
            logger.error(f"Erro ao monitorar embedding: {e}")
            self.embedding_erros.labels(tipo='connection').inc()
    
    def check_sistema(self) -> None:
        """Monitora recursos do sistema."""
        if not self.monitoring_config.get('metrics', {}).get('system', {}).get('enabled', True):
            return
            
        try:
            self.sistema_cpu.set(psutil.cpu_percent())
            self.sistema_memoria.set(psutil.virtual_memory().percent)
            self.sistema_disco.set(psutil.disk_usage('/').percent)
        except Exception as e:
            logger.error(f"Erro ao monitorar sistema: {e}")
    
    def run(self) -> None:
        """Executa o loop principal de monitoramento."""
        logger.info("Iniciando monitoramento...")
        
        while True:
            try:
                if self.test_settings.get('auto_proceed', True):
                    self.check_embates()
                    self.check_embedding()
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
