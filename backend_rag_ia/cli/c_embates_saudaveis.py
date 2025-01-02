"""
Módulo para gerenciamento de embates saudáveis.
"""

import numpy as np
from typing import Dict, List, Optional

from .embates.models import Argumento, Embate
from .embates.manager import EmbateManager

def cosine_similarity(vec1: np.ndarray, vec2: np.ndarray) -> float:
    """Calcula similaridade por cosseno entre dois vetores."""
    dot = np.dot(vec1, vec2)
    norm1 = np.linalg.norm(vec1)
    norm2 = np.linalg.norm(vec2)
    return dot / (norm1 * norm2)

async def iniciar(tipo: str, titulo: str, contexto: str) -> Dict:
    """
    Inicia um novo embate.
    
    Args:
        tipo: Tipo do embate
        titulo: Título do embate
        contexto: Contexto do embate
        
    Returns:
        Dados do embate criado
    """
    manager = EmbateManager()
    
    embate = Embate(
        tipo=tipo,
        titulo=titulo,
        contexto=contexto
    )
    
    result = await manager.create_embate(embate)
    return result

async def edit_embate(embate_id: str, updates: Dict) -> Dict:
    """
    Edita um embate existente.
    
    Args:
        embate_id: ID do embate
        updates: Dados para atualizar
        
    Returns:
        Dados atualizados
    """
    manager = EmbateManager()
    embate = await manager.get_embate(embate_id)
    
    if not embate:
        raise ValueError("Embate não encontrado")
        
    for key, value in updates.items():
        setattr(embate, key, value)
        
    result = await manager.create_embate(embate)
    return result

async def adicionar_argumento(embate_id: str, argumento: Argumento) -> Dict:
    """
    Adiciona um argumento a um embate.
    
    Args:
        embate_id: ID do embate
        argumento: Argumento a adicionar
        
    Returns:
        Dados atualizados
    """
    manager = EmbateManager()
    embate = await manager.get_embate(embate_id)
    
    if not embate:
        raise ValueError("Embate não encontrado")
        
    embate.argumentos.append(argumento)
    result = await manager.create_embate(embate)
    return result

async def export_embates(filtros: Optional[Dict] = None) -> List[Dict]:
    """
    Exporta embates.
    
    Args:
        filtros: Filtros opcionais
        
    Returns:
        Lista de embates exportados
    """
    manager = EmbateManager()
    embates = await manager.list_embates()
    
    if not filtros:
        return [e.dict() for e in embates]
        
    # Aplica filtros
    resultado = []
    for embate in embates:
        if all(
            getattr(embate, key, None) == value
            for key, value in filtros.items()
        ):
            resultado.append(embate.dict())
            
    return resultado

class CondensadorEmbates:
    """Condensa embates similares."""
    
    def __init__(self, manager: Optional[EmbateManager] = None):
        self.manager = manager or EmbateManager()
        
    async def condensar(self, embates: List[Embate]) -> List[Embate]:
        """
        Condensa embates similares.
        
        Args:
            embates: Lista de embates
            
        Returns:
            Lista condensada
        """
        if not embates:
            return []
            
        # Agrupa por tipo
        por_tipo: Dict[str, List[Embate]] = {}
        for e in embates:
            if e.tipo not in por_tipo:
                por_tipo[e.tipo] = []
            por_tipo[e.tipo].append(e)
            
        # Condensa cada grupo
        condensados = []
        for tipo, grupo in por_tipo.items():
            condensados.extend(self._condensar_grupo(grupo))
            
        return condensados
        
    def _condensar_grupo(self, grupo: List[Embate]) -> List[Embate]:
        """Condensa um grupo de embates do mesmo tipo."""
        if len(grupo) <= 1:
            return grupo
            
        # Calcula similaridades
        similares = []
        for i, e1 in enumerate(grupo):
            for e2 in grupo[i+1:]:
                sim = self._calcular_similaridade(e1, e2)
                if sim > 0.7:  # threshold
                    similares.append((e1, e2, sim))
                    
        # Agrupa similares
        if not similares:
            return grupo
            
        # Mantém o mais recente de cada par
        manter = set()
        remover = set()
        for e1, e2, _ in sorted(similares, key=lambda x: x[2], reverse=True):
            if e1 not in remover and e2 not in remover:
                if e1.criado_em > e2.criado_em:
                    manter.add(e1)
                    remover.add(e2)
                else:
                    manter.add(e2)
                    remover.add(e1)
                    
        return list(manter) + [e for e in grupo if e not in manter and e not in remover]
        
    def _calcular_similaridade(self, e1: Embate, e2: Embate) -> float:
        """Calcula similaridade entre dois embates."""
        # Por enquanto usa apenas o contexto
        # TODO: Usar embeddings ou outra técnica mais robusta
        palavras1 = set(e1.contexto.lower().split())
        palavras2 = set(e2.contexto.lower().split())
        intersecao = palavras1.intersection(palavras2)
        return len(intersecao) / max(len(palavras1), len(palavras2)) 