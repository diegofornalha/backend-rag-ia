"""
Pacote para gerenciamento de embates.
Fornece funcionalidades para criar, editar, buscar e gerenciar embates.
"""

from .commands import cli
from .manager import EmbateManager
from .models import Argumento, Embate
from .storage import SupabaseStorage

__all__ = ['Argumento', 'Embate', 'EmbateManager', 'SupabaseStorage', 'cli'] 