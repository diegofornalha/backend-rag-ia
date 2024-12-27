from .base import BaseCluster
from .local import LocalCluster
from .production import ProductionCluster

def get_cluster():
    """Retorna o cluster apropriado baseado no ambiente"""
    from config.config import get_settings
    
    settings = get_settings()
    clusters = {
        "local": LocalCluster,
        "production": ProductionCluster
    }
    
    cluster_class = clusters.get(settings.ENVIRONMENT, LocalCluster)
    return cluster_class(settings) 