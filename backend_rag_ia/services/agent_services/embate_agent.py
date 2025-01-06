"""
Sistema de embates integrado ao multiagente.
"""

from typing import Dict, Any, Optional
from datetime import datetime
import logging
import re

from ...monitoring.metrics import Metrica
from .multi_agent import GeminiAgent, MultiAgentSystem

logger = logging.getLogger(__name__)


class EmbateAgent(GeminiAgent):
    """Agente especializado em embates."""

    PALAVRAS_CHAVE_EMBATE = [
        "compare",
        "analise",
        "debata",
        "discuta",
        "avalie",
        "critique",
        "confronte",
        "versus",
        "pros e contras",
        "vantagens e desvantagens",
        "melhor opção",
        "diferenças",
        "semelhanças",
    ]

    def __init__(self, name: str, api_key: str):
        super().__init__(name, api_key)
        self.metrica = Metrica(nome=f"embate_{name}", valor=0.0, timestamp=datetime.now())

    @classmethod
    def requer_embate(cls, prompt: str) -> bool:
        """Verifica se o prompt requer um embate."""
        prompt_lower = prompt.lower()
        return any(palavra in prompt_lower for palavra in cls.PALAVRAS_CHAVE_EMBATE)

    async def run(self, task: str, **kwargs) -> Dict[str, Any]:
        """Executa uma tarefa usando o sistema de embates."""
        try:
            # Verifica se precisa ativar embate
            if not self.requer_embate(task) and not kwargs.get("force_embate"):
                # Se não requer embate, executa normalmente
                return await super().run(task)

            # Verifica se pode usar ferramentas
            if not self.metrica.incrementar_tools():
                logger.warning(f"Agente {self.name} bloqueado por limite de ferramentas")
                return {"error": "Limite de ferramentas atingido"}

            # Prepara contexto do embate
            dados_entrada = {
                "tema": kwargs.get("tema", "debate_ia"),
                "contexto": task,
                "parametros": {"max_tokens": 2048, "temperatura": 0.7},
            }

            # Valida parâmetros
            if not self._validar_parametros(dados_entrada):
                return {"error": "Parâmetros inválidos"}

            # Executa a tarefa
            response = await super().run(task)

            # Atualiza métrica
            self.metrica.valor += 0.3

            return response

        except Exception as e:
            logger.error(f"Erro no embate: {e}")
            self.metrica.interromper_embate()
            return {"error": str(e)}

    def _validar_parametros(self, dados: Dict[str, Any]) -> bool:
        """Valida os parâmetros do embate."""
        try:
            assert dados["tema"] is not None, "Tema não pode ser nulo"
            assert isinstance(dados["parametros"], dict), "Parâmetros devem ser um dicionário"
            assert (
                0 <= dados["parametros"]["temperatura"] <= 1
            ), "Temperatura deve estar entre 0 e 1"
            assert dados["parametros"]["max_tokens"] > 0, "Max tokens deve ser positivo"
            return True
        except AssertionError as e:
            logger.error(f"Validação falhou: {e}")
            return False


class EmbateSystem(MultiAgentSystem):
    """Sistema multiagente com suporte a embates."""

    def _setup_agents(self) -> Dict[str, EmbateAgent]:
        """Configura os agentes com suporte a embates."""
        return {
            "researcher": EmbateAgent("researcher", self.api_key),
            "analyst": EmbateAgent("analyst", self.api_key),
            "improver": EmbateAgent("improver", self.api_key),
            "synthesizer": EmbateAgent("synthesizer", self.api_key),
        }

    async def process_task(
        self, task: str, context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Processa uma tarefa, ativando embate se necessário."""
        # Verifica se o prompt requer embate
        requires_embate = any(agent.requer_embate(task) for agent in self.agents.values())

        if requires_embate:
            logger.info(f"Ativando sistema de embates para a tarefa: {task}")
            context = context or {}
            context["force_embate"] = True

        return await super().process_task(task, context)

    def interromper_todos_embates(self) -> None:
        """Interrompe todos os embates ativos."""
        for agent in self.agents.values():
            agent.metrica.interromper_embate()

    def get_status_embates(self) -> Dict[str, Any]:
        """Retorna o status de todos os embates."""
        return {
            name: {
                "ativo": agent.metrica.embate_ativo,
                "tools_count": agent.metrica.tools_count,
                "valor": agent.metrica.valor,
            }
            for name, agent in self.agents.items()
        }
