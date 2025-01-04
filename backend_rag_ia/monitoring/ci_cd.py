"""Implementa monitoramento de CI/CD.

Este módulo implementa o monitoramento e validação de pipelines de CI/CD,
incluindo resolução de dependências e métricas de performance.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel

# Constantes
MAX_TOOLS = 15  # Limite máximo de ferramentas

class Pipeline(BaseModel):
    """Define um pipeline de CI/CD.

    Representa um pipeline de CI/CD com suas propriedades e métricas.

    Attributes
    ----------
    nome : str
        Nome do pipeline.
    status : str
        Status atual do pipeline.
    inicio : datetime
        Data e hora de início.
    fim : Optional[datetime]
        Data e hora de finalização.
    etapas : list[str]
        Lista de etapas do pipeline.
    metricas : dict
        Métricas coletadas durante a execução.
    tools_count : int
        Contador de ferramentas utilizadas.

    """

    nome: str
    status: str
    inicio: datetime
    fim: Optional[datetime] = None
    etapas: list[str] = []
    metricas: dict = {}
    tools_count: int = 0

    def incrementar_tools(self) -> bool:
        """Incrementa contador de ferramentas e verifica limite.

        Returns
        -------
        bool
            True se ainda não atingiu limite, False caso contrário.

        """
        self.tools_count += 1
        return self.tools_count < MAX_TOOLS

class PipelineValidator:
    """Valida pipelines de CI/CD.

    Esta classe implementa a validação de pipelines de CI/CD,
    verificando regras de duração, etapas obrigatórias e métricas.

    """

    def __init__(self):
        """Inicializa o validador com regras padrão."""
        self.regras = {
            "max_duracao": 3600,  # 1 hora
            "etapas_obrigatorias": ["build", "test"],
            "status_validos": ["em_andamento", "sucesso", "falha"]
        }

    def validar_pipeline(self, pipeline: Pipeline) -> list[str]:
        """Valida um pipeline.

        Parameters
        ----------
        pipeline : Pipeline
            Pipeline para validar.

        Returns
        -------
        list[str]
            Lista de erros encontrados.

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
        """Valida métricas de um pipeline.

        Parameters
        ----------
        pipeline : Pipeline
            Pipeline para validar.

        Returns
        -------
        list[str]
            Lista de avisos sobre métricas.

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
    """Resolve dependências entre pipelines.

    Esta classe gerencia as dependências entre diferentes pipelines,
    permitindo adicionar, consultar e verificar ciclos nas dependências.

    """

    def __init__(self):
        """Inicializa o resolvedor de dependências."""
        self.dependencias: dict[str, list[str]] = {}

    def adicionar_dependencia(self, pipeline: str, depende_de: str) -> None:
        """Adiciona uma dependência.

        Parameters
        ----------
        pipeline : str
            Pipeline dependente.
        depende_de : str
            Pipeline que é dependência.

        """
        if pipeline not in self.dependencias:
            self.dependencias[pipeline] = []
        self.dependencias[pipeline].append(depende_de)

    def get_dependencias(self, pipeline: str) -> list[str]:
        """Retorna dependências de um pipeline.

        Parameters
        ----------
        pipeline : str
            Pipeline para verificar.

        Returns
        -------
        list[str]
            Lista de dependências.

        """
        return self.dependencias.get(pipeline, [])

    def verificar_ciclos(self) -> bool:
        """Verifica se há ciclos nas dependências.

        Returns
        -------
        bool
            True se houver ciclos.

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
    """Monitora pipelines de CI/CD.

    Esta classe implementa o monitoramento de pipelines de CI/CD,
    gerenciando seu ciclo de vida e coletando métricas.

    """

    def __init__(self):
        """Inicializa o monitor de CI/CD."""
        self.pipelines: list[Pipeline] = []
        self.resolver = DependencyResolver()
        self.validator = PipelineValidator()

    def iniciar_pipeline(self, nome: str, depende_de: Optional[list[str]] = None) -> Pipeline:
        """Inicia um novo pipeline.

        Parameters
        ----------
        nome : str
            Nome do pipeline.
        depende_de : Optional[list[str]], optional
            Lista de dependências, por padrão None.

        Returns
        -------
        Pipeline
            Pipeline criado.

        Raises
        ------
        ValueError
            Se o limite de ferramentas for atingido.

        """
        pipeline = Pipeline(
            nome=nome,
            status="em_andamento",
            inicio=datetime.now()
        )

        # Verifica limite de ferramentas
        if not pipeline.incrementar_tools():
            raise ValueError(f"Limite de {MAX_TOOLS} ferramentas atingido")

        if depende_de:
            for dep in depende_de:
                self.resolver.adicionar_dependencia(nome, dep)

        self.pipelines.append(pipeline)
        return pipeline

    def finalizar_pipeline(self, pipeline: Pipeline, sucesso: bool = True) -> None:
        """Finaliza um pipeline.

        Parameters
        ----------
        pipeline : Pipeline
            Pipeline a finalizar.
        sucesso : bool, optional
            Se foi bem sucedido, por padrão True.

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
        """Adiciona uma métrica ao pipeline.

        Parameters
        ----------
        pipeline : Pipeline
            Pipeline alvo.
        nome : str
            Nome da métrica.
        valor : float
            Valor da métrica.

        """
        pipeline.metricas[nome] = valor

    def get_metricas(self) -> dict:
        """Retorna métricas agregadas dos pipelines.

        Returns
        -------
        dict
            Métricas calculadas.

        """
        metricas = {
            "total": len(self.pipelines),
            "sucesso": len([p for p in self.pipelines if p.status == "sucesso"]),
            "falha": len([p for p in self.pipelines if p.status == "falha"]),
            "tempo_medio": 0.0
        }

        tempos = []
        for p in self.pipelines:
            if p.fim:
                tempo = (p.fim - p.inicio).total_seconds()
                tempos.append(tempo)

        if tempos:
            metricas["tempo_medio"] = sum(tempos) / len(tempos)

        return metricas
