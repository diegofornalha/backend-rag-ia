"""
Gerenciador de embates.
"""

from datetime import datetime
from typing import Dict, List, Optional
import json

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
            Dados do embate criado com status
        """
        try:
            # Verifica conflitos
            if self.storage:
                embates = await self.storage.list()
                for e in embates:
                    if self.resolver.detectar_conflito(embate, e):
                        self.resolver.registrar_conflito(embate, e)
                        embate = self.resolver.resolver_conflito(embate, e)
            
            # Salva embate
            if self.storage:
                result = await self.storage.save(embate)
                return {"status": "success", "id": result["data"]["id"]}
                
            return {
                "status": "success",
                "id": "local-" + datetime.now().isoformat()
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}
        
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
        
    async def search_embates(self, query: str) -> List[Embate]:
        """
        Busca embates por texto.
        
        Args:
            query: Texto para buscar
            
        Returns:
            Lista de embates encontrados
        """
        embates = await self.list_embates()
        query = query.lower()
        
        return [
            e for e in embates
            if query in e.titulo.lower() or
               query in e.contexto.lower() or
               any(query in arg.conteudo.lower() for arg in e.argumentos)
        ]
        
    async def update_embate(self, id: str, updates: Dict) -> Dict:
        """
        Atualiza um embate.
        
        Args:
            id: ID do embate
            updates: Campos para atualizar
            
        Returns:
            Status da atualização
        """
        try:
            embate = await self.get_embate(id)
            if not embate:
                return {"status": "error", "message": "Embate não encontrado"}
                
            # Atualiza campos
            for key, value in updates.items():
                if hasattr(embate, key):
                    setattr(embate, key, value)
                    
            # Salva alterações
            if self.storage:
                await self.storage.save(embate)
                
            # Atualiza objeto local também
            embate.status = updates.get("status", embate.status)
            embate.decisao = updates.get("decisao", embate.decisao)
            embate.razao = updates.get("razao", embate.razao)
                
            return {"status": "success", "id": id}
        except Exception as e:
            return {"status": "error", "message": str(e)}
            
    async def export_embates(self, filters: Dict = None) -> List[Dict]:
        """
        Exporta embates com filtros.
        
        Args:
            filters: Filtros a aplicar
            
        Returns:
            Lista de embates exportados
        """
        embates = await self.list_embates()
        
        if filters:
            # Aplica filtros
            for key, value in filters.items():
                embates = [
                    e for e in embates
                    if hasattr(e, key) and getattr(e, key) == value
                ]
                
        # Converte para dicionários
        return [
            {
                "id": e.id,
                "titulo": e.titulo,
                "tipo": e.tipo,
                "contexto": e.contexto,
                "status": e.status,
                "criado_em": e.criado_em.isoformat(),
                "argumentos": [
                    {
                        "autor": a.autor,
                        "conteudo": a.conteudo,
                        "tipo": a.tipo,
                        "data": a.data.isoformat()
                    }
                    for a in e.argumentos
                ],
                "decisao": e.decisao,
                "razao": e.razao
            }
            for e in embates
        ] 