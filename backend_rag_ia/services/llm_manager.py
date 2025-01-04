"""Módulo para gerenciamento de modelos de linguagem.

Este módulo fornece funcionalidades para gerenciar e interagir com
modelos de linguagem (LLMs), incluindo configuração e chamadas.
"""

from typing import Any, Optional

from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage

from backend_rag_ia.config.env_config import get_env_config


class LLMManager:
    """Gerenciador de modelos de linguagem.

    Esta classe fornece métodos para configurar e interagir com
    modelos de linguagem (LLMs).

    Attributes
    ----------
    model : ChatOpenAI
        Modelo de linguagem configurado.
    system_prompt : str
        Prompt do sistema para contextualização.

    """

    def __init__(self, model_name: str = "gpt-3.5-turbo") -> None:
        """Inicializa o gerenciador.

        Parameters
        ----------
        model_name : str, optional
            Nome do modelo a ser usado, por padrão "gpt-3.5-turbo".

        """
        env_config = get_env_config()
        self.model = ChatOpenAI(
            model_name=model_name,
            openai_api_key=env_config.openai_api_key,
            temperature=0.7
        )
        self.system_prompt = (
            "Você é um assistente especializado em documentação técnica. "
            "Responda de forma clara e objetiva, usando exemplos quando necessário."
        )

    def generate_response(
        self,
        query: str,
        context: Optional[str] = None,
        system_prompt: Optional[str] = None
    ) -> str:
        """Gera uma resposta usando o modelo de linguagem.

        Parameters
        ----------
        query : str
            Pergunta ou prompt do usuário.
        context : str, optional
            Contexto adicional para a pergunta.
        system_prompt : str, optional
            Prompt do sistema personalizado.

        Returns
        -------
        str
            Resposta gerada pelo modelo.

        """
        messages = []

        # Adiciona o prompt do sistema
        if system_prompt:
            messages.append(SystemMessage(content=system_prompt))
        else:
            messages.append(SystemMessage(content=self.system_prompt))

        # Adiciona o contexto se fornecido
        if context:
            messages.append(
                SystemMessage(
                    content=f"Use o seguinte contexto para responder: {context}"
                )
            )

        # Adiciona a pergunta do usuário
        messages.append(HumanMessage(content=query))

        # Gera a resposta
        response = self.model.generate([messages])
        return response.generations[0][0].text

    def analyze_document(self, document: dict[str, Any]) -> dict[str, Any]:
        """Analisa um documento usando o modelo de linguagem.

        Parameters
        ----------
        document : dict[str, Any]
            Documento a ser analisado.

        Returns
        -------
        dict[str, Any]
            Análise do documento.

        """
        content = document.get("content", "")
        metadata = document.get("metadata", {})

        # Gera um resumo do documento
        summary_prompt = "Faça um resumo conciso do seguinte texto:\n\n" + content
        summary = self.generate_response(summary_prompt)

        # Extrai palavras-chave
        keywords_prompt = (
            "Extraia as 5 principais palavras-chave do texto, "
            "separadas por vírgula:\n\n" + content
        )
        keywords = self.generate_response(keywords_prompt)

        return {
            "summary": summary,
            "keywords": keywords.split(","),
            "metadata": metadata
        }
