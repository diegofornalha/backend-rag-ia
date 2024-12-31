# Exemplos de Docstrings

> Este documento demonstra o estilo de documentação usando docstrings
> seguindo o estilo Google e as regras do Ruff.

## 1. Documentação de Módulo

```python
"""Módulo de exemplo para demonstrar o estilo de documentação.

Este módulo contém exemplos de documentação seguindo o estilo Google
e as regras definidas pelo Ruff.
"""
```

## 2. Documentação de Classe

```python
class ModeloExemplo:
    """Classe de exemplo para demonstrar documentação de classes.

    Esta classe serve como exemplo de como documentar classes seguindo
    o estilo Google e as regras definidas.

    Attributes:
        nome: Nome do modelo.
        parametros: Dicionário com os parâmetros do modelo.
        treinado: Indica se o modelo já foi treinado.
    """
```

## 3. Documentação de Método

```python
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
```

## 4. Documentação de Função

```python
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
```

## 5. Boas Práticas

1. **Type Hints**:

   - Usar em todos os parâmetros
   - Usar em todos os retornos
   - Usar tipos do typing quando necessário

2. **Docstrings**:

   - Primeira linha é resumo
   - Linha em branco após resumo
   - Seções organizadas (Args, Returns, Raises, etc)

3. **Exemplos**:
   - Incluir quando relevante
   - Usar doctest quando possível
   - Manter exemplos simples e claros
