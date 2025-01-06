"""
Métricas do sistema.
"""

import time
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Dict, List, Optional

# Constantes
MAX_TOOLS = 3  # Limite máximo de ferramentas


def testar_limite_ferramentas():
    """Função para testar o limite de ferramentas."""
    print("\nTestando limite de ferramentas:")
    print("--------------------------------")

    metrica = Metrica(nome="teste", valor=1.0, timestamp=datetime.now())

    # Testa incrementos até passar do limite
    for i in range(MAX_TOOLS + 1):
        resultado = metrica.incrementar_tools()
        print(f"Ferramenta {i+1}: {'✅ Permitido' if resultado else '❌ Bloqueado'}")

    print(f"\nTotal de ferramentas usadas: {metrica.tools_count}")


@dataclass
class Metrica:
    """Modelo para métricas."""

    nome: str
    valor: float
    timestamp: datetime
    tags: dict[str, str] = None
    tools_count: int = 0
    modo_contencao: bool = False
    embate_ativo: bool = True
    tema_atual: str | None = None

    def incrementar_tools(self) -> bool:
        """
        Incrementa contador de ferramentas e verifica limite.

        Returns:
            True se ainda não atingiu limite, False caso contrário
        """
        if not self.embate_ativo:
            return False

        self.tools_count += 1
        hora_atual = datetime.now().strftime("%H:%M:%S")

        if self.tools_count >= MAX_TOOLS:
            if not self.modo_contencao:
                print(f"\n🛑 AVISO: Embate em ação! [{hora_atual}]")
                if not self.tema_atual:
                    self.tema_atual = self.nome
                print(f"Tema do embate: {self.tema_atual}")
                print(f"CLI interrompido após {self.tools_count} ferramentas.")
                print("Sistema entrando em modo de contenção...")
                self.modo_contencao = True
                return False
            else:
                print(f"\n⏸️  Sistema em contenção [{hora_atual}]")
                print("Aguardando 2 segundos...")
                time.sleep(2)
                print(
                    f"\n🔄 Reativando embate sobre '{self.tema_atual}'... [{datetime.now().strftime('%H:%M:%S')}]"
                )
                print("Sistema retomando fluxo de embates.")
                print("\n> Digite 'continue' para prosseguir ou 'stop' para interromper")
                comando = "continue"  # Simulando input do usuário
                print(comando)

                if comando.lower() == "stop":
                    print("\n🛑 Embate interrompido manualmente pelo usuário.")
                    self.embate_ativo = False
                    return False

                print(f"\n✨ Embate sobre '{self.tema_atual}' continuando...")
                self.modo_contencao = False
                # Reseta o contador mas mantém o embate ativo
                self.tools_count = 0
                return True
        return True

    def interromper_embate(self) -> None:
        """Interrompe manualmente o embate atual."""
        hora_atual = datetime.now().strftime("%H:%M:%S")
        print(f"\n🛑 Embate sobre '{self.tema_atual}' interrompido manualmente [{hora_atual}]")
        self.embate_ativo = False
        self.modo_contencao = False


@dataclass
class CacheMetric:
    """Métrica de cache."""

    hits: int = 0
    misses: int = 0
    tamanho: int = 0
    ultima_limpeza: datetime | None = None

    @property
    def hit_rate(self) -> float:
        """Taxa de acertos do cache."""
        total = self.hits + self.misses
        return self.hits / total if total > 0 else 0.0


@dataclass
class ResponseTimeMetric:
    """Métrica de tempo de resposta."""

    tempos: list[float] = None

    def __post_init__(self):
        if self.tempos is None:
            self.tempos = []

    async def record_request(self, inicio: datetime, fim: datetime) -> None:
        """Registra tempo de uma requisição."""
        tempo = (fim - inicio).total_seconds() * 1000  # em ms
        self.tempos.append(tempo)

    async def get_stats(self) -> dict:
        """Calcula estatísticas dos tempos."""
        if not self.tempos:
            return {"avg_response_time": 0, "p95_response_time": 0, "p99_response_time": 0}

        tempos_ordenados = sorted(self.tempos)
        n = len(tempos_ordenados)

        return {
            "avg_response_time": sum(self.tempos) / n,
            "p95_response_time": tempos_ordenados[int(n * 0.95)],
            "p99_response_time": tempos_ordenados[int(n * 0.99)],
        }


@dataclass
class SearchAccuracyMetric:
    """Métrica de precisão da busca."""

    relevantes: int = 0
    irrelevantes: int = 0

    async def record_relevant_result(self) -> None:
        """Registra resultado relevante."""
        self.relevantes += 1

    async def record_irrelevant_result(self) -> None:
        """Registra resultado irrelevante."""
        self.irrelevantes += 1

    async def get_stats(self) -> dict:
        """Calcula estatísticas de precisão."""
        total = self.relevantes + self.irrelevantes
        return {
            "accuracy": self.relevantes / total if total > 0 else 0,
            "total_searches": total,
            "relevant_results": self.relevantes,
            "irrelevant_results": self.irrelevantes,
        }


@dataclass
class DependencyMetric:
    """Métrica de dependências."""

    conflicts: int = 0
    outdated: list[str] = None
    incompatible: list[str] = None

    def __post_init__(self):
        if self.outdated is None:
            self.outdated = []
        if self.incompatible is None:
            self.incompatible = []

    async def check_dependencies(self) -> None:
        """Verifica dependências."""
        # Implementação simplificada por enquanto
        pass

    async def get_stats(self) -> dict:
        """Retorna estatísticas de dependências."""
        return {
            "conflicts": self.conflicts,
            "outdated": self.outdated,
            "incompatible": self.incompatible,
        }


class MetricsCollector:
    """Coletor de métricas do sistema."""

    def __init__(self, janela_retencao: int = 30):
        """
        Inicializa o coletor.

        Args:
            janela_retencao: Dias para manter métricas
        """
        self.janela_retencao = janela_retencao
        self.metricas: list[Metrica] = []
        self.cache_metrics = CacheMetric()
        self.response_time = ResponseTimeMetric()
        self.search_accuracy = SearchAccuracyMetric()
        self.dependency = DependencyMetric()

    def registrar(self, nome: str, valor: float, tags: dict[str, str] = None) -> None:
        """
        Registra uma nova métrica.

        Args:
            nome: Nome da métrica
            valor: Valor da métrica
            tags: Tags opcionais
        """
        metrica = Metrica(nome=nome, valor=valor, timestamp=datetime.now(), tags=tags or {})

        # Verifica limite de ferramentas
        if not metrica.incrementar_tools():
            raise ValueError(f"Limite de {MAX_TOOLS} ferramentas atingido")

        self.metricas.append(metrica)
        self._limpar_antigas()

    def registrar_cache_hit(self) -> None:
        """Registra um acerto no cache."""
        self.cache_metrics.hits += 1

    def registrar_cache_miss(self) -> None:
        """Registra um erro no cache."""
        self.cache_metrics.misses += 1

    def atualizar_tamanho_cache(self, tamanho: int) -> None:
        """
        Atualiza tamanho do cache.

        Args:
            tamanho: Novo tamanho
        """
        self.cache_metrics.tamanho = tamanho

    def registrar_limpeza_cache(self) -> None:
        """Registra limpeza do cache."""
        self.cache_metrics.ultima_limpeza = datetime.now()

    def get_metricas(
        self, nome: str | None = None, tags: dict[str, str] = None
    ) -> list[Metrica]:
        """
        Busca métricas com filtros.

        Args:
            nome: Filtrar por nome
            tags: Filtrar por tags

        Returns:
            Lista de métricas filtradas
        """
        metricas = self.metricas

        if nome:
            metricas = [m for m in metricas if m.nome == nome]

        if tags:
            metricas = [m for m in metricas if all(m.tags.get(k) == v for k, v in tags.items())]

        return metricas

    def get_estatisticas(self, nome: str, periodo: timedelta = None) -> dict:
        """
        Calcula estatísticas de uma métrica.

        Args:
            nome: Nome da métrica
            periodo: Período para análise

        Returns:
            Estatísticas calculadas
        """
        metricas = self.get_metricas(nome)

        if periodo:
            limite = datetime.now() - periodo
            metricas = [m for m in metricas if m.timestamp > limite]

        if not metricas:
            return {"total": 0, "media": 0.0, "min": 0.0, "max": 0.0}

        valores = [m.valor for m in metricas]
        return {
            "total": len(valores),
            "media": sum(valores) / len(valores),
            "min": min(valores),
            "max": max(valores),
        }

    def get_cache_metrics(self) -> dict:
        """
        Retorna métricas do cache.

        Returns:
            Métricas do cache
        """
        return {
            "hits": self.cache_metrics.hits,
            "misses": self.cache_metrics.misses,
            "hit_rate": self.cache_metrics.hit_rate,
            "tamanho": self.cache_metrics.tamanho,
            "ultima_limpeza": self.cache_metrics.ultima_limpeza,
        }

    async def collect_all(self) -> None:
        """Coleta todas as métricas."""
        await self.dependency.check_dependencies()

    async def generate_report(self) -> dict:
        """Gera relatório com todas as métricas."""
        return {
            "response_time": await self.response_time.get_stats(),
            "cache": self.cache_metrics.hit_rate,
            "search": await self.search_accuracy.get_stats(),
            "dependencies": await self.dependency.get_stats(),
        }

    async def check_alerts(self) -> list[str]:
        """Verifica alertas críticos."""
        alertas = []

        # Verifica tempo de resposta
        stats = await self.response_time.get_stats()
        if stats["p99_response_time"] > 1000:  # mais de 1s
            alertas.append("Tempo de resposta crítico")

        # Verifica precisão da busca
        search_stats = await self.search_accuracy.get_stats()
        if search_stats["accuracy"] < 0.8:  # menos de 80%
            alertas.append("Precisão da busca baixa")

        # Verifica dependências
        dep_stats = await self.dependency.get_stats()
        if dep_stats["conflicts"] > 0:
            alertas.append("Conflitos de dependências detectados")

        return alertas

    def _limpar_antigas(self) -> None:
        """Remove métricas antigas."""
        if not self.janela_retencao:
            return

        limite = datetime.now() - timedelta(days=self.janela_retencao)
        self.metricas = [m for m in self.metricas if m.timestamp > limite]
