<<<<<<< Updated upstream
"""Módulo para gerenciamento de embates.

Este módulo contém classes e funções para gerenciar embates,
incluindo análise de impacto e execução de mudanças.

"""

from datetime import datetime

from .models import Embate
=======
"""Gerenciador de embates.

Este módulo fornece classes para gerenciar embates, incluindo
resolução de conflitos e detecção de alucinações.
"""

from datetime import datetime
from typing import Any, Optional

from core.refactoring_limits_checker import RefactoringLimitsChecker

from .models import Embate
from .storage import SupabaseStorage


class ConflictResolver:
    """Resolve conflitos entre embates.

    Esta classe fornece métodos para detectar e resolver conflitos
    entre diferentes embates no sistema.

    Attributes
    ----------
    conflitos : list[dict]
        Lista de conflitos detectados.

    """

    def __init__(self):
        """Inicializa o resolvedor de conflitos."""
        self.conflitos: list[dict] = []

    def detectar_conflito(self, embate1: Embate, embate2: Embate) -> bool:
        """Detecta conflito entre dois embates.

        Parameters
        ----------
        embate1 : Embate
            Primeiro embate a ser comparado.
        embate2 : Embate
            Segundo embate a ser comparado.

        Returns
        -------
        bool
            True se houver conflito, False caso contrário.

        """
        # Mesmo tipo e contexto similar
        if embate1.tipo == embate2.tipo:
            return self._contexto_similar(embate1.contexto, embate2.contexto)
        return False

    def registrar_conflito(self, embate1: Embate, embate2: Embate) -> None:
        """Registra um conflito entre embates.

        Parameters
        ----------
        embate1 : Embate
            Primeiro embate envolvido no conflito.
        embate2 : Embate
            Segundo embate envolvido no conflito.

        """
        self.conflitos.append({
            "embate1": embate1.id,
            "embate2": embate2.id,
            "timestamp": datetime.now(),
            "resolvido": False
        })

    def resolver_conflito(self, embate1: Embate, embate2: Embate) -> Embate:
        """Resolve um conflito entre embates.

        Parameters
        ----------
        embate1 : Embate
            Primeiro embate a ser resolvido.
        embate2 : Embate
            Segundo embate a ser resolvido.

        Returns
        -------
        Embate
            Embate escolhido como resolução do conflito.

        """
        # Por padrão, mantém o mais recente
        if embate1.criado_em > embate2.criado_em:
            return embate1
        return embate2

    def _contexto_similar(self, ctx1: str, ctx2: str) -> bool:
        """Verifica se dois contextos são similares.

        Parameters
        ----------
        ctx1 : str
            Primeiro contexto a ser comparado.
        ctx2 : str
            Segundo contexto a ser comparado.

        Returns
        -------
        bool
            True se os contextos forem similares, False caso contrário.

        """
        # Implementação simples por enquanto
        palavras1 = set(ctx1.lower().split())
        palavras2 = set(ctx2.lower().split())
        intersecao = palavras1.intersection(palavras2)
        return len(intersecao) / max(len(palavras1), len(palavras2)) > 0.7


class EmbateManager:
    """Gerencia embates.

    Esta classe fornece métodos para gerenciar o ciclo de vida
    completo dos embates, incluindo criação, busca e atualização.

    Attributes
    ----------
    storage : Optional[SupabaseStorage]
        Storage para persistência dos embates.
    resolver : ConflictResolver
        Resolvedor de conflitos entre embates.

    """

    def __init__(self, storage: Optional[SupabaseStorage] = None):
        """Inicializa o gerenciador.

        Parameters
        ----------
        storage : Optional[SupabaseStorage], optional
            Storage opcional para persistência, por padrão None.

        """
        self.storage = storage
        self.resolver = ConflictResolver()

    async def create_embate(self, embate: Embate) -> dict:
        """Cria um novo embate.

        Parameters
        ----------
        embate : Embate
            Embate a ser criado.

        Returns
        -------
        dict
            Dados do embate criado com status.

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
        """Busca um embate por ID.

        Parameters
        ----------
        id : str
            ID do embate.

        Returns
        -------
        Optional[Embate]
            Embate encontrado ou None se não encontrado.

        """
        if self.storage:
            return await self.storage.get(id)
        return None

    async def list_embates(self) -> list[Embate]:
        """Lista todos os embates.

        Returns
        -------
        list[Embate]
            Lista de embates.

        """
        if self.storage:
            return await self.storage.list()
        return []

    async def search_embates(self, query: str) -> list[Embate]:
        """Busca embates por texto.

        Parameters
        ----------
        query : str
            Texto para buscar.

        Returns
        -------
        list[Embate]
            Lista de embates encontrados.

        """
        embates = await self.list_embates()
        query = query.lower()

        return [
            e for e in embates
            if query in e.titulo.lower() or
               query in e.contexto.lower() or
               any(query in arg.conteudo.lower() for arg in e.argumentos)
        ]

    async def update_embate(self, id: str, updates: dict) -> dict:
        """Atualiza um embate.

        Parameters
        ----------
        id : str
            ID do embate.
        updates : dict
            Campos para atualizar.

        Returns
        -------
        dict
            Status da atualização.

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
        """Exporta embates com filtros.

        Parameters
        ----------
        filters : dict, optional
            Filtros a aplicar, por padrão None.

        Returns
        -------
        list[dict]
            Lista de embates exportados.

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

    async def detect_hallucination(self, embate: Embate) -> dict[str, Any]:
        """Detecta possíveis alucinações em um embate.

        Parameters
        ----------
        embate : Embate
            Embate a ser analisado.

        Returns
        -------
        dict[str, Any]
            Dicionário com resultado da análise.

        """
        hallucination_indicators = {
            "inconsistencias": [],
            "duplicidades": [],
            "score": 0.0,
            "loop_indicators": []
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
                hallucination_indicators["inconsistencias"].append(
                    "Contexto muito curto/vago"
                )
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
                "is_hallucination": hallucination_indicators["score"] > 0.7
            }

        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }

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
            argumentos=[]
        )

        # Argumento a favor dos Logs
        embate.argumentos.append({
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
            "data": now
        })

        # Argumento a favor do JSONB
        embate.argumentos.append({
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
            "data": now
        })

        # Argumento a favor do Gemini
        embate.argumentos.append({
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
            "data": now
        })

        # Contra-argumento final
        embate.argumentos.append({
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
            "data": now
        })

        return await self.create_embate(embate)
>>>>>>> Stashed changes

class RefactoringManager:
    """Gerencia operações de refatoração.

    Esta classe é responsável por gerenciar operações de refatoração
    no código, incluindo análise de impacto e execução de mudanças.

    """

    def __init__(self):
<<<<<<< Updated upstream
        """Inicializa o gerenciador de refatoração."""
        self.changes: list[dict] = []

    async def analyze_impact(self, embate: Embate) -> dict:
        """Analisa o impacto de uma refatoração.

        Parameters
        ----------
        embate : Embate
            O embate que contém a proposta de refatoração.

        Returns
        -------
        dict
            Dicionário com a análise de impacto.

        """
        impact = {
            "files_affected": [],
            "complexity_change": 0,
            "risk_level": "low"
        }

        # Analisa argumentos do embate
        for arg in embate.argumentos:
            if "arquivo" in arg.metadata:
                impact["files_affected"].append(arg.metadata["arquivo"])

        # Calcula risco baseado em quantidade de arquivos
        if len(impact["files_affected"]) > 5:
            impact["risk_level"] = "high"
        elif len(impact["files_affected"]) > 2:
            impact["risk_level"] = "medium"

        return impact

    async def execute_refactoring(self, embate: Embate) -> dict:
        """Executa uma refatoração.

        Parameters
        ----------
        embate : Embate
            O embate que contém a proposta de refatoração.

        Returns
        -------
        dict
            Dicionário com o resultado da execução.

        """
        result = {
            "success": True,
            "changes_made": [],
            "errors": []
        }

        try:
            # Executa a refatoração
            for arg in embate.argumentos:
                if "arquivo" in arg.metadata:
                    result["changes_made"].append({
                        "file": arg.metadata["arquivo"],
                        "type": "modify",
                        "timestamp": datetime.now().isoformat()
                    })
        except Exception as e:
            result["success"] = False
            result["errors"].append(str(e))

        return result
=======
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
            "cohesion": self.calculate_cohesion()
        }

        result = self.limits_checker.should_continue_refactoring(metrics)

        if not result["continue"]:
            return {
                "status": "stop",
                "reason": result["reason"],
                "recommendations": self.limits_checker.get_recommendations()
            }

        return {
            "status": "continue",
            "recommendations": self.limits_checker.get_recommendations()
        }
>>>>>>> Stashed changes
