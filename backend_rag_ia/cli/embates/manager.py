"""
Gerenciador de embates.
"""

import json
from datetime import datetime
from typing import Any, Dict, List, Optional

from ...1_core.refactoring_limits_checker import RefactoringLimitsChecker

from .models import Embate
from .storage import SupabaseStorage


class ConflictResolver:
    """Resolve conflitos entre embates."""

    def __init__(self):
        self.conflitos: list[dict] = []

    def detectar_conflito(self, embate1: Embate, embate2: Embate) -> bool:
        """Detecta conflito entre dois embates."""
        # Mesmo tipo e contexto similar
        if embate1.tipo == embate2.tipo:
            return self._contexto_similar(embate1.contexto, embate2.contexto)
        return False

    def registrar_conflito(self, embate1: Embate, embate2: Embate) -> None:
        """Registra um conflito."""
        self.conflitos.append(
            {
                "embate1": embate1.id,
                "embate2": embate2.id,
                "timestamp": datetime.now(),
                "resolvido": False,
            }
        )

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

    def __init__(self, storage: SupabaseStorage | None = None):
        """
        Inicializa o gerenciador.

        Args:
            storage: Storage opcional para persistência
        """
        self.storage = storage
        self.resolver = ConflictResolver()

    async def create_embate(self, embate: Embate) -> dict:
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

            return {"status": "success", "id": "local-" + datetime.now().isoformat()}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    async def get_embate(self, id: str) -> Embate | None:
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

    async def list_embates(self) -> list[Embate]:
        """
        Lista todos os embates.

        Returns:
            Lista de embates
        """
        if self.storage:
            return await self.storage.list()
        return []

    async def search_embates(self, query: str) -> list[Embate]:
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
            e
            for e in embates
            if query in e.titulo.lower()
            or query in e.contexto.lower()
            or any(query in arg.conteudo.lower() for arg in e.argumentos)
        ]

    async def update_embate(self, id: str, updates: dict) -> dict:
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

    async def export_embates(self, filters: dict = None) -> list[dict]:
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
                embates = [e for e in embates if hasattr(e, key) and getattr(e, key) == value]

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
                        "data": a.data.isoformat(),
                    }
                    for a in e.argumentos
                ],
                "decisao": e.decisao,
                "razao": e.razao,
            }
            for e in embates
        ]

    async def detect_hallucination(self, embate: Embate) -> dict[str, Any]:
        """
        Detecta possíveis alucinações em um embate.

        Args:
            embate: Embate a ser analisado

        Returns:
            Dicionário com resultado da análise
        """
        hallucination_indicators = {
            "inconsistencias": [],
            "duplicidades": [],
            "score": 0.0,
            "loop_indicators": [],
        }

        try:
            # Verifica inconsistências internas
            if embate.status == "resolvido" and not embate.data_resolucao:
                hallucination_indicators["inconsistencias"].append(
                    "Status resolvido sem data de resolução"
                )
                hallucination_indicators["score"] += 0.3

            if embate.data_resolucao and embate.data_resolucao < embate.data_inicio:
                hallucination_indicators["inconsistencias"].append(
                    "Data de resolução anterior à data de início"
                )
                hallucination_indicators["score"] += 0.5

            # Verifica argumentos
            argumentos_unicos = set()
            for arg in embate.argumentos:
                # Verifica duplicidade de conteúdo
                if arg.conteudo in argumentos_unicos:
                    hallucination_indicators["duplicidades"].append(
                        f"Argumento duplicado: {arg.conteudo[:100]}..."
                    )
                    hallucination_indicators["score"] += 0.2
                argumentos_unicos.add(arg.conteudo)

                # Verifica datas dos argumentos
                if arg.data < embate.data_inicio:
                    hallucination_indicators["inconsistencias"].append(
                        "Argumento com data anterior ao início do embate"
                    )
                    hallucination_indicators["score"] += 0.3

            # Verifica contexto vs título
            if len(embate.contexto.split()) < 10:
                hallucination_indicators["inconsistencias"].append("Contexto muito curto/vago")
                hallucination_indicators["score"] += 0.2

            # Verifica metadados
            if "is_trigger_embate" in embate.metadata:
                hallucination_indicators["score"] += 0.1

            # Busca embates similares
            if self.storage:
                embates = await self.storage.list()
                for e in embates:
                    if e != embate and self.resolver._contexto_similar(e.contexto, embate.contexto):
                        hallucination_indicators["duplicidades"].append(
                            f"Embate similar existente: {e.titulo}"
                        )
                        hallucination_indicators["score"] += 0.4

            # Verificar embates relacionados não implementados
            related_embates = await self.find_related_embates(embate.titulo)
            pending_implementations = [e for e in related_embates if not e.implementado]

            if len(pending_implementations) > 2:
                hallucination_indicators["loop_indicators"].append(
                    "Múltiplos embates relacionados pendentes de implementação"
                )
                hallucination_indicators["score"] += 0.4

            return {
                "status": "success",
                "indicators": hallucination_indicators,
                "is_hallucination": hallucination_indicators["score"] > 0.7,
            }

        except Exception as e:
            return {"status": "error", "message": str(e)}

    async def create_implementation_embate(self) -> dict:
        """
        Cria um embate para decidir qual implementação priorizar.

        Returns:
            Status da criação do embate
        """
        now = datetime.now()

        embate = Embate(
            titulo="Qual implementação devemos priorizar?",
            tipo="tecnico",
            contexto="""
            Temos três implementações técnicas importantes pendentes:
            1. Padronização de Logs
            2. Migração para JSONB
            3. Integração com Gemini
            
            Precisamos decidir qual delas implementar primeiro, considerando
            o impacto prático no sistema e a viabilidade técnica.
            """,
            status="aberto",
            data_inicio=now,
            metadata={"is_implementation_decision": True},
            argumentos=[],
        )

        # Argumento a favor dos Logs
        embate.argumentos.append(
            {
                "autor": "Sistema",
                "tipo": "tecnico",
                "conteudo": """
            Defendo começar pela Padronização de Logs porque:
            
            1. É a base para debugar e monitorar as outras mudanças
            2. Não depende de nenhuma outra implementação
            3. Usa apenas a biblioteca padrão do Python
            4. Pode ser feito gradualmente, módulo por módulo
            
            Se algo der errado nas outras implementações (JSONB ou Gemini),
            ter logs bem estruturados será essencial para identificar e
            resolver problemas rapidamente.
            """,
                "data": now,
            }
        )

        # Argumento a favor do JSONB
        embate.argumentos.append(
            {
                "autor": "Sistema",
                "tipo": "tecnico",
                "conteudo": """
            Discordo. Deveríamos priorizar a Migração JSONB porque:
            
            1. O impacto na performance será imediato e significativo
            2. Queries mais eficientes beneficiam todo o sistema
            3. Quanto mais dados tivermos, mais complexa será a migração
            4. Podemos usar logs básicos durante a migração
            
            Logs estruturados são importantes, mas o ganho de performance
            do JSONB terá impacto maior no sistema como um todo.
            """,
                "data": now,
            }
        )

        # Argumento a favor do Gemini
        embate.argumentos.append(
            {
                "autor": "Sistema",
                "tipo": "tecnico",
                "conteudo": """
            Proponho começar pela Integração Gemini porque:
            
            1. Melhora imediata na qualidade dos embates
            2. Reduz trabalho manual de análise
            3. API já existe, é só integrar
            4. Podemos usar logs simples no início
            
            A análise automática nos ajudaria inclusive a avaliar melhor
            as outras implementações e seus impactos.
            """,
                "data": now,
            }
        )

        # Contra-argumento final
        embate.argumentos.append(
            {
                "autor": "Sistema",
                "tipo": "tecnico",
                "conteudo": """
            Após analisar todos os argumentos, mantenho que Logs devem ser primeiro:
            
            1. É a mudança mais segura e controlada
            2. Cria base sólida para as outras implementações
            3. Facilita debug e rollback se necessário
            4. Pode ser feito sem afetar performance
            
            Tanto JSONB quanto Gemini são importantes, mas ter visibilidade
            do sistema é crucial antes de fazer mudanças mais impactantes.
            """,
                "data": now,
            }
        )

        return await self.create_embate(embate)


class RefactoringManager:
    def __init__(self):
        self.limits_checker = RefactoringLimitsChecker()

    async def analyze_directory(self, directory: str) -> dict[str, Any]:
        """Analisa um diretório e retorna recomendações"""

        metrics = {
            "iterations": self.current_iteration,
            "total_changes": len(self.changes),
            "removed": len(self.removed_items),
            "simplified": len(self.simplified_items),
            "consolidated": len(self.consolidated_items),
            "updated": len(self.updated_items),
            "complexity": self.calculate_complexity(),
            "cohesion": self.calculate_cohesion(),
        }

        result = self.limits_checker.should_continue_refactoring(metrics)

        if not result["continue"]:
            return {
                "status": "stop",
                "reason": result["reason"],
                "recommendations": self.limits_checker.get_recommendations(),
            }

        return {"status": "continue", "recommendations": self.limits_checker.get_recommendations()}
