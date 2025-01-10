"""
Monitoramento de CI/CD.
"""

from datetime import datetime
from typing import Dict, List, Optional

from pydantic import BaseModel

# Constantes
MAX_TOOLS = 15  # Limite máximo de ferramentas


class Pipeline(BaseModel):
    """Modelo para pipeline de CI/CD."""

    nome: str
    status: str
    inicio: datetime
    fim: datetime | None = None
    etapas: list[str] = []
    metricas: dict = {}
    tools_count: int = 0

    def incrementar_tools(self) -> bool:
        """
        Incrementa contador de ferramentas e verifica limite.

        Returns:
            True se ainda não atingiu limite, False caso contrário
        """
        self.tools_count += 1
        return self.tools_count < MAX_TOOLS


class PipelineValidator:
    """Valida pipelines de CI/CD."""

    def __init__(self):
        self.regras = {
            "max_duracao": 3600,  # 1 hora
            "etapas_obrigatorias": ["build", "test"],
            "status_validos": ["em_andamento", "sucesso", "falha"],
        }

    def validar_pipeline(self, pipeline: Pipeline) -> list[str]:
        """
        Valida um pipeline.

        Args:
            pipeline: Pipeline para validar

        Returns:
            Lista de erros encontrados
        """
        erros = []

        # Valida status
        if pipeline.status not in self.regras["status_validos"]:
            erros.append(f"Status inválido: {pipeline.status}")

        # Valida etapas obrigatórias
        for etapa in self.regras["etapas_obrigatorias"]:
            if etapa not in pipeline.etapas:
                erros.append(f"Etapa obrigatória ausente: {etapa}")

        # Valida duração
        if pipeline.fim:
            duracao = (pipeline.fim - pipeline.inicio).total_seconds()
            if duracao > self.regras["max_duracao"]:
                erros.append(
                    f"Duração excede limite: {duracao:.1f}s "
                    f"(max: {self.regras['max_duracao']}s)"
                )

        return erros

    def validar_metricas(self, pipeline: Pipeline) -> list[str]:
        """
        Valida métricas de um pipeline.

        Args:
            pipeline: Pipeline para validar

        Returns:
            Lista de avisos sobre métricas
        """
        avisos = []

        # Verifica cobertura de testes
        if "cobertura" in pipeline.metricas:
            cobertura = pipeline.metricas["cobertura"]
            if cobertura < 80:
                avisos.append(f"Cobertura baixa: {cobertura}%")

        # Verifica tempo de build
        if "tempo_build" in pipeline.metricas:
            tempo = pipeline.metricas["tempo_build"]
            if tempo > 300:  # 5 minutos
                avisos.append(f"Build lento: {tempo:.1f}s")

        return avisos


class DependencyResolver:
    """Resolve dependências entre pipelines."""

    def __init__(self):
        self.dependencias: dict[str, list[str]] = {}

    def adicionar_dependencia(self, pipeline: str, depende_de: str) -> None:
        """
        Adiciona uma dependência.

        Args:
            pipeline: Pipeline dependente
            depende_de: Pipeline que é dependência
        """
        if pipeline not in self.dependencias:
            self.dependencias[pipeline] = []
        self.dependencias[pipeline].append(depende_de)

    def get_dependencias(self, pipeline: str) -> list[str]:
        """
        Retorna dependências de um pipeline.

        Args:
            pipeline: Pipeline para verificar

        Returns:
            Lista de dependências
        """
        return self.dependencias.get(pipeline, [])

    def verificar_ciclos(self) -> bool:
        """
        Verifica se há ciclos nas dependências.

        Returns:
            True se houver ciclos
        """
        visitados = set()
        pilha = set()

        def tem_ciclo(pipeline: str) -> bool:
            if pipeline in pilha:
                return True

            if pipeline in visitados:
                return False

            visitados.add(pipeline)
            pilha.add(pipeline)

            for dep in self.get_dependencias(pipeline):
                if tem_ciclo(dep):
                    return True

            pilha.remove(pipeline)
            return False

        return any(tem_ciclo(p) for p in self.dependencias)


class CICDMonitor:
    """Monitor de pipelines de CI/CD."""

    def __init__(self):
        self.pipelines: list[Pipeline] = []
        self.resolver = DependencyResolver()
        self.validator = PipelineValidator()

    def iniciar_pipeline(self, nome: str, depende_de: list[str] | None = None) -> Pipeline:
        """
        Inicia um novo pipeline.

        Args:
            nome: Nome do pipeline
            depende_de: Lista de dependências

        Returns:
            Pipeline criado
        """
        pipeline = Pipeline(nome=nome, status="em_andamento", inicio=datetime.now())

        # Verifica limite de ferramentas
        if not pipeline.incrementar_tools():
            raise ValueError(f"Limite de {MAX_TOOLS} ferramentas atingido")

        if depende_de:
            for dep in depende_de:
                self.resolver.adicionar_dependencia(nome, dep)

        self.pipelines.append(pipeline)
        return pipeline

    def finalizar_pipeline(self, pipeline: Pipeline, sucesso: bool = True) -> None:
        """
        Finaliza um pipeline.

        Args:
            pipeline: Pipeline a finalizar
            sucesso: Se foi bem sucedido
        """
        pipeline.fim = datetime.now()
        pipeline.status = "sucesso" if sucesso else "falha"

        # Valida pipeline finalizado
        erros = self.validator.validar_pipeline(pipeline)
        if erros:
            pipeline.status = "falha"
            pipeline.metricas["erros_validacao"] = erros

        # Valida métricas
        avisos = self.validator.validar_metricas(pipeline)
        if avisos:
            pipeline.metricas["avisos"] = avisos

    def adicionar_metrica(self, pipeline: Pipeline, nome: str, valor: float) -> None:
        """
        Adiciona uma métrica ao pipeline.

        Args:
            pipeline: Pipeline alvo
            nome: Nome da métrica
            valor: Valor da métrica
        """
        pipeline.metricas[nome] = valor

    def get_metricas(self) -> dict:
        """
        Retorna métricas agregadas dos pipelines.

        Returns:
            Métricas calculadas
        """
        metricas = {
            "total": len(self.pipelines),
            "sucesso": len([p for p in self.pipelines if p.status == "sucesso"]),
            "falha": len([p for p in self.pipelines if p.status == "falha"]),
            "tempo_medio": 0.0,
        }

        tempos = []
        for p in self.pipelines:
            if p.fim:
                tempo = (p.fim - p.inicio).total_seconds()
                tempos.append(tempo)

        if tempos:
            metricas["tempo_medio"] = sum(tempos) / len(tempos)

        return metricas
