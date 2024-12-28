"""Módulo de inicialização dos clusters.

Este módulo é responsável por inicializar e gerenciar os diferentes
tipos de clusters disponíveis na aplicação.

Estrutura do módulo:
- debug/: Ferramentas de debug
- deploy/: Scripts de deploy
- evolutionapi/: API específica
- indexes/: Índices e estruturas de dados
- tools/: Ferramentas específicas
- utils/: Utilitários específicos
- supabase/: Integrações com Supabase
"""
from typing import Optional
from .base import BaseCluster
from .production import ProductionCluster
from .local import LocalCluster
from config.settings import Settings
import os

_cluster_instance: Optional[BaseCluster] = None

def get_cluster(settings: Optional[Settings] = None) -> BaseCluster:
    """Retorna a instância do cluster apropriado baseado nas configurações.
    
    Args:
        settings: Configurações da aplicação. Se None, cria uma nova instância.
    
    Returns:
        Instância do cluster configurado
    """
    global _cluster_instance
    
    if _cluster_instance is None:
        if settings is None:
            settings = Settings(
                SUPABASE_URL=os.getenv("SUPABASE_URL", ""),
                SUPABASE_KEY=os.getenv("SUPABASE_KEY", "")
            )
        
        if settings.ENVIRONMENT == "production":
            _cluster_instance = ProductionCluster(settings)
        else:
            _cluster_instance = LocalCluster(settings)
            
    return _cluster_instance 