"""
Pacote para gerenciamento de embates.
Fornece funcionalidades para criar, editar, buscar e gerenciar embates.
"""

from .models import Argumento, Embate
from .manager import EmbateManager
from .storage import SupabaseStorage
from .commands import cli

__all__ = ['Argumento', 'Embate', 'EmbateManager', 'SupabaseStorage', 'cli'] 