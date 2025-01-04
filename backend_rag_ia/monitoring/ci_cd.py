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
<<<<<<< Updated upstream
        """Incrementa contador de ferramentas e verifica limite.

        Returns
        -------
        bool
            True se ainda não atingiu limite, False caso contrário.

=======
        """
        Incrementa contador de ferramentas e verifica limite.

        Returns:
            True se ainda não atingiu limite, False caso contrário
>>>>>>> Stashed changes
        """
        self.tools_count += 1
        return self.tools_count < MAX_TOOLS

class PipelineValidator:
<<<<<<< Updated upstream
    """Valida pipelines de CI/CD.

    Esta classe implementa a validação de pipelines de CI/CD,
    verificando regras de duração, etapas obrigatórias e métricas.

    """
=======
    """Valida pipelines de CI/CD."""
>>>>>>> Stashed changes

    def __init__(self):
        """Inicializa o validador com regras padrão."""
        self.regras = {
            "max_duracao": 3600,  # 1 hora
            "etapas_obrigatorias": ["build", "test"],
            "status_validos": ["em_andamento", "sucesso", "falha"]
        }

    def validar_pipeline(self, pipeline: Pipeline) -> list[str]:
<<<<<<< Updated upstream
        """Valida um pipeline.

        Parameters
        ----------
        pipeline : Pipeline
            Pipeline para validar.

        Returns
        -------
        list[str]
            Lista de erros encontrados.

=======
        """
        Valida um pipeline.

        Args:
            pipeline: Pipeline para validar

        Returns:
            Lista de erros encontrados
>>>>>>> Stashed changes
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
<<<<<<< Updated upstream
        """Valida métricas de um pipeline.

        Parameters
        ----------
        pipeline : Pipeline
            Pipeline para validar.

        Returns
        -------
        list[str]
            Lista de avisos sobre métricas.

=======
        """
        Valida métricas de um pipeline.

        Args:
            pipeline: Pipeline para validar

        Returns:
            Lista de avisos sobre métricas
>>>>>>> Stashed changes
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
<<<<<<< Updated upstream
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

=======
    """Resolve dependências entre pipelines."""

    def __init__(self):
        self.dependencias: dict[str, list[str]] = {}

    def adicionar_dependencia(self, pipeline: str, depende_de: str) -> None:
        """
        Adiciona uma dependência.

        Args:
            pipeline: Pipeline dependente
            depende_de: Pipeline que é dependência
>>>>>>> Stashed changes
        """
        if pipeline not in self.dependencias:
            self.dependencias[pipeline] = []
        self.dependencias[pipeline].append(depende_de)

    def get_dependencias(self, pipeline: str) -> list[str]:
<<<<<<< Updated upstream
        """Retorna dependências de um pipeline.

        Parameters
        ----------
        pipeline : str
            Pipeline para verificar.

        Returns
        -------
        list[str]
            Lista de dependências.

=======
        """
        Retorna dependências de um pipeline.

        Args:
            pipeline: Pipeline para verificar

        Returns:
            Lista de dependências
>>>>>>> Stashed changes
        """
        return self.dependencias.get(pipeline, [])

    def verificar_ciclos(self) -> bool:
<<<<<<< Updated upstream
        """Verifica se há ciclos nas dependências.

        Returns
        -------
        bool
            True se houver ciclos.

=======
        """
        Verifica se há ciclos nas dependências.

        Returns:
            True se houver ciclos
>>>>>>> Stashed changes
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
<<<<<<< Updated upstream
    """Monitora pipelines de CI/CD.

    Esta classe implementa o monitoramento de pipelines de CI/CD,
    gerenciando seu ciclo de vida e coletando métricas.

    """

    def __init__(self):
        """Inicializa o monitor de CI/CD."""
=======
    """Monitor de pipelines de CI/CD."""

    def __init__(self):
>>>>>>> Stashed changes
        self.pipelines: list[Pipeline] = []
        self.resolver = DependencyResolver()
        self.validator = PipelineValidator()

    def iniciar_pipeline(self, nome: str, depende_de: Optional[list[str]] = None) -> Pipeline:
<<<<<<< Updated upstream
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

=======
        """
        Inicia um novo pipeline.

        Args:
            nome: Nome do pipeline
            depende_de: Lista de dependências

        Returns:
            Pipeline criado
>>>>>>> Stashed changes
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
<<<<<<< Updated upstream
        """Finaliza um pipeline.

        Parameters
        ----------
        pipeline : Pipeline
            Pipeline a finalizar.
        sucesso : bool, optional
            Se foi bem sucedido, por padrão True.

=======
        """
        Finaliza um pipeline.

        Args:
            pipeline: Pipeline a finalizar
            sucesso: Se foi bem sucedido
>>>>>>> Stashed changes
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
<<<<<<< Updated upstream
        """Adiciona uma métrica ao pipeline.

        Parameters
        ----------
        pipeline : Pipeline
            Pipeline alvo.
        nome : str
            Nome da métrica.
        valor : float
            Valor da métrica.

=======
        """
        Adiciona uma métrica ao pipeline.

        Args:
            pipeline: Pipeline alvo
            nome: Nome da métrica
            valor: Valor da métrica
>>>>>>> Stashed changes
        """
        pipeline.metricas[nome] = valor

    def get_metricas(self) -> dict:
<<<<<<< Updated upstream
        """Retorna métricas agregadas dos pipelines.

        Returns
        -------
        dict
            Métricas calculadas.

=======
        """
        Retorna métricas agregadas dos pipelines.

        Returns:
            Métricas calculadas
>>>>>>> Stashed changes
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
