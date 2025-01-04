"""
Sistema de embates para monitoramento.
"""

import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

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
            "limites_excedidos": self.verificar_limites()
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
        except Exception as e:
            logger.error(f"Erro ao salvar relatório: {e}") 