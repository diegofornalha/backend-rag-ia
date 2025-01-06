"""
Provider instrumentado para rastreamento de uso.
"""

from typing import Any, Dict, List, TypedDict

from .base import BaseProvider


class ChatCall(TypedDict):
    """Registro de chamada do método chat."""

    type: str
    messages: list[dict[str, Any]]
    kwargs: dict[str, Any]


class GenerateCall(TypedDict):
    """Registro de chamada do método generate."""

    type: str
    prompt: str
    kwargs: dict[str, Any]


Call = ChatCall | GenerateCall


class InstrumentedProvider(BaseProvider):
    """Provider instrumentado para rastreamento de uso."""

    def __init__(self, provider: BaseProvider):
        """
        Inicializa o provider instrumentado.

        Args:
            provider: O provider base a ser instrumentado
        """
        self.provider = provider
        self.calls: list[Call] = []

    def chat(self, messages: list[dict[str, Any]], **kwargs: Any) -> dict[str, Any]:
        """
        Processa uma conversa com o modelo.

        Args:
            messages: Lista de mensagens no formato {role: str, content: str}
            **kwargs: Argumentos adicionais para a API

        Returns:
            Dict com a resposta do modelo
        """
        self.calls.append({"type": "chat", "messages": messages, "kwargs": kwargs})
        return self.provider.chat(messages, **kwargs)

    def generate(self, prompt: str, **kwargs: Any) -> dict[str, Any]:
        """
        Gera texto a partir de um prompt.

        Args:
            prompt: O prompt para geração
            **kwargs: Argumentos adicionais para a API

        Returns:
            Dict com a resposta do modelo
        """
        self.calls.append({"type": "generate", "prompt": prompt, "kwargs": kwargs})
        return self.provider.generate(prompt, **kwargs)

    def get_calls(self) -> list[Call]:
        """Retorna a lista de chamadas registradas."""
        return self.calls
