"""
Gerenciador de embates.
"""

from datetime import datetime
from typing import Dict, List, Optional

from .models import Embate
from .storage import SupabaseStorage

class ConflictResolver:
    """Resolve conflitos entre embates."""
    
    def __init__(self):
        self.conflitos: List[Dict] = []
        
    def detectar_conflito(self, embate1: Embate, embate2: Embate) -> bool:
        """Detecta conflito entre dois embates."""
        # Mesmo tipo e contexto similar
        if embate1.tipo == embate2.tipo:
            return self._contexto_similar(embate1.contexto, embate2.contexto)
        return False
        
    def registrar_conflito(self, embate1: Embate, embate2: Embate) -> None:
        """Registra um conflito."""
        self.conflitos.append({
            "embate1": embate1.id,
            "embate2": embate2.id,
            "timestamp": datetime.now(),
            "resolvido": False
        })
        
    def resolver_conflito(self, embate1: Embate, embate2: Embate) -> Embate:
        """Resolve um conflito entre embates."""
        # Por padrão, mantém o mais recente
        if embate1.criado_em > embate2.criado_em:
            return embate1
        return embate2
        
    def _contexto_similar(self, ctx1: str, ctx2: str) -> bool:
        """Verifica se dois contextos são similares."""
        # Implementação simples por enquanto
        palavras1 = set(ctx1.lower().split())
        palavras2 = set(ctx2.lower().split())
        intersecao = palavras1.intersection(palavras2)
        return len(intersecao) / max(len(palavras1), len(palavras2)) > 0.7

class EmbateManager:
    """Gerencia embates."""
    
    def __init__(self, storage: Optional[SupabaseStorage] = None):
        """
        Inicializa o gerenciador.
        
        Args:
            storage: Storage opcional para persistência
        """
        self.storage = storage
        self.resolver = ConflictResolver()
        
    async def create_embate(self, embate: Embate) -> Dict:
        """
        Cria um novo embate.
        
        Args:
            embate: Embate a criar
            
        Returns:
            Dados do embate criado
        """
        # Verifica conflitos
        if self.storage:
            embates = await self.storage.list()
            for e in embates:
                if self.resolver.detectar_conflito(embate, e):
                    self.resolver.registrar_conflito(embate, e)
                    embate = self.resolver.resolver_conflito(embate, e)
        
        # Salva embate
        if self.storage:
            return await self.storage.save(embate)
            
        return {"data": {"id": "local-" + datetime.now().isoformat()}}
        
    async def get_embate(self, id: str) -> Optional[Embate]:
        """
        Busca um embate por ID.
        
        Args:
            id: ID do embate
            
        Returns:
            Embate encontrado ou None
        """
        if self.storage:
            return await self.storage.get(id)
        return None
        
    async def list_embates(self) -> List[Embate]:
        """
        Lista todos os embates.
        
        Returns:
            Lista de embates
        """
        if self.storage:
            return await self.storage.list()
        return [] 