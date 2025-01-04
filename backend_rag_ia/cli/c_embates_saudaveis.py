"""Módulo para gerenciamento de embates saudáveis.

Este módulo fornece funcionalidades para gerenciar embates saudáveis,
incluindo criação, edição, adição de argumentos e condensação de embates similares.
"""

from typing import Optional

import numpy as np

from .embates.manager import EmbateManager
from .embates.models import Argumento, Embate


def cosine_similarity(vec1: np.ndarray, vec2: np.ndarray) -> float:
    """Calcula similaridade por cosseno entre dois vetores.

    Parameters
    ----------
    vec1 : np.ndarray
        Primeiro vetor.
    vec2 : np.ndarray
        Segundo vetor.

    Returns
    -------
    float
        Similaridade por cosseno entre os vetores.

    """
    dot = np.dot(vec1, vec2)
    norm1 = np.linalg.norm(vec1)
    norm2 = np.linalg.norm(vec2)
    return dot / (norm1 * norm2)


async def iniciar(tipo: str, titulo: str, contexto: str) -> dict:
    """Inicia um novo embate.

    Parameters
    ----------
    tipo : str
        Tipo do embate.
    titulo : str
        Título do embate.
    contexto : str
        Contexto do embate.

    Returns
    -------
    dict
        Dados do embate criado.

    """
    manager = EmbateManager()

    embate = Embate(
        tipo=tipo,
        titulo=titulo,
        contexto=contexto
    )

    result = await manager.create_embate(embate)
    return result


async def edit_embate(embate_id: str, updates: dict) -> dict:
    """Edita um embate existente.

    Parameters
    ----------
    embate_id : str
        ID do embate.
    updates : dict
        Dados para atualizar.

    Returns
    -------
    dict
        Dados atualizados.

    Raises
    ------
    ValueError
        Se o embate não for encontrado.

    """
    manager = EmbateManager()
    embate = await manager.get_embate(embate_id)

    if not embate:
        raise ValueError("Embate não encontrado")

    for key, value in updates.items():
        setattr(embate, key, value)

    result = await manager.create_embate(embate)
    return result


async def adicionar_argumento(embate_id: str, argumento: Argumento) -> dict:
    """Adiciona um argumento a um embate.

    Parameters
    ----------
    embate_id : str
        ID do embate.
    argumento : Argumento
        Argumento a adicionar.

    Returns
    -------
    dict
        Dados atualizados.

    Raises
    ------
    ValueError
        Se o embate não for encontrado.

    """
    manager = EmbateManager()
    embate = await manager.get_embate(embate_id)

    if not embate:
        raise ValueError("Embate não encontrado")

    embate.argumentos.append(argumento)
    result = await manager.create_embate(embate)
    return result


async def export_embates(filtros: Optional[dict] = None) -> list[dict]:
    """Exporta embates.

    Parameters
    ----------
    filtros : Optional[dict], optional
        Filtros opcionais, por padrão None.

    Returns
    -------
    list[dict]
        Lista de embates exportados.

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
    """Condensa embates similares.

    Esta classe fornece funcionalidades para condensar embates similares,
    reduzindo duplicidade e mantendo apenas as versões mais relevantes.

    Attributes
    ----------
    manager : Optional[EmbateManager]
        Gerenciador de embates opcional.

    """

    def __init__(self, manager: Optional[EmbateManager] = None):
        """Inicializa o condensador de embates.

        Parameters
        ----------
        manager : Optional[EmbateManager], optional
            Gerenciador de embates opcional, por padrão None.

        """
        self.manager = manager or EmbateManager()

    async def condensar(self, embates: list[Embate]) -> list[Embate]:
        """Condensa embates similares.

        Parameters
        ----------
        embates : list[Embate]
            Lista de embates a condensar.

        Returns
        -------
        list[Embate]
            Lista de embates condensada.

        """
        if not embates:
            return []

        # Agrupa por tipo
        por_tipo: dict[str, list[Embate]] = {}
        for e in embates:
            if e.tipo not in por_tipo:
                por_tipo[e.tipo] = []
            por_tipo[e.tipo].append(e)

        # Condensa cada grupo
        condensados = []
        for tipo, grupo in por_tipo.items():
            condensados.extend(self._condensar_grupo(grupo))

        return condensados

    def _condensar_grupo(self, grupo: list[Embate]) -> list[Embate]:
        """Condensa um grupo de embates do mesmo tipo.

        Parameters
        ----------
        grupo : list[Embate]
            Grupo de embates do mesmo tipo.

        Returns
        -------
        list[Embate]
            Lista de embates condensada.

        """
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
        """Calcula similaridade entre dois embates.

        Parameters
        ----------
        e1 : Embate
            Primeiro embate.
        e2 : Embate
            Segundo embate.

        Returns
        -------
        float
            Valor de similaridade entre os embates.

        Notes
        -----
        Por enquanto usa apenas o contexto.
        TODO: Usar embeddings ou outra técnica mais robusta.

        """
        palavras1 = set(e1.contexto.lower().split())
        palavras2 = set(e2.contexto.lower().split())
        intersecao = palavras1.intersection(palavras2)
        return len(intersecao) / max(len(palavras1), len(palavras2))
