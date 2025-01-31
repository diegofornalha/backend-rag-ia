"""
Monitoramento do Git Flow.
"""

import re
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional

# Constantes
MAX_TOOLS = 15  # Limite máximo de ferramentas


@dataclass
class Commit:
    """Modelo para commits."""

    hash: str
    mensagem: str
    autor: str
    data: datetime
    branch: str
    tools_count: int = 0

    def incrementar_tools(self) -> bool:
        """
        Incrementa contador de ferramentas e verifica limite.

        Returns:
            True se ainda não atingiu limite, False caso contrário
        """
        self.tools_count += 1
        return self.tools_count < MAX_TOOLS


@dataclass
class Branch:
    """Modelo para branches."""

    nome: str
    commits: list[Commit]
    ultima_atualizacao: datetime


class ChangelogGenerator:
    """Gera changelogs a partir de commits."""

    def __init__(self):
        self.tipos_mudanca = {
            "feat": "Novas funcionalidades",
            "fix": "Correções de bugs",
            "docs": "Documentação",
            "style": "Estilo de código",
            "refactor": "Refatorações",
            "test": "Testes",
            "chore": "Manutenção",
        }

    def gerar_changelog(self, commits: list[Commit], versao: str) -> str:
        """
        Gera changelog para uma versão.

        Args:
            commits: Lista de commits
            versao: Número da versão

        Returns:
            Changelog formatado
        """
        # Agrupa commits por tipo
        por_tipo: dict[str, list[Commit]] = {}
        for commit in commits:
            tipo = self._extrair_tipo(commit.mensagem)
            if tipo not in por_tipo:
                por_tipo[tipo] = []
            por_tipo[tipo].append(commit)

        # Gera markdown
        linhas = [f"# Changelog v{versao}", f"\nData: {datetime.now().strftime('%Y-%m-%d')}\n"]

        for tipo, tipo_desc in self.tipos_mudanca.items():
            if tipo not in por_tipo:
                continue

            linhas.append(f"\n## {tipo_desc}")
            for commit in por_tipo[tipo]:
                msg = self._extrair_mensagem(commit.mensagem)
                linhas.append(f"- {msg} ({commit.hash[:7]})")

        return "\n".join(linhas)

    def _extrair_tipo(self, mensagem: str) -> str:
        """Extrai tipo do commit da mensagem."""
        match = re.match(r"^(feat|fix|docs|style|refactor|test|chore)", mensagem)
        return match.group(1) if match else "other"

    def _extrair_mensagem(self, mensagem: str) -> str:
        """Extrai mensagem principal do commit."""
        # Remove tipo e escopo
        msg = re.sub(r"^(feat|fix|docs|style|refactor|test|chore)(\(.+\))?: ", "", mensagem)
        # Capitaliza primeira letra
        return msg[0].upper() + msg[1:]


class BranchManager:
    """Gerencia branches do Git Flow."""

    def __init__(self):
        self.branches: dict[str, Branch] = {}
        self.protected_branches = ["main", "develop"]

    def criar_branch(self, nome: str, base: str) -> Branch:
        """
        Cria uma nova branch.

        Args:
            nome: Nome da branch
            base: Branch base

        Returns:
            Branch criada
        """
        if nome in self.branches:
            raise ValueError(f"Branch {nome} já existe")

        if base not in self.branches and base not in self.protected_branches:
            raise ValueError(f"Branch base {base} não existe")

        branch = Branch(nome=nome, commits=[], ultima_atualizacao=datetime.now())
        self.branches[nome] = branch
        return branch

    def deletar_branch(self, nome: str) -> None:
        """
        Deleta uma branch.

        Args:
            nome: Nome da branch
        """
        if nome in self.protected_branches:
            raise ValueError(f"Não é possível deletar branch protegida: {nome}")

        if nome not in self.branches:
            raise ValueError(f"Branch {nome} não existe")

        del self.branches[nome]

    def merge_branch(self, source: str, target: str) -> None:
        """
        Faz merge de uma branch em outra.

        Args:
            source: Branch origem
            target: Branch destino
        """
        if source not in self.branches:
            raise ValueError(f"Branch origem {source} não existe")

        if target not in self.branches and target not in self.protected_branches:
            raise ValueError(f"Branch destino {target} não existe")

        # Simula merge movendo commits
        if target in self.branches:
            self.branches[target].commits.extend(self.branches[source].commits)
            self.branches[target].ultima_atualizacao = datetime.now()

    def get_branch_status(self, nome: str) -> dict:
        """
        Retorna status de uma branch.

        Args:
            nome: Nome da branch

        Returns:
            Status da branch
        """
        if nome not in self.branches:
            raise ValueError(f"Branch {nome} não existe")

        branch = self.branches[nome]
        return {
            "nome": branch.nome,
            "commits": len(branch.commits),
            "ultima_atualizacao": branch.ultima_atualizacao,
            "dias_inativa": (datetime.now() - branch.ultima_atualizacao).days,
        }


class GitFlowMonitor:
    """Monitor do Git Flow."""

    def __init__(self):
        self.branches: dict[str, Branch] = {}
        self.padrao_commit = re.compile(r"^(feat|fix|docs|style|refactor|test|chore)(\(.+\))?: .+")
        self.branch_manager = BranchManager()
        self.changelog_generator = ChangelogGenerator()

    def registrar_commit(self, commit: Commit) -> None:
        """Registra um novo commit."""
        # Verifica limite de ferramentas
        if not commit.incrementar_tools():
            raise ValueError(f"Limite de {MAX_TOOLS} ferramentas atingido")

        if commit.branch not in self.branches:
            self.branches[commit.branch] = Branch(
                nome=commit.branch, commits=[], ultima_atualizacao=commit.data
            )

        branch = self.branches[commit.branch]
        branch.commits.append(commit)
        branch.ultima_atualizacao = max(branch.ultima_atualizacao, commit.data)

    def verificar_commit(self, commit: Commit) -> list[str]:
        """Verifica se um commit segue as convenções."""
        avisos = []

        if not self.padrao_commit.match(commit.mensagem):
            avisos.append(f"Mensagem de commit não segue convenção: {commit.mensagem}")

        if len(commit.mensagem) > 72:
            avisos.append(f"Mensagem de commit muito longa: {len(commit.mensagem)} caracteres")

        return avisos

    def get_metricas(self) -> dict:
        """Retorna métricas do Git Flow."""
        total_commits = sum(len(b.commits) for b in self.branches.values())

        metricas = {
            "total_branches": len(self.branches),
            "total_commits": total_commits,
            "commits_por_tipo": self._contar_commits_por_tipo(),
            "branches_ativas": len(
                [
                    b
                    for b in self.branches.values()
                    if (datetime.now() - b.ultima_atualizacao).days < 30
                ]
            ),
        }

        return metricas

    def _contar_commits_por_tipo(self) -> dict[str, int]:
        """Conta commits por tipo."""
        contagem = {}

        for branch in self.branches.values():
            for commit in branch.commits:
                match = self.padrao_commit.match(commit.mensagem)
                if match:
                    tipo = match.group(1)
                    contagem[tipo] = contagem.get(tipo, 0) + 1

        return contagem
