"""
Sistema de embates para monitoramento.
"""

import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, Optional
from collections import defaultdict
import time

import yaml

logger = logging.getLogger(__name__)

class EmbatesMonitor:
    """Controle de embates para monitoramento."""
    
    def __init__(self, config: Dict[str, Any]):
        """Inicializa o monitor de embates."""
        self.config = config
        self.tools_count = 0
        self.embate_ativo = True
        self.ultima_verificacao = datetime.now()
        self.metricas_hidratacao = {
            "cpu": 0.0,
            "memoria": 0.0,
            "disco": 0.0,
            "rede": 0.0
        }
        
        # Configurações anti-DDoS
        self.ddos_config = {
            "janela_tempo": 60,  # Janela de tempo em segundos
            "max_requisicoes": 1000,  # Máximo de requisições por janela
            "tempo_bloqueio": 300,  # Tempo de bloqueio em segundos
            "limite_cpu": 80,  # Limite de CPU para considerar ataque
            "limite_memoria": 90  # Limite de memória para considerar ataque
        }
        
        # Controle de requisições
        self.requisicoes = defaultdict(list)  # IP -> lista de timestamps
        self.ips_bloqueados = {}  # IP -> timestamp do bloqueio
        self.alertas_ddos = []  # Lista de alertas de DDoS
        
    def verificar_ddos(self, ip: str) -> bool:
        """Verifica se há tentativa de DDoS para um IP."""
        agora = datetime.now()
        
        # Limpa IPs bloqueados antigos
        self._limpar_bloqueios_expirados(agora)
        
        # Verifica se IP está bloqueado
        if ip in self.ips_bloqueados:
            return True
            
        # Atualiza e verifica requisições
        self._atualizar_requisicoes(ip, agora)
        
        # Verifica limites
        if self._verificar_limites_ddos(ip):
            self._bloquear_ip(ip, agora)
            return True
            
        return False
        
    def _limpar_bloqueios_expirados(self, agora: datetime) -> None:
        """Remove bloqueios expirados."""
        ips_expirados = [
            ip for ip, tempo_bloqueio in self.ips_bloqueados.items()
            if (agora - tempo_bloqueio).total_seconds() > self.ddos_config["tempo_bloqueio"]
        ]
        for ip in ips_expirados:
            del self.ips_bloqueados[ip]
            logger.info(f"Bloqueio expirado para IP: {ip}")
            
    def _atualizar_requisicoes(self, ip: str, agora: datetime) -> None:
        """Atualiza o registro de requisições."""
        # Remove requisições antigas
        janela = timedelta(seconds=self.ddos_config["janela_tempo"])
        self.requisicoes[ip] = [
            tempo for tempo in self.requisicoes[ip]
            if (agora - tempo) <= janela
        ]
        
        # Adiciona nova requisição
        self.requisicoes[ip].append(agora)
        
    def _verificar_limites_ddos(self, ip: str) -> bool:
        """Verifica se os limites de DDoS foram excedidos."""
        # Verifica quantidade de requisições
        if len(self.requisicoes[ip]) > self.ddos_config["max_requisicoes"]:
            logger.warning(f"Limite de requisições excedido para IP: {ip}")
            return True
            
        # Verifica uso de recursos
        if (self.metricas_hidratacao["cpu"] * 100 > self.ddos_config["limite_cpu"] and
            self.metricas_hidratacao["memoria"] * 100 > self.ddos_config["limite_memoria"]):
            logger.warning(f"Uso suspeito de recursos detectado para IP: {ip}")
            return True
            
        return False
        
    def _bloquear_ip(self, ip: str, agora: datetime) -> None:
        """Bloqueia um IP por tentativa de DDoS."""
        self.ips_bloqueados[ip] = agora
        logger.warning(f"IP bloqueado por suspeita de DDoS: {ip}")
        
        # Registra alerta
        self.alertas_ddos.append({
            "ip": ip,
            "timestamp": agora.isoformat(),
            "requisicoes": len(self.requisicoes[ip]),
            "metricas": {
                "cpu": self.metricas_hidratacao["cpu"],
                "memoria": self.metricas_hidratacao["memoria"]
            }
        })
        
    def hidratar_metrica(self, nome: str, valor: float) -> None:
        """Hidrata uma métrica específica."""
        if not self.embate_ativo:
            logger.warning(f"Tentativa de hidratação com embate inativo: {nome}")
            return
            
        if nome not in self.metricas_hidratacao:
            logger.error(f"Métrica desconhecida: {nome}")
            return
            
        # Validação de limites
        if not 0 <= valor <= 1:
            logger.warning(f"Valor fora dos limites para {nome}: {valor}")
            valor = max(0, min(1, valor))
            
        self.metricas_hidratacao[nome] = valor
        logger.info(f"Métrica {nome} hidratada: {valor:.2f}")
        
    def verificar_limites(self) -> Dict[str, bool]:
        """Verifica se as métricas ultrapassaram os limites."""
        thresholds = self.config.get('monitoring', {}).get('metrics', {}).get('system', {}).get('thresholds', {})
        
        return {
            "cpu": (self.metricas_hidratacao["cpu"] * 100) > thresholds.get('cpu_max', 80),
            "memoria": (self.metricas_hidratacao["memoria"] * 100) > thresholds.get('memoria_max', 80),
            "disco": (self.metricas_hidratacao["disco"] * 100) > thresholds.get('disco_max', 90)
        }
        
    def incrementar_tools(self) -> bool:
        """Incrementa o contador de ferramentas e verifica limites."""
        if not self.embate_ativo:
            return False
            
        self.tools_count += 1
        
        # Verifica se atingiu limite de ferramentas
        if self.tools_count >= 3:
            logger.warning("Limite de ferramentas atingido - Entrando em contenção")
            self._entrar_contencao()
            return False
            
        return True
        
    def _entrar_contencao(self) -> None:
        """Entra em modo de contenção."""
        logger.info("Sistema entrando em modo de contenção")
        self.embate_ativo = False
        self.tools_count = 0
        
    def retomar_embate(self) -> None:
        """Retoma o embate após contenção."""
        if not self.embate_ativo:
            logger.info("Retomando embate após contenção")
            self.embate_ativo = True
            self.tools_count = 0
            self.ultima_verificacao = datetime.now()
        
    def gerar_relatorio(self) -> Dict[str, Any]:
        """Gera relatório do estado atual do embate."""
        return {
            "timestamp": datetime.now().isoformat(),
            "embate_ativo": self.embate_ativo,
            "tools_count": self.tools_count,
            "metricas_hidratacao": self.metricas_hidratacao,
            "limites_excedidos": self.verificar_limites(),
            "ddos_stats": {
                "ips_bloqueados": len(self.ips_bloqueados),
                "alertas_recentes": len(self.alertas_ddos),
                "ultima_atualizacao": datetime.now().isoformat()
            }
        }
        
    def salvar_relatorio(self, diretorio: Path) -> None:
        """Salva o relatório em arquivo."""
        relatorio = self.gerar_relatorio()
        arquivo = diretorio / f"embate_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.yml"
        
        try:
            arquivo.parent.mkdir(parents=True, exist_ok=True)
            with open(arquivo, 'w') as f:
                yaml.dump(relatorio, f, default_flow_style=False)
            logger.info(f"Relatório salvo em {arquivo}")
            
            # Salva alertas DDoS separadamente se houver
            if self.alertas_ddos:
                alertas_arquivo = diretorio / f"ddos_alerts_{datetime.now().strftime('%Y%m%d_%H%M%S')}.yml"
                with open(alertas_arquivo, 'w') as f:
                    yaml.dump(self.alertas_ddos, f, default_flow_style=False)
                logger.info(f"Alertas DDoS salvos em {alertas_arquivo}")
        except Exception as e:
            logger.error(f"Erro ao salvar relatório: {e}") 