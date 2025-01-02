"""Sistema base de monitoramento."""

import time
from pathlib import Path
import psutil
import logging
from prometheus_client import start_http_server, Counter, Histogram, Gauge
import requests
from typing import Dict, Any, Optional
import json

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Métricas de Negócio
embates_total = Counter('embates_total', 'Total de embates', ['status'])
resolucao_tempo = Histogram('resolucao_tempo', 'Tempo de resolução em horas', buckets=[1, 4, 12, 24, 48, 72])
concordancia_taxa = Gauge('concordancia_taxa', 'Taxa de concordância em decisões')
tags_uso = Counter('tags_uso', 'Uso de tags', ['tag'])

# Métricas de Embedding
embedding_tempo = Histogram('embedding_tempo', 'Tempo de processamento do embedding em segundos', buckets=[0.1, 0.5, 1, 2, 5])
embedding_memoria = Gauge('embedding_memoria', 'Uso de memória do processo de embedding em MB')
embedding_cache = Counter('embedding_cache', 'Cache hits/misses', ['tipo'])
embedding_erros = Counter('embedding_erros', 'Erros no processo de embedding', ['tipo'])

# Métricas de API
api_requests = Counter('api_requests', 'Requisições à API', ['endpoint', 'method'])
api_latency = Histogram('api_latency', 'Latência da API em segundos', buckets=[0.05, 0.1, 0.2, 0.5, 1])
api_erros = Counter('api_erros', 'Erros na API', ['endpoint', 'code'])

# Métricas de Sistema
sistema_memoria = Gauge('sistema_memoria', 'Uso de memória do sistema em porcentagem')
sistema_cpu = Gauge('sistema_cpu', 'Uso de CPU do sistema em porcentagem')
sistema_disco = Gauge('sistema_disco', 'Uso de disco em porcentagem')

class Monitor:
    """Classe principal de monitoramento."""
    
    def __init__(self, config: Dict[str, Any]):
        """Inicializa o monitor com configurações."""
        self.config = config
        self.embates_dir = Path(config.get('embates_dir', 'embates'))
        self.api_url = config.get('api_url', 'http://localhost:10000')
        self.check_interval = config.get('check_interval', 60)
        
        # Inicia servidor Prometheus
        start_http_server(config.get('prometheus_port', 9090))
    
    def check_embates(self) -> None:
        """Verifica métricas relacionadas aos embates."""
        try:
            # Contagem de embates por status
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
                        resolucao_tempo.observe(horas)
                
                # Concordância
                if embate.get('decisao') and embate.get('argumentos'):
                    votos_favor = sum(1 for arg in embate['argumentos'] if 'concordo' in arg['conteudo'].lower())
                    concordancia = votos_favor / len(embate['argumentos'])
                    concordancias.append(concordancia)
                
                # Tags
                for tag in embate.get('tags', []):
                    tags[tag] = tags.get(tag, 0) + 1
            
            # Atualiza métricas
            embates_total.labels(status='aberto').inc(abertos)
            embates_total.labels(status='resolvido').inc(resolvidos)
            
            if concordancias:
                concordancia_taxa.set(sum(concordancias) / len(concordancias))
            
            for tag, count in tags.items():
                tags_uso.labels(tag=tag).inc(count)
            
        except Exception as e:
            logger.error(f"Erro ao verificar embates: {e}")
            api_erros.labels(endpoint='/embates', code='internal').inc()
    
    def check_embedding(self) -> None:
        """Monitora performance do embedding."""
        try:
            # Simula uma requisição de embedding
            start_time = time.time()
            response = requests.post(f"{self.api_url}/embedding", json={"text": "teste"})
            duration = time.time() - start_time
            
            embedding_tempo.observe(duration)
            
            if response.status_code == 200:
                embedding_cache.labels(tipo='hit' if response.headers.get('X-Cache') == 'HIT' else 'miss').inc()
            else:
                embedding_erros.labels(tipo='http').inc()
            
            # Monitora uso de memória
            process = psutil.Process()
            memoria_mb = process.memory_info().rss / 1024 / 1024
            embedding_memoria.set(memoria_mb)
            
        except Exception as e:
            logger.error(f"Erro ao monitorar embedding: {e}")
            embedding_erros.labels(tipo='connection').inc()
    
    def check_sistema(self) -> None:
        """Monitora recursos do sistema."""
        try:
            sistema_cpu.set(psutil.cpu_percent())
            sistema_memoria.set(psutil.virtual_memory().percent)
            sistema_disco.set(psutil.disk_usage('/').percent)
        except Exception as e:
            logger.error(f"Erro ao monitorar sistema: {e}")
    
    def run(self) -> None:
        """Executa o loop principal de monitoramento."""
        logger.info("Iniciando monitoramento...")
        
        while True:
            try:
                self.check_embates()
                self.check_embedding()
                self.check_sistema()
                
                time.sleep(self.check_interval)
                
            except KeyboardInterrupt:
                logger.info("Monitoramento interrompido pelo usuário")
                break
            except Exception as e:
                logger.error(f"Erro no loop de monitoramento: {e}")
                time.sleep(self.check_interval)

if __name__ == "__main__":
    config = {
        'embates_dir': 'embates',
        'api_url': 'http://localhost:10000',
        'check_interval': 60,
        'prometheus_port': 9090
    }
    
    monitor = Monitor(config)
    monitor.run()
