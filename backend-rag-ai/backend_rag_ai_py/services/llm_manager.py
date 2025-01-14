"""
Gerenciador de modelos de linguagem com suporte a multiagentes.
"""

import logging
from typing import Any, Dict, Optional, AsyncIterator
from enum import Enum

import google.generativeai as genai
from langchain_ragie import RagieRetriever
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_google_genai import ChatGoogleGenerativeAI
from MultiAgente_gemini.analysis.suggestions.interfaces import CursorAI
from MultiAgente_gemini.engine.coordinator.base import AgentCoordinator
from MultiAgente_gemini.engine.llms.tracker import LlmTracker

logger = logging.getLogger(__name__)

class QueryType(Enum):
    """Tipos de queries suportados."""
    RAG = "rag"  # Usa apenas retrieval
    AGENT = "agent"  # Usa apenas agentes
    HYBRID = "hybrid"  # Combina RAG com agentes

class LLMManager:
    """Gerenciador de modelos de linguagem com suporte a multiagentes."""

    def __init__(self):
        """Inicializa o gerenciador com suporte a multiagentes."""
        self.llm_tracker = LlmTracker()
        self.cursor_ai = CursorAI()
        self.coordinator = AgentCoordinator()
        self._setup_models()

    def _setup_models(self) -> None:
        """Configura os modelos e retrievers."""
        try:
            # Configurar Gemini
            genai.configure(timeout=30)
            self.raw_model = genai.GenerativeModel("gemini-pro")
            
            # Configurar LangChain + Gemini
            self.chat_model = ChatGoogleGenerativeAI(
                model_name="gemini-pro",
                max_output_tokens=2048,
                streaming=True
            )
            
            # Configurar Ragie Retriever
            self.retriever = RagieRetriever(
                rerank=True,
                limit=3
            )
            
            # Templates de prompts especializados
            self.templates = {
                QueryType.RAG: ChatPromptTemplate.from_template(
                    """Responda a pergunta baseado APENAS no contexto fornecido.
                    Se a informação não estiver no contexto, diga que não sabe.
                    
                    Contexto: {context}
                    Pergunta: {question}
                    
                    Resposta:"""
                ),
                QueryType.AGENT: ChatPromptTemplate.from_template(
                    """Você é um agente especializado com acesso a várias ferramentas.
                    Use suas capacidades para responder a pergunta da melhor forma possível.
                    
                    Pergunta: {question}
                    
                    Resposta:"""
                ),
                QueryType.HYBRID: ChatPromptTemplate.from_template(
                    """Use tanto o contexto fornecido quanto suas capacidades como agente para responder.
                    Priorize informações do contexto, mas complemente com seu conhecimento quando relevante.
                    
                    Contexto: {context}
                    Pergunta: {question}
                    
                    Resposta:"""
                )
            }
            
            self.output_parser = StrOutputParser()
            
            # Chains especializadas
            self.chains = {
                QueryType.RAG: (
                    {"context": self.retriever, "question": RunnablePassthrough()}
                    | self.templates[QueryType.RAG]
                    | self.chat_model
                    | self.output_parser
                ),
                QueryType.AGENT: (
                    {"question": RunnablePassthrough()}
                    | self.templates[QueryType.AGENT]
                    | self.chat_model
                    | self.output_parser
                ),
                QueryType.HYBRID: (
                    {"context": self.retriever, "question": RunnablePassthrough()}
                    | self.templates[QueryType.HYBRID]
                    | self.chat_model
                    | self.output_parser
                )
            }
            
        except Exception as err:
            self.handle_error(err, "configuração dos modelos")

    def handle_error(self, error: Exception, context: str) -> None:
        """Trata erros de forma padronizada."""
        logger.error("Erro no processamento", extra={"context": context, "error": str(error)})
        if isinstance(error, ValueError):
            raise ValueError(f"Erro de valor no {context}") from error
        elif isinstance(error, ConnectionError):
            raise ConnectionError(f"Erro de conexão no {context}") from error
        else:
            raise RuntimeError(f"Erro inesperado no {context}") from error

    async def process_query(self, query: str, query_type: Optional[QueryType] = None) -> dict[str, str]:
        """Processa uma query usando o modelo e sistema multiagente."""
        try:
            # Análise inicial pelo CursorAI
            context = {"query": query, "model": self.raw_model, "tracker": self.llm_tracker}
            cursor_analysis = self.cursor_ai.analyze(context)
            
            # Determinar tipo de query se não especificado
            if query_type is None:
                query_type = (
                    QueryType.RAG if cursor_analysis.needs_context
                    else QueryType.AGENT if cursor_analysis.needs_tools
                    else QueryType.HYBRID
                )
            
            # Processar baseado no tipo
            if query_type == QueryType.AGENT:
                result = await self.coordinator.process(
                    context=context,
                    initial_analysis=cursor_analysis
                )
            else:
                result = await self.chains[query_type].ainvoke(query)

            return {
                "status": "success",
                "result": result,
                "query_type": query_type.value,
                "agent_info": cursor_analysis.metadata
            }

        except Exception as err:
            self.handle_error(err, "processamento de query")
            return {"status": "error", "result": str(err)}

    async def stream_response(self, query: str, query_type: Optional[QueryType] = None) -> AsyncIterator[str]:
        """Gera uma resposta em streaming."""
        try:
            context = {"query": query, "model": self.raw_model, "tracker": self.llm_tracker}
            cursor_analysis = self.cursor_ai.analyze(context)
            
            if query_type is None:
                query_type = (
                    QueryType.RAG if cursor_analysis.needs_context
                    else QueryType.AGENT if cursor_analysis.needs_tools
                    else QueryType.HYBRID
                )
            
            async for chunk in self.chains[query_type].astream(query):
                yield chunk

        except Exception as err:
            self.handle_error(err, "streaming de resposta")
            yield f"Erro: {str(err)}"

    async def generate_response(self, context: str) -> dict[str, str]:
        """Gera uma resposta baseada no contexto usando multiagentes."""
        try:
            # Preparação do contexto para os agentes
            agent_context = {
                "input_context": context,
                "model": self.raw_model,
                "tracker": self.llm_tracker,
            }

            # Processamento coordenado
            response = await self.coordinator.generate(context=agent_context)

            return {
                "status": "success",
                "response": response,
                "agent_metrics": self.llm_tracker.get_metrics(),
            }

        except Exception as err:
            self.handle_error(err, "geração de resposta")
            return {"status": "error", "response": str(err)}

    def get_agent_status(self) -> dict[str, Any]:
        """Retorna o status atual do sistema multiagente."""
        return {
            "cursor_ai": self.cursor_ai.name,
            "capabilities": self.cursor_ai._capabilities,
            "coordinator_status": self.coordinator.get_status(),
            "tracker_metrics": self.llm_tracker.get_metrics(),
            "available_query_types": [qt.value for qt in QueryType],
        }
