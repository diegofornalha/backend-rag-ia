#!/usr/bin/env python3
import glob
import os
import subprocess

from rich.console import Console
from rich.panel import Panel

console = Console()


def check_directory_references() -> bool:
    """Verifica referências a diretórios em todos os arquivos Python."""
    try:
        console.print(
            Panel.fit("🔍 Verificando referências a diretórios", style="bold yellow")
        )

        dir_mapping = {
            "backend-rag-ia": "backend_rag_ia",
            "scripts": "scripts_apenas_raiz",
            "tests": "tests_apenas_raiz",
        }

        python_files = glob.glob("**/*.py", recursive=True)
        issues_found = False

        for file_path in python_files:
            with open(file_path) as f:
                content = f.read()

            for old_dir, new_dir in dir_mapping.items():
                if old_dir in content:
                    console.print(
                        f"[red]⚠️ Arquivo {file_path} contém referência ao diretório {old_dir!r}[/red]"
                    )
                    console.print(
                        f"[yellow]   Sugestão: Atualizar para {new_dir!r}[/yellow]"
                    )
                    issues_found = True

        if not issues_found:
            console.print("[green]✅ Nenhuma referência desatualizada encontrada![/green]")

        return not issues_found

    except Exception as e:
        console.print(f"[red]❌ Erro ao verificar referências: {e!s}[/red]")
        return False


def save_questions_to_md(section_name: str, questions: list[str]) -> None:
    """Salva novas perguntas no arquivo markdown.

    Args:
        section_name: Nome da seção onde adicionar as perguntas
        questions: Lista de perguntas para adicionar
    """
    md_path = "docs/NEXT_STEPS_QUESTIONS.md"
    try:
        with open(md_path) as f:
            content = f.read()

        # Verifica se a seção já existe
        if section_name not in content:
            # Adiciona nova seção no final do arquivo
            new_section = f"\n## {section_name}\n\n"
            new_section += "\n".join(f"{i + 1}. {q}" for i, q in enumerate(questions))
            new_section += "\n"

            # Adiciona antes da nota final
            if "---" in content:
                content = content.replace("---", f"{new_section}\n---")
            else:
                content += new_section

            with open(md_path, "w") as f:
                f.write(content)
    except Exception as e:
        console.print(f"[yellow]⚠️ Não foi possível salvar perguntas: {e!s}[/yellow]")


def format_and_check_directory(
    directory: str, max_attempts: int = 3, check_types: bool = True
) -> bool:
    """Formata e verifica um diretório usando Ruff e MyPy.

    Args:
        directory: Caminho do diretório para processar.
        max_attempts: Número máximo de tentativas de correção.
        check_types: Se True, executa verificação de tipos com MyPy.

    Returns:
        bool: True se todas as verificações passaram.
    """
    if not os.path.exists(directory):
        console.print(f"[yellow]⚠️ Diretório {directory} não encontrado[/yellow]")
        return False

    attempt = 1
    last_errors: list[str] = []

    while attempt <= max_attempts:
        console.print(f"\n[cyan]Tentativa {attempt} de {max_attempts} para {directory}...[/cyan]")

        # Executa Ruff com correções automáticas
        passed_ruff, current_errors = run_ruff(directory, fix=True)

        if passed_ruff:
            if check_types:
                # Se Ruff passou, verifica tipos com MyPy
                passed_mypy, mypy_errors = run_mypy(directory)
                if passed_mypy:
                    console.print(f"[green]✅ Todas as verificações passaram para {directory}![/green]")
                    return True
                current_errors.extend(mypy_errors)
            else:
                console.print(f"[green]✅ Formatação concluída para {directory}![/green]")
                return True

        # Verifica se os erros são os mesmos da última tentativa
        if set(current_errors) == set(last_errors):
            console.print("[yellow]⚠️ Mesmos erros persistem, interrompendo tentativas[/yellow]")
            break

        last_errors = current_errors
        attempt += 1

    msg = f"[red]❌ Não foi possível corrigir todos os problemas em {directory} "
    msg += f"após {max_attempts} tentativas[/red]"
    console.print(msg)
    return False


def suggest_next_steps(all_passed: bool, errors_found: list[str] = None) -> None:
    """Sugere próximos passos baseado no resultado da formatação.

    Args:
        all_passed: Se todas as verificações passaram
        errors_found: Lista de erros encontrados
    """
    console.print("\n[bold cyan]📋 Próximos Passos Sugeridos:[/bold cyan]")

    # Define perguntas padrão
    success_questions = [
        "Gostaria de executar os testes do projeto?",
        "Deseja fazer commit das alterações realizadas?",
        "Quer verificar a cobertura de tipos com MyPy?",
        "Precisa atualizar a documentação com as mudanças?",
        "Quer revisar as alterações feitas pelo formatador?"
    ]

    error_questions = [
        "Deseja ver detalhes dos erros encontrados?",
        "Quer tentar corrigir os erros manualmente?",
        "Prefere ignorar alguns tipos específicos de erro?",
        "Quer ajuda para entender algum erro específico?",
        "Deseja executar apenas a formatação sem verificação de tipos?"
    ]

    try:
        # Tenta carregar perguntas do arquivo markdown
        with open("docs/NEXT_STEPS_QUESTIONS.md") as f:
            content = f.read()

        if all_passed:
            # Extrai perguntas da seção "Após Formatação Bem-sucedida"
            section = content.split("### Após Formatação Bem-sucedida")[1].split("###")[0]
            questions = success_questions
        else:
            # Extrai perguntas da seção "Após Encontrar Erros"
            section = content.split("### Após Encontrar Erros")[1].split("###")[0]
            questions = error_questions

        # Se não encontrou a seção, salva as perguntas
        if "### Após Formatação Bem-sucedida" not in content:
            save_questions_to_md("🎨 Formatação de Código", success_questions)
        if "### Após Encontrar Erros" not in content:
            save_questions_to_md("🎨 Formatação de Código", error_questions)

    except FileNotFoundError:
        # Se o arquivo não existe, cria com as perguntas padrão
        initial_content = (
            "# Perguntas de Próximos Passos\n\n"
            "Este documento mantém um catálogo de perguntas sugeridas para próximos "
            "passos em diferentes contextos do projeto.\n\n"
            "## 🎨 Formatação de Código\n\n"
            "### Após Formatação Bem-sucedida\n\n"
            "1. Gostaria de executar os testes do projeto?\n"
            "2. Deseja fazer commit das alterações realizadas?\n"
            "3. Quer verificar a cobertura de tipos com MyPy?\n"
            "4. Precisa atualizar a documentação com as mudanças?\n"
            "5. Quer revisar as alterações feitas pelo formatador?\n\n"
            "### Após Encontrar Erros\n\n"
            "1. Deseja ver detalhes dos erros encontrados?\n"
            "2. Quer tentar corrigir os erros manualmente?\n"
            "3. Prefere ignorar alguns tipos específicos de erro?\n"
            "4. Quer ajuda para entender algum erro específico?\n"
            "5. Deseja executar apenas a formatação sem verificação de tipos?\n\n"
            "---\n\n"
            "> **Nota**: Este documento é atualizado continuamente com novas perguntas "
            "relevantes para o projeto.\n"
        )
        os.makedirs("docs", exist_ok=True)
        with open("docs/NEXT_STEPS_QUESTIONS.md", "w") as f:
            f.write(initial_content)
        questions = success_questions if all_passed else error_questions

    # Exibe as perguntas
    for i, question in enumerate(questions, 1):
        console.print(f"{i}. {question}")


def format_python_files(check_types: bool = True) -> bool:
    """Formata todos os arquivos Python do projeto usando Ruff e MyPy.

    Args:
        check_types: Se True, executa verificação de tipos com MyPy.

    Returns:
        bool: True se todas as verificações passaram.
    """
    try:
        # Primeiro verifica referências
        check_directory_references()

        # Lista de diretórios para formatar
        directories = ["backend_rag_ia", "monitoring", "scripts_apenas_raiz"]

        # Formatação e verificação
        title = "🎨 Formatando e verificando código Python com Ruff"
        if check_types:
            title += " e MyPy"
        console.print(Panel.fit(title, style="bold blue"))

        all_passed = True
        errors_found = []
        for directory in directories:
            if not format_and_check_directory(directory, check_types=check_types):
                all_passed = False

        if all_passed:
            console.print("\n[bold green]✨ Formatação e verificação concluídas com sucesso![/bold green]")
        else:
            msg = "\n[bold yellow]⚠️ Formatação concluída, mas alguns problemas "
            msg += "persistem[/bold yellow]"
            console.print(msg)

        # Sugere próximos passos
        suggest_next_steps(all_passed, errors_found)

        return all_passed

    except Exception as e:
        console.print(f"[red]❌ Erro durante o processo: {e!s}[/red]")
        suggest_next_steps(False, [str(e)])
        return False


def run_ruff(directory: str, fix: bool = True) -> tuple[bool, list[str]]:
    """Executa o Ruff para formatação e verificação.

    Args:
        directory: Caminho do diretório para processar.
        fix: Se True, tenta corrigir problemas automaticamente.

    Returns:
        Tuple com status (bool) e lista de erros (list).
    """
    try:
        cmd = ["ruff", "check", directory]
        if fix:
            cmd.append("--fix")
            cmd.extend(["--extend-select", "I,N,UP,B,A,C4,PT,RET,SIM,ERA,ICN"])

        result = subprocess.run(cmd, capture_output=True, text=True, check=False)

        if result.returncode == 0:
            console.print(f"[green]✅ {directory} passou na verificação do Ruff![/green]")
            return True, []

        errors = result.stdout.strip().split("\n")
        formatted_errors = []

        for error in errors:
            if error.strip():
                formatted_errors.append(error)
                console.print(f"   [yellow]{error}[/yellow]")

        return False, formatted_errors

    except Exception as e:
        console.print(f"[red]❌ Erro ao executar Ruff: {e!s}[/red]")
        return False, [str(e)]


def run_mypy(directory: str) -> tuple[bool, list[str]]:
    """Executa o MyPy para verificação de tipos.

    Args:
        directory: Caminho do diretório para verificar.

    Returns:
        Tuple com status (bool) e lista de erros (list).
    """
    try:
        result = subprocess.run(
            [
                "mypy",
                directory,
                "--ignore-missing-imports",
                "--disallow-untyped-defs",
                "--check-untyped-defs",
                "--warn-redundant-casts",
                "--warn-unused-ignores",
                "--warn-return-any",
                "--strict-optional",
            ],
            capture_output=True,
            text=True, check=False,
        )

        if result.returncode == 0:
            console.print(f"[green]✅ {directory} passou na verificação do MyPy![/green]")
            return True, []

        errors = result.stdout.strip().split("\n")
        formatted_errors = []

        for error in errors:
            if error.strip():
                formatted_errors.append(error)
                console.print(f"   [yellow]{error}[/yellow]")

        return False, formatted_errors

    except Exception as e:
        console.print(f"[red]❌ Erro ao executar MyPy: {e!s}[/red]")
        return False, [str(e)]


if __name__ == "__main__":
    format_python_files()
