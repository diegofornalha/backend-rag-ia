"""
Sistema de chat integrado com multiagentes.
"""

import logging
from typing import Any, Dict, List, Optional
from datetime import datetime

from .agent_services.multi_agent import MultiAgentSystem
from .llm_services.tracker import LlmTracker

logger = logging.getLogger(__name__)


class ChatSystem:
    """Sistema de chat integrado com multiagentes."""

    def __init__(self, config: dict[str, Any] | None = None):
        """Inicializa o sistema de chat."""
        self.multi_agent = MultiAgentSystem(config)
        self.tracker = LlmTracker()

    async def process_message(
        self, 
        message: str, 
        context: dict[str, Any]
    ) -> dict[str, Any]:
        """
        Processa uma mensagem do chat.

        Args:
            message: Mensagem do usuário
            context: Contexto da mensagem (cliente, documentos, etc)

        Returns:
            Resposta processada
        """
        try:
            # Registra evento de início
            self.track_chat_event("message_received", {
                "message": message,
                "context": context
            })

            # Se for upload de documento
            if context.get("is_upload"):
                response = await self.multi_agent.process_task(
                    task=message,
                    context={
                        "is_upload": True,
                        "cliente": context.get("cliente"),
                        "content": message
                    }
                )

                self.track_chat_event("upload_processed", {
                    "result": response,
                    "cliente": context.get("cliente")
                })

                return response

            # Caso contrário, processa com o pipeline normal
            response = await self.multi_agent.process_task(
                task=message,
                context={
                    "history": context.get("history", []),
                    "documents": context.get("documents", []),
                    "cliente": context.get("cliente")
                }
            )

            self.track_chat_event("message_processed", {
                "result": response
            })

            return response

        except Exception as e:
            error = f"Erro ao processar mensagem: {str(e)}"
            logger.error(error)
            self.track_chat_event("error", {"error": error})
            return {"error": error}

    def track_chat_event(self, event_type: str, data: dict[str, Any]) -> None:
        """Registra eventos do chat."""
        self.tracker.track_event(f"chat_{event_type}", {
            "timestamp": datetime.now().isoformat(),
            **data
        })

    async def validate_document(
        self, 
        content: str, 
        cliente: str
    ) -> dict[str, Any]:
        """
        Valida um documento usando o DocumentUploadAgent.

        Args:
            content: Conteúdo do documento
            cliente: Nome do cliente

        Returns:
            Resultado da validação
        """
        try:
            response = await self.multi_agent.process_task(
                task=content,
                context={
                    "is_upload": True,
                    "cliente": cliente,
                    "content": content,
                    "action": "validate"
                }
            )

            self.track_chat_event("document_validated", {
                "result": response,
                "cliente": cliente
            })

            return response

        except Exception as e:
            error = f"Erro ao validar documento: {str(e)}"
            logger.error(error)
            self.track_chat_event("validation_error", {"error": error})
            return {"error": error}

    def get_system_status(self) -> dict[str, Any]:
        """Retorna o status atual do sistema."""
        return {
            "multi_agent": self.multi_agent.get_system_status(),
            "tracker": self.tracker.get_metrics()
        } 