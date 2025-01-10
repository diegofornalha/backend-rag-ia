"""
Verificador de complexidade de código.
"""

import ast
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional


@dataclass
class ComplexityMetrics:
    """Métricas de complexidade."""

    linhas: int = 0
    funcoes: int = 0
    classes: int = 0
    imports: int = 0
    complexidade_ciclomatica: int = 0


class ComplexityChecker:
    """Analisa complexidade de código Python."""

    def __init__(self, max_linhas: int = 500, max_complexidade: int = 10):
        self.max_linhas = max_linhas
        self.max_complexidade = max_complexidade

    def analisar_arquivo(self, caminho: Path) -> ComplexityMetrics:
        """
        Analisa um arquivo Python.

        Args:
            caminho: Caminho do arquivo

        Returns:
            Métricas de complexidade
        """
        if not caminho.exists() or not caminho.is_file():
            raise FileNotFoundError(f"Arquivo não encontrado: {caminho}")

        with open(caminho) as f:
            codigo = f.read()

        try:
            tree = ast.parse(codigo)
        except SyntaxError:
            return ComplexityMetrics()

        metricas = ComplexityMetrics()
        metricas.linhas = len(codigo.splitlines())

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                metricas.funcoes += 1
                metricas.complexidade_ciclomatica += self._calcular_complexidade(node)
            elif isinstance(node, ast.ClassDef):
                metricas.classes += 1
            elif isinstance(node, ast.Import) or isinstance(node, ast.ImportFrom):
                metricas.imports += 1

        return metricas

    def verificar_limites(self, metricas: ComplexityMetrics) -> list[str]:
        """
        Verifica se as métricas excedem os limites.

        Args:
            metricas: Métricas a verificar

        Returns:
            Lista de avisos
        """
        avisos = []

        if metricas.linhas > self.max_linhas:
            avisos.append(
                f"Arquivo muito longo: {metricas.linhas} linhas " f"(máximo: {self.max_linhas})"
            )

        if metricas.complexidade_ciclomatica > self.max_complexidade:
            avisos.append(
                f"Complexidade muito alta: {metricas.complexidade_ciclomatica} "
                f"(máximo: {self.max_complexidade})"
            )

        return avisos

    def _calcular_complexidade(self, node: ast.AST) -> int:
        """Calcula complexidade ciclomática de um nó AST."""
        complexidade = 1

        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.ExceptHandler)):
                complexidade += 1
            elif isinstance(child, ast.BoolOp):
                complexidade += len(child.values) - 1

        return complexidade
