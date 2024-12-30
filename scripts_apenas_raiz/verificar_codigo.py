#!/usr/bin/env python3
import subprocess
import sys
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()

# Constantes
RUFF_CONFIG = """
# Configurações do Ruff para verificação de código
[tool.ruff]
line-length = 100
target-version = "py311"

# Habilita todas as regras recomendadas
select = [
    "E",   # pycodestyle
    "F",   # pyflakes
    "I",   # isort
    "N",   # pep8-naming
    "UP",  # pyupgrade
    "YTT", # flake8-2020
    "B",   # flake8-bugbear
    "C4",  # flake8-comprehensions
    "DTZ", # flake8-datetimez
    "ISC", # flake8-implicit-str-concat
    "PIE", # flake8-pie
    "T20", # flake8-print
    "PT",  # flake8-pytest-style
    "Q",   # flake8-quotes
    "RET", # flake8-return
    "SIM", # flake8-simplify
    "TCH", # flake8-type-checking
    "INT", # flake8-gettext
    "ARG", # flake8-unused-arguments
    "PGH", # pygrep-hooks
    "PL",  # pylint
    "TRY", # tryceratops
    "RUF", # ruff-specific rules
]

# Ignora algumas regras específicas
ignore = [
    "E501",    # line too long
    "PLR0913", # too many arguments
]

# Configurações específicas
[tool.ruff.per-file-ignores]
"__init__.py" = ["F401"] # unused imports

[tool.ruff.isort]
known-first-party = ["backend_rag_ia"]
"""

def executar_comando(comando: str, shell: bool = True) -> tuple[bool, str]:
    """Executa um comando e retorna o resultado."""
    try:
        resultado = subprocess.check_output(comando, shell=shell, text=True, stderr=subprocess.STDOUT)
        return True, resultado
    except subprocess.CalledProcessError as e:
        return False, e.output
    except Exception as e:
        return False, str(e)

def verificar_ruff_instalado() -> bool:
    """Verifica se o Ruff está instalado."""
    console.print("\n[bold blue]Verificando instalação do Ruff[/bold blue]")
    sucesso, _ = executar_comando("ruff --version")
    if not sucesso:
        console.print("[red]❌ Ruff não encontrado. Instalando...[/red]")
        sucesso, resultado = executar_comando("pip install ruff")
        if not sucesso:
            console.print(f"[red]❌ Erro ao instalar Ruff: {resultado}[/red]")
            return False
        console.print("[green]✅ Ruff instalado com sucesso[/green]")
    else:
        console.print("[green]✅ Ruff já está instalado[/green]")
    return True

def criar_config_ruff():
    """Cria ou atualiza o arquivo de configuração do Ruff."""
    console.print("\n[bold blue]Configurando Ruff[/bold blue]")
    config_path = Path("pyproject.toml")
    
    try:
        with config_path.open("w") as f:
            f.write(RUFF_CONFIG)
        console.print("[green]✅ Configuração do Ruff atualizada[/green]")
        return True
    except Exception as e:
        console.print(f"[red]❌ Erro ao criar configuração: {e}[/red]")
        return False

def verificar_codigo(fix: bool = True) -> bool:
    """Verifica o código usando Ruff."""
    console.print("\n[bold blue]Verificando código[/bold blue]")
    
    # Primeiro faz uma verificação sem correção
    comando = "ruff check ."
    sucesso, resultado = executar_comando(comando)
    
    if sucesso:
        console.print("[green]✅ Nenhum problema encontrado[/green]")
        return True
    
    # Se houver problemas e fix=True, tenta corrigir
    if fix:
        console.print("\n[yellow]Problemas encontrados. Tentando corrigir...[/yellow]")
        comando_fix = "ruff check . --fix"
        sucesso_fix, resultado_fix = executar_comando(comando_fix)
        
        # Verifica novamente após a correção
        sucesso_final, resultado_final = executar_comando(comando)
        if sucesso_final:
            console.print("[green]✅ Todos os problemas foram corrigidos[/green]")
            return True
        console.print("[yellow]⚠️ Alguns problemas precisam ser corrigidos manualmente:[/yellow]")
        console.print(resultado_final)
    else:
        console.print("[yellow]⚠️ Problemas encontrados:[/yellow]")
        console.print(resultado)
    
    return False

def verificar_imports() -> bool:
    """Verifica e organiza imports usando Ruff."""
    console.print("\n[bold blue]Verificando imports[/bold blue]")
    
    comando = "ruff check . --select I"
    sucesso, resultado = executar_comando(comando)
    
    if sucesso:
        console.print("[green]✅ Imports estão organizados corretamente[/green]")
        return True
    
    console.print("[yellow]⚠️ Organizando imports...[/yellow]")
    comando_fix = "ruff check . --select I --fix"
    sucesso_fix, _ = executar_comando(comando_fix)
    
    if sucesso_fix:
        console.print("[green]✅ Imports organizados com sucesso[/green]")
        return True
    console.print("[red]❌ Alguns imports precisam ser organizados manualmente[/red]")
    return False

def main():
    console.print(Panel.fit("🔍 Verificação de Qualidade de Código", style="bold blue"))
    
    # Lista de verificações
    checklist = {
        "Instalação do Ruff": verificar_ruff_instalado,
        "Configuração do Ruff": criar_config_ruff,
        "Verificação de Código": verificar_codigo,
        "Verificação de Imports": verificar_imports,
    }
    
    resultados = {}
    for nome, funcao in checklist.items():
        resultados[nome] = funcao()
    
    # Resumo final
    console.print("\n[bold blue]Resumo da Verificação[/bold blue]")
    tabela = Table(title="Status das Verificações")
    tabela.add_column("Verificação", style="cyan")
    tabela.add_column("Status", style="green")
    
    todos_passaram = True
    for nome, resultado in resultados.items():
        status = "[green]✅ Passou[/green]" if resultado else "[red]❌ Falhou[/red]"
        tabela.add_row(nome, status)
        if not resultado:
            todos_passaram = False
    
    console.print(tabela)
    
    if todos_passaram:
        console.print("\n[green bold]✅ Todas as verificações passaram![/green bold]")
        sys.exit(0)
    else:
        console.print("\n[red bold]❌ Algumas verificações falharam[/red bold]")
        sys.exit(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n[yellow]Verificação interrompida pelo usuário[/yellow]")
        sys.exit(1) 