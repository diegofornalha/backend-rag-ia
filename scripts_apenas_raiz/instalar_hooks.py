#!/usr/bin/env python3
import os
import stat
from pathlib import Path

from rich.console import Console

console = Console()

# Conteúdo do hook de pré-commit
PRE_COMMIT_HOOK = """#!/bin/sh
# Verifica qualidade do código antes do commit
python scripts_apenas_raiz/verificar_codigo.py

# Se a verificação falhar, impede o commit
if [ $? -ne 0 ]; then
    echo "❌ Verificação de código falhou. Por favor, corrija os problemas antes de fazer commit."
    exit 1
fi
"""

def instalar_hook():
    """Instala o hook de pré-commit."""
    git_dir = Path(".git")
    if not git_dir.is_dir():
        console.print("[red]❌ Diretório .git não encontrado. Execute este script na raiz do projeto.[/red]")
        return False

    hooks_dir = git_dir / "hooks"
    pre_commit = hooks_dir / "pre-commit"

    # Cria o arquivo de hook
    try:
        with pre_commit.open("w") as f:
            f.write(PRE_COMMIT_HOOK)
        
        # Torna o arquivo executável
        os.chmod(pre_commit, os.stat(pre_commit).st_mode | stat.S_IEXEC)
        
        console.print("[green]✅ Hook de pré-commit instalado com sucesso![/green]")
        return True
    except Exception as e:
        console.print(f"[red]❌ Erro ao instalar hook: {e}[/red]")
        return False

if __name__ == "__main__":
    console.print("\n[bold blue]Instalando hook de pré-commit...[/bold blue]")
    instalar_hook() 