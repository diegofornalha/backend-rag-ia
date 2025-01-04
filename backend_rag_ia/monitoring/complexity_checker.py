"""Implementa verificação de complexidade de código.

Este módulo fornece classes e funções para analisar e reportar a complexidade
ciclomática de funções em código Python.
"""

import ast
from dataclasses import dataclass


@dataclass
class ComplexityReport:
    """Define um relatório de complexidade.

    Attributes
    ----------
    file_path : str
        Caminho do arquivo analisado.
    function_name : str
        Nome da função analisada.
    complexity : int
        Valor da complexidade ciclomática.
    line_number : int
        Número da linha onde a função começa.

    """

    file_path: str
    function_name: str
    complexity: int
    line_number: int


class ComplexityChecker(ast.NodeVisitor):
    """Analisa complexidade ciclomática de código Python.

    Esta classe visita nós da AST para calcular a complexidade
    ciclomática de funções em código Python.

    Attributes
    ----------
    max_complexity : int
        Limite máximo de complexidade aceitável.
    complexity : int
        Complexidade atual sendo calculada.
    reports : list[ComplexityReport]
        Lista de relatórios de complexidade.

    """

    def __init__(self, max_complexity: int = 10) -> None:
        """Inicializa o verificador de complexidade.

        Parameters
        ----------
        max_complexity : int, optional
            Limite máximo de complexidade, por padrão 10.

        """
        self.max_complexity = max_complexity
        self.complexity = 0
        self.reports: list[ComplexityReport] = []
        self._current_function: str | None = None
        self._current_line: int = 0

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        """Visita definição de função e calcula sua complexidade.

        Parameters
        ----------
        node : ast.FunctionDef
            Nó da AST representando a definição da função.

        """
        old_complexity = self.complexity
        old_function = self._current_function
        self.complexity = 0
        self._current_function = node.name
        self._current_line = node.lineno

        # Visit all child nodes
        self.generic_visit(node)

        # Check if complexity exceeds limit
        if self.complexity > self.max_complexity:
            self.reports.append(ComplexityReport(
                file_path="",  # Set later
                function_name=node.name,
                complexity=self.complexity,
                line_number=node.lineno
            ))

        # Restore state
        self.complexity = old_complexity
        self._current_function = old_function

    def visit_If(self, node: ast.If) -> None:
        """Visita nó if e incrementa complexidade.

        Parameters
        ----------
        node : ast.If
            Nó da AST representando uma estrutura if.

        """
        self.complexity += 1
        self.generic_visit(node)

    def visit_While(self, node: ast.While) -> None:
        """Visita nó while e incrementa complexidade.

        Parameters
        ----------
        node : ast.While
            Nó da AST representando uma estrutura while.

        """
        self.complexity += 1
        self.generic_visit(node)

    def visit_For(self, node: ast.For) -> None:
        """Visita nó for e incrementa complexidade.

        Parameters
        ----------
        node : ast.For
            Nó da AST representando uma estrutura for.

        """
        self.complexity += 1
        self.generic_visit(node)

    def visit_ExceptHandler(self, node: ast.ExceptHandler) -> None:
        """Visita nó except e incrementa complexidade.

        Parameters
        ----------
        node : ast.ExceptHandler
            Nó da AST representando um bloco except.

        """
        self.complexity += 1
        self.generic_visit(node)

    def check_file(self, file_path: str) -> list[ComplexityReport]:
        """Analisa um arquivo e retorna relatórios de complexidade.

        Parameters
        ----------
        file_path : str
            Caminho do arquivo a ser analisado.

        Returns
        -------
        list[ComplexityReport]
            Lista de relatórios de complexidade encontrados.

        """
        with open(file_path, encoding='utf-8') as f:
            tree = ast.parse(f.read(), filename=file_path)

        self.reports = []
        self.visit(tree)

        # Set file path in reports
        for report in self.reports:
            report.file_path = file_path

        return self.reports
