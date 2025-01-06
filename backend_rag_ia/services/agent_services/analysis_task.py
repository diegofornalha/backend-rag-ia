"""
Tarefa de análise da estrutura de diretórios.
"""

from dataclasses import dataclass
from typing import List, Dict, Set
from pathlib import Path


@dataclass
class DirectoryAnalysis:
    """Resultado da análise de um diretório."""

    path: str
    redundant_dirs: List[str]
    misplaced_dirs: List[str]
    empty_dirs: List[str]
    reasons: Dict[str, str]


class StructureAnalyzer:
    """Analisador da estrutura de diretórios."""

    def __init__(self, root_path: str):
        self.root = Path(root_path)
        self.valid_clusters = {
            "engine": {"agents", "coordinator", "continuity", "integration", "llms"},
            "analysis": {"code", "patterns", "optimization", "suggestions"},
            "generation": {"code", "docs", "tests", "refactor"},
            "infra": {"config", "logging", "storage", "security"},
            "interfaces": {"api", "cli", "events", "hooks"},
        }

    def analyze_cluster(self, cluster_name: str) -> DirectoryAnalysis:
        """Analisa um cluster específico."""
        cluster_path = self.root / cluster_name
        if not cluster_path.exists():
            return DirectoryAnalysis(
                path=str(cluster_path),
                redundant_dirs=[],
                misplaced_dirs=[],
                empty_dirs=[],
                reasons={},
            )

        valid_subdirs = self.valid_clusters[cluster_name]
        current_subdirs = {p.name for p in cluster_path.iterdir() if p.is_dir()}

        redundant = []
        misplaced = []
        empty = []
        reasons = {}

        # Verifica diretórios redundantes
        for subdir in current_subdirs:
            if subdir not in valid_subdirs:
                redundant.append(subdir)
                reasons[subdir] = f"Não pertence ao cluster {cluster_name}"

        # Verifica diretórios vazios
        for subdir in current_subdirs:
            dir_path = cluster_path / subdir
            if not any(dir_path.iterdir()):
                empty.append(subdir)
                reasons[subdir] = "Diretório vazio"

        # Verifica diretórios mal posicionados
        for subdir in current_subdirs:
            for other_cluster, other_subdirs in self.valid_clusters.items():
                if other_cluster != cluster_name and subdir in other_subdirs:
                    misplaced.append(subdir)
                    reasons[subdir] = f"Deveria estar em {other_cluster}"

        return DirectoryAnalysis(
            path=str(cluster_path),
            redundant_dirs=redundant,
            misplaced_dirs=misplaced,
            empty_dirs=empty,
            reasons=reasons,
        )

    def analyze_all(self) -> Dict[str, DirectoryAnalysis]:
        """Analisa todos os clusters."""
        results = {}
        for cluster in self.valid_clusters:
            results[cluster] = self.analyze_cluster(cluster)
        return results

    def get_cleanup_commands(self, results: Dict[str, DirectoryAnalysis]) -> List[str]:
        """Gera comandos para limpeza."""
        commands = []

        for cluster, analysis in results.items():
            dirs_to_remove = set(
                analysis.redundant_dirs + analysis.misplaced_dirs + analysis.empty_dirs
            )
            if dirs_to_remove:
                dirs_str = " ".join(dirs_to_remove)
                commands.append(f"rm -rf gemini/{cluster}/{{{dirs_str}}}")

        return commands
