"""Módulo para padronização de mensagens de erro e sucesso.

Este módulo fornece constantes e funções para garantir consistência
nas mensagens de log em toda a aplicação.
"""
from __future__ import annotations

from enum import Enum
from typing import Any, Dict, Optional, Union

class StatusType(str, Enum):
    """Tipos de status para mensagens."""
    SUCCESS = "success"
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"

class MessageTemplate:
    """Templates para mensagens padronizadas."""
    
    # Operações Gerais
    OPERATION_SUCCESS = "Operação concluída com sucesso: {operation}"
    OPERATION_ERROR = "Erro ao executar operação: {operation}. Motivo: {reason}"
    OPERATION_WARNING = "Alerta durante operação: {operation}. Detalhes: {details}"
    
    # Banco de Dados
    DB_CONNECTION_SUCCESS = "Conexão com banco de dados estabelecida: {db_name}"
    DB_CONNECTION_ERROR = "Erro ao conectar ao banco de dados: {db_name}. Erro: {error}"
    DB_QUERY_ERROR = "Erro ao executar query: {query}. Erro: {error}"
    
    # Autenticação
    AUTH_SUCCESS = "Usuário {user} autenticado com sucesso"
    AUTH_ERROR = "Falha na autenticação do usuário {user}. Motivo: {reason}"
    AUTH_EXPIRED = "Sessão expirada para usuário {user}"
    
    # API
    API_REQUEST_SUCCESS = "Requisição processada com sucesso: {endpoint}"
    API_REQUEST_ERROR = "Erro ao processar requisição: {endpoint}. Status: {status}"
    API_VALIDATION_ERROR = "Erro de validação: {details}"
    
    # Cache
    CACHE_HIT = "Cache encontrado para chave: {key}"
    CACHE_MISS = "Cache não encontrado para chave: {key}"
    CACHE_ERROR = "Erro ao acessar cache: {error}"
    
    # Arquivos
    FILE_OPERATION_SUCCESS = "Operação em arquivo concluída: {operation} - {path}"
    FILE_OPERATION_ERROR = "Erro em operação de arquivo: {operation} - {path}. Erro: {error}"
    
    # Processamento
    PROCESS_START = "Iniciando processamento: {process}"
    PROCESS_END = "Processamento finalizado: {process}"
    PROCESS_ERROR = "Erro durante processamento: {process}. Erro: {error}"

def format_message(
    template: str,
    params: Optional[Dict[str, Any]] = None,
    **kwargs: Any
) -> str:
    """Formata uma mensagem usando um template e parâmetros.
    
    Args:
        template: Template da mensagem
        params: Dicionário com parâmetros para formatação
        **kwargs: Parâmetros adicionais para formatação
    
    Returns:
        Mensagem formatada
    """
    all_params = {}
    if params:
        all_params.update(params)
    all_params.update(kwargs)
    
    try:
        return template.format(**all_params)
    except KeyError as e:
        return f"ERRO DE FORMATAÇÃO: Parâmetro ausente {e} no template: {template}"
    except Exception as e:
        return f"ERRO DE FORMATAÇÃO: {str(e)}"

def get_status_message(
    status: Union[StatusType, str],
    operation: str,
    details: Optional[Dict[str, Any]] = None,
    **kwargs: Any
) -> str:
    """Gera uma mensagem padronizada de status.
    
    Args:
        status: Tipo do status (success, error, warning, info)
        operation: Nome da operação
        details: Detalhes adicionais para a mensagem
        **kwargs: Parâmetros adicionais para formatação
    
    Returns:
        Mensagem formatada
    """
    if isinstance(status, str):
        status = StatusType(status.lower())
    
    templates = {
        StatusType.SUCCESS: MessageTemplate.OPERATION_SUCCESS,
        StatusType.ERROR: MessageTemplate.OPERATION_ERROR,
        StatusType.WARNING: MessageTemplate.OPERATION_WARNING,
        StatusType.INFO: MessageTemplate.PROCESS_START
    }
    
    params = {"operation": operation}
    if details:
        params.update(details)
    params.update(kwargs)
    
    return format_message(templates[status], params)

# Exemplos de uso:
"""
from utils.messages import MessageTemplate, get_status_message, StatusType

# Usando template direto
msg = format_message(
    MessageTemplate.DB_CONNECTION_ERROR,
    db_name="postgres",
    error="timeout"
)

# Usando helper de status
msg = get_status_message(
    StatusType.SUCCESS,
    operation="sincronização",
    details={"items": 100}
)
""" 