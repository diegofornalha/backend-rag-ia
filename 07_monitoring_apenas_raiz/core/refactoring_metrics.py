"""Módulo para análise de métricas de código."""

import ast
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Set
import networkx as nx

@dataclass
class CodeMetrics:
    """Métricas de código."""
    cyclomatic_complexity: int
    module_cohesion: float
    coupling_score: float
    dependencies: Set[str]
    loc: int
    
class MetricsAnalyzer:
    """Analisador de métricas de código."""
    
    def analyze_file(self, file_path: Path) -> CodeMetrics:
        """Analisa métricas de um arquivo."""
        with open(file_path) as f:
            content = f.read()
            
        tree = ast.parse(content)
        
        # Análise de complexidade ciclomática
        complexity = self._calculate_cyclomatic_complexity(tree)
        
        # Análise de coesão
        cohesion = self._calculate_module_cohesion(tree)
        
        # Análise de acoplamento
        coupling, deps = self._calculate_coupling(tree)
        
        # Contagem de linhas
        loc = len(content.splitlines())
        
        return CodeMetrics(
            cyclomatic_complexity=complexity,
            module_cohesion=cohesion,
            coupling_score=coupling,
            dependencies=deps,
            loc=loc
        )
        
    def _calculate_cyclomatic_complexity(self, tree: ast.AST) -> int:
        """Calcula complexidade ciclomática."""
        complexity = 1  # Base complexity
        
        for node in ast.walk(tree):
            # Branches aumentam complexidade
            if isinstance(node, (ast.If, ast.While, ast.For)):
                complexity += 1
            # Operadores lógicos aumentam complexidade    
            elif isinstance(node, ast.BoolOp):
                complexity += len(node.values) - 1
            # Handlers de exceção aumentam complexidade
            elif isinstance(node, ast.ExceptHandler):
                complexity += 1
                
        return complexity
        
    def _calculate_module_cohesion(self, tree: ast.AST) -> float:
        """Calcula coesão do módulo."""
        # Constrói grafo de dependências entre funções/métodos
        function_graph = nx.Graph()
        shared_variables = {}
        
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                function_graph.add_node(node.name)
                
                # Coleta variáveis usadas
                for child in ast.walk(node):
                    if isinstance(child, ast.Name):
                        if child.id not in shared_variables:
                            shared_variables[child.id] = set()
                        shared_variables[child.id].add(node.name)
                        
        # Adiciona arestas entre funções que compartilham variáveis
        for var, functions in shared_variables.items():
            for f1 in functions:
                for f2 in functions:
                    if f1 != f2:
                        function_graph.add_edge(f1, f2)
                        
        if not function_graph.nodes():
            return 1.0  # Coesão máxima para módulos vazios/simples
            
        # Calcula coesão como densidade do grafo
        return nx.density(function_graph)
        
    def _calculate_coupling(self, tree: ast.AST) -> tuple[float, Set[str]]:
        """Calcula acoplamento e dependências."""
        dependencies = set()
        import_count = 0
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                import_count += len(node.names)
                for name in node.names:
                    dependencies.add(name.name)
            elif isinstance(node, ast.ImportFrom):
                import_count += len(node.names)
                for name in node.names:
                    dependencies.add(f"{node.module}.{name.name}")
                    
        # Normaliza score de acoplamento (0-1)
        coupling_score = min(import_count / 20.0, 1.0)  # 20 imports = score 1.0
        
        return coupling_score, dependencies
        
class SemanticAnalyzer:
    """Analisador de mudanças semânticas."""
    
    def analyze_changes(self, old_content: str, new_content: str) -> Dict:
        """Analisa mudanças semânticas entre duas versões."""
        old_tree = ast.parse(old_content)
        new_tree = ast.parse(new_content)
        
        return {
            "complexity_changes": self._analyze_complexity_changes(old_tree, new_tree),
            "api_changes": self._analyze_api_changes(old_tree, new_tree)
        }
        
    def _analyze_complexity_changes(self, old_tree: ast.AST, new_tree: ast.AST) -> Dict:
        """Analisa mudanças de complexidade."""
        analyzer = MetricsAnalyzer()
        old_complexity = analyzer._calculate_cyclomatic_complexity(old_tree)
        new_complexity = analyzer._calculate_cyclomatic_complexity(new_tree)
        
        return {
            "old_complexity": old_complexity,
            "new_complexity": new_complexity,
            "complexity_delta": new_complexity - old_complexity
        }
        
    def _analyze_api_changes(self, old_tree: ast.AST, new_tree: ast.AST) -> Dict:
        """Analisa mudanças na API."""
        old_api = self._extract_api(old_tree)
        new_api = self._extract_api(new_tree)
        
        # Detecta breaking changes
        breaking_changes = []
        
        # Funções/métodos removidos
        for name in old_api["functions"] - new_api["functions"]:
            breaking_changes.append(f"Função removida: {name}")
            
        # Mudanças em assinaturas
        for name in old_api["functions"] & new_api["functions"]:
            old_params = old_api["signatures"].get(name, [])
            new_params = new_api["signatures"].get(name, [])
            
            if len(new_params) < len(old_params):
                breaking_changes.append(f"Parâmetros removidos: {name}")
            elif old_params != new_params[:len(old_params)]:
                breaking_changes.append(f"Assinatura alterada: {name}")
                
        return {
            "breaking_changes": breaking_changes,
            "total_changes": len(breaking_changes)
        }
        
    def _extract_api(self, tree: ast.AST) -> Dict:
        """Extrai API pública do código."""
        api = {
            "functions": set(),
            "signatures": {}
        }
        
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                # Ignora métodos privados
                if not node.name.startswith('_'):
                    api["functions"].add(node.name)
                    api["signatures"][node.name] = [
                        arg.arg for arg in node.args.args
                    ]
                    
        return api 