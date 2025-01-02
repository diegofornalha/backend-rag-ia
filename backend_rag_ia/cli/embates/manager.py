"""
Gerenciamento de operações com embates.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
from pathlib import Path
import json
import shutil
from backend_rag_ia.utils.logging_config import logger
from .models import Embate
from .storage import SupabaseStorage

class ConflictResolver:
    """Resolve conflitos entre embates."""
    
    def __init__(self):
        """Inicializa o resolvedor de conflitos."""
        self.logger = logger
        self.known_locations = [
            "/embates/",
            "/02_ferramentas_rag_apenas_raiz/dados_embates/",
            "/02_ferramentas_rag_apenas_raiz/cli/dados/embates/"
        ]
    
    def has_conflicts(self, embate: Embate) -> bool:
        """
        Verifica se há conflitos para um embate.
        
        Args:
            embate: Instância de Embate para verificar
            
        Returns:
            bool indicando se há conflitos
        """
        try:
            # Verifica duplicatas
            for location in self.known_locations:
                path = Path(location) / embate.arquivo
                if path.exists():
                    with open(path) as f:
                        existing = json.load(f)
                        if existing.get("version_key") == embate.version_key:
                            return True
            return False
            
        except Exception as e:
            self.logger.error(
                "Erro ao verificar conflitos",
                extra={"error": str(e), "arquivo": embate.arquivo},
                exc_info=True
            )
            return False
    
    async def resolve_conflicts(self, embate: Embate) -> None:
        """
        Resolve conflitos para um embate.
        
        Args:
            embate: Instância de Embate para resolver conflitos
        """
        try:
            # Backup dos arquivos existentes
            for location in self.known_locations:
                path = Path(location) / embate.arquivo
                if path.exists():
                    backup_dir = path.parent / "backup"
                    backup_dir.mkdir(exist_ok=True)
                    backup_path = backup_dir / f"{path.stem}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                    shutil.copy2(path, backup_path)
                    path.unlink()
                    
            self.logger.info(
                "Conflitos resolvidos com sucesso",
                extra={"arquivo": embate.arquivo}
            )
            
        except Exception as e:
            self.logger.error(
                "Erro ao resolver conflitos",
                extra={"error": str(e), "arquivo": embate.arquivo},
                exc_info=True
            )
            raise

class EmbateManager:
    """Gerencia operações principais com embates."""
    
    def __init__(self, storage: Optional[SupabaseStorage] = None):
        """
        Inicializa o gerenciador.
        
        Args:
            storage: Instância opcional de SupabaseStorage
        """
        self.storage = storage or SupabaseStorage()
        self.conflict_resolver = ConflictResolver()
        self.logger = logger
    
    async def create_embate(self, embate: Embate) -> Dict[str, Any]:
        """
        Cria um novo embate.
        
        Args:
            embate: Instância de Embate para criar
            
        Returns:
            Dict com resultado da operação
        """
        try:
            # Verifica conflitos
            if self.conflict_resolver.has_conflicts(embate):
                await self.conflict_resolver.resolve_conflicts(embate)
            
            # Salva embate
            result = await self.storage.save_embate(embate)
            
            self.logger.info(
                "Embate criado com sucesso",
                extra={"arquivo": embate.arquivo}
            )
            return result
            
        except Exception as e:
            self.logger.error(
                "Erro ao criar embate",
                extra={"error": str(e), "arquivo": embate.arquivo},
                exc_info=True
            )
            raise
    
    async def update_embate(self, embate_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """
        Atualiza um embate existente.
        
        Args:
            embate_id: ID do embate
            updates: Dicionário com atualizações
            
        Returns:
            Dict com resultado da operação
        """
        try:
            result = await self.storage.update_embate(embate_id, updates)
            
            self.logger.info(
                "Embate atualizado com sucesso",
                extra={"embate_id": embate_id}
            )
            return result
            
        except Exception as e:
            self.logger.error(
                "Erro ao atualizar embate",
                extra={"error": str(e), "embate_id": embate_id},
                exc_info=True
            )
            raise
    
    async def search_embates(self, query: str) -> List[Dict[str, Any]]:
        """
        Busca embates.
        
        Args:
            query: Texto para buscar
            
        Returns:
            Lista de embates encontrados
        """
        try:
            results = await self.storage.search_embates(query)
            
            self.logger.info(
                "Busca realizada com sucesso",
                extra={"query": query}
            )
            return results
            
        except Exception as e:
            self.logger.error(
                "Erro ao buscar embates",
                extra={"error": str(e), "query": query},
                exc_info=True
            )
            raise
    
    async def export_embates(self, filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Exporta embates.
        
        Args:
            filters: Dicionário com filtros
            
        Returns:
            Lista de embates exportados
        """
        try:
            results = await self.storage.export_embates(filters)
            
            self.logger.info(
                "Embates exportados com sucesso",
                extra={"filters": filters}
            )
            return results
            
        except Exception as e:
            self.logger.error(
                "Erro ao exportar embates",
                extra={"error": str(e), "filters": filters},
                exc_info=True
            )
            raise 