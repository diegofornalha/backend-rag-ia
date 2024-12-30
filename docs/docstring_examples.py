"""Módulo de exemplo para demonstrar o estilo de documentação.

Este módulo contém exemplos de documentação seguindo o estilo Google
e as regras definidas no .pydocstyle e .flake8.
"""


import numpy as np


class ModeloExemplo:
    """Classe de exemplo para demonstrar documentação de classes.

    Esta classe serve como exemplo de como documentar classes seguindo
    o estilo Google e as regras definidas.

    Attributes:
        nome: Nome do modelo.
        parametros: Dicionário com os parâmetros do modelo.
        treinado: Indica se o modelo já foi treinado.
    """

    def __init__(self, nome: str, parametros: dict | None = None):
        """Inicializa o ModeloExemplo.

        Args:
            nome: Nome do modelo.
            parametros: Dicionário opcional com os parâmetros do modelo.
                Se não fornecido, usa parâmetros padrão.
        """
        self.nome = nome
        self.parametros = parametros or {}
        self.treinado = False

    def treinar(
        self, dados: np.ndarray, labels: np.ndarray, epochs: int = 10
    ) -> dict[str, float]:
        """Treina o modelo com os dados fornecidos.

        Args:
            dados: Array numpy com os dados de treinamento.
            labels: Array numpy com os rótulos dos dados.
            epochs: Número de épocas de treinamento.

        Returns:
            Dicionário com métricas do treinamento (loss, accuracy).

        Raises:
            ValueError: Se os dados e labels tiverem tamanhos diferentes.
        """
        if dados.shape[0] != labels.shape[0]:
            raise ValueError("Dados e labels devem ter o mesmo número de amostras")

        # Exemplo de list comprehension (seguindo regras do flake8-comprehensions)
        metricas = [self._treinar_epoca(dados, labels) for _ in range(epochs)]

        self.treinado = True
        return {
            "loss": float(np.mean([m["loss"] for m in metricas])),
            "accuracy": float(np.mean([m["accuracy"] for m in metricas])),
        }

    def _treinar_epoca(self, dados: np.ndarray, labels: np.ndarray) -> dict[str, float]:
        """Treina o modelo por uma época.

        Args:
            dados: Array numpy com os dados de treinamento.
            labels: Array numpy com os rótulos dos dados.

        Returns:
            Dicionário com métricas da época (loss, accuracy).
        """
        # Simulação de treinamento
        return {"loss": 0.1, "accuracy": 0.95}

    def predizer(self, dados: np.ndarray) -> np.ndarray:
        """Faz predições com o modelo treinado.

        Args:
            dados: Array numpy com os dados para predição.

        Returns:
            Array numpy com as predições.

        Raises:
            RuntimeError: Se o modelo não foi treinado ainda.
        """
        if not self.treinado:
            raise RuntimeError("Modelo precisa ser treinado antes de fazer predições")

        # Exemplo de list comprehension (seguindo regras do flake8-comprehensions)
        return np.array([self._predizer_amostra(x) for x in dados])

    def _predizer_amostra(self, amostra: np.ndarray) -> float:
        """Faz predição para uma única amostra.

        Args:
            amostra: Array numpy com uma única amostra.

        Returns:
            Valor predito para a amostra.
        """
        # Simulação de predição
        return float(np.mean(amostra))


def processar_dados(
    dados: list | np.ndarray, normalizar: bool = True
) -> np.ndarray:
    """Processa os dados de entrada.

    Args:
        dados: Lista ou array numpy com os dados a serem processados.
        normalizar: Se True, normaliza os dados para média 0 e desvio padrão 1.

    Returns:
        Array numpy com os dados processados.

    Examples:
        >>> dados = [1, 2, 3, 4, 5]
        >>> dados_proc = processar_dados(dados, normalizar=True)
        >>> print(dados_proc.mean())
        0.0
    """
    # Converte para numpy array se necessário
    dados_array = np.array(dados)

    if normalizar:
        return (dados_array - dados_array.mean()) / dados_array.std()

    return dados_array
