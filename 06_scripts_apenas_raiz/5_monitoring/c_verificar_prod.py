#!/usr/bin/env python3
import json
import logging
import subprocess

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

# Configuração do logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

console = Console()

# Constantes
IMAGEM_DOCKER = "fornalha/backend:latest"
ID_ESPERADO = "1971c92916a2"
PORTA_PADRAO = "10000"
CMD_DOCKER_RUN = "docker run --rm"
CMD_VERIFICAR_ID = f"docker images {IMAGEM_DOCKER} --format '{{{{.ID}}}}'"
CMD_VERIFICAR_TAMANHO = f"docker images {IMAGEM_DOCKER} --format '{{{{.Size}}}}'"
STATUS_CODE_OK = 0
VARIAVEIS_NECESSARIAS = {"HOST", "PORT", "PYTHON_VERSION"}
PACOTES_PYTHON = ["python", "torch", "transformers", "sentence_transformers", "pgvector"]

class VerificacaoError(Exception):
    """Exceção personalizada para erros de verificação."""

def executar_comando(comando: str) -> tuple[bool, str]:
    """Executa um comando e retorna o resultado."""
    try:
        resultado = subprocess.check_output(comando, shell=True).decode()
        return True, resultado.strip()
    except subprocess.CalledProcessError as e:
        logger.exception("Erro ao executar comando")
        return False, str(e)
    except Exception as e:
        logger.exception("Erro inesperado ao executar comando")
        return False, str(e)

def verificar_imagem() -> bool:
    """Verifica e garante que a imagem Docker correta está disponível."""
    logger.info("Iniciando verificação da imagem Docker")
    console.print("\n[bold blue]1. Verificação da Imagem[/bold blue]")

    # Verificar se a imagem existe localmente com ID correto
    sucesso, resultado = executar_comando(CMD_VERIFICAR_ID)
    if not sucesso:
        logger.error("Falha ao verificar ID da imagem")
        return False

    if ID_ESPERADO in resultado:
        console.print(f"[green]✅ Imagem correta já presente localmente (ID: {ID_ESPERADO})[/green]")
    else:
        logger.info("Imagem não encontrada ou desatualizada, tentando pull...")
        console.print("Imagem não encontrada ou desatualizada, tentando pull...")

        sucesso, resultado = executar_comando(f"docker pull {IMAGEM_DOCKER}")
        if not sucesso:
            logger.error(f"Erro no pull da imagem: {resultado}")
            console.print(f"[red]❌ Erro no pull da imagem: {resultado}[/red]")
            return False

        # Verificar novamente o ID após o pull
        sucesso, resultado = executar_comando(CMD_VERIFICAR_ID)
        if not sucesso or ID_ESPERADO not in resultado:
            logger.error("ID da imagem não corresponde ao esperado após pull")
            console.print("[red]❌ Pull realizado mas ID da imagem não corresponde ao esperado[/red]")
            return False

        logger.info("Pull realizado com sucesso")
        console.print(f"[green]✅ Pull realizado com sucesso - Imagem correta (ID: {ID_ESPERADO})[/green]")

    # Verificar tamanho da imagem
    sucesso, resultado = executar_comando(CMD_VERIFICAR_TAMANHO)
    if sucesso:
        logger.info(f"Tamanho da imagem: {resultado}")
        console.print(f"[green]✅ Tamanho da imagem: {resultado}[/green]")

    logger.info("Verificação da imagem concluída com sucesso")
    console.print("[green]✅ Verificação da imagem passou[/green]")
    return True

def verificar_configuracao() -> bool:
    """Verifica configurações da imagem Docker (portas e variáveis)."""
    logger.info("Iniciando verificação de configuração")
    console.print("\n[bold blue]2. Verificando Configuração da Imagem[/bold blue]")

    sucesso, resultado = executar_comando(f"docker inspect {IMAGEM_DOCKER}")
    if not sucesso:
        logger.error("Falha ao inspecionar imagem")
        console.print("[red]❌ Falha ao inspecionar imagem[/red]")
        return False

    try:
        config = json.loads(resultado)[0]["Config"]
    except (json.JSONDecodeError, IndexError, KeyError):
        logger.exception("Erro ao processar configuração da imagem")
        console.print("[red]❌ Erro ao processar configuração da imagem[/red]")
        return False

    # Verifica portas
    portas = config.get("ExposedPorts", {})
    porta_esperada = f"{PORTA_PADRAO}/tcp"
    if porta_esperada in portas:
        logger.info(f"Porta {PORTA_PADRAO} verificada com sucesso")
        console.print(f"[green]✅ Porta {PORTA_PADRAO} corretamente exposta[/green]")
    else:
        logger.error(f"Porta {PORTA_PADRAO} não encontrada")
        console.print(f"[red]❌ Porta {PORTA_PADRAO} não encontrada[/red]")
        return False

    # Verifica variáveis de ambiente
    env_vars = config.get("Env", [])
    variaveis_encontradas = {var.split("=")[0] for var in env_vars}
    variaveis_faltando = VARIAVEIS_NECESSARIAS - variaveis_encontradas

    for var in VARIAVEIS_NECESSARIAS:
        if var in variaveis_encontradas:
            logger.info(f"Variável {var} encontrada")
            console.print(f"[green]✅ Variável {var} encontrada[/green]")

    if variaveis_faltando:
        logger.error(f"Variáveis faltando: {', '.join(variaveis_faltando)}")
        console.print(f"[red]❌ Variáveis faltando: {', '.join(variaveis_faltando)}[/red]")
        return False

    logger.info("Verificação de configuração concluída com sucesso")
    console.print("[green]✅ Verificação de configuração passou[/green]")
    return True

def testar_ambiente() -> bool:
    """Testa o ambiente Python e suas dependências."""
    logger.info("Iniciando teste do ambiente")
    console.print("\n[bold blue]3. Teste do Ambiente[/bold blue]")

    for pacote in PACOTES_PYTHON:
        logger.info(f"Testando {pacote}")
        console.print(f"Testando {pacote}...")

        comando = (
            f"{CMD_DOCKER_RUN} {IMAGEM_DOCKER} python --version"
            if pacote == "python"
            else
            f"""{CMD_DOCKER_RUN} {IMAGEM_DOCKER} python -c '
import {pacote}
print("OK - " + {pacote}.__version__ if hasattr({pacote}, "__version__") else "OK")
'"""
        )

        sucesso, resultado = executar_comando(comando)
        if not sucesso:
            logger.error(f"Falha ao verificar {pacote}: {resultado}")
            console.print(f"[red]❌ Falha ao verificar {pacote}: {resultado}[/red]")
            return False

        logger.info(f"{pacote}: {resultado}")
        console.print(f"[green]✅ {pacote}: {resultado}[/green]")

    logger.info("Teste do ambiente concluído com sucesso")
    console.print("[green]✅ Teste do ambiente passou[/green]")
    return True

def main() -> None:
    """Função principal que executa todas as verificações."""
    logger.info("Iniciando verificação de execução local")
    console.print(Panel.fit("🚀 Verificação de Execução Local", style="bold blue"))

    checklist = {
        "Verificação da Imagem": verificar_imagem,
        "Configuração da Imagem": verificar_configuracao,
        "Teste do Ambiente": testar_ambiente,
    }

    resultados = {}
    for nome, funcao in checklist.items():
        try:
            resultados[nome] = funcao()
        except Exception:
            logger.exception(f"Erro ao executar {nome}")
            resultados[nome] = False

    # Resumo final
    console.print("\n[bold blue]Resumo da Verificação[/bold blue]")
    tabela = Table(title="Status dos Testes")
    tabela.add_column("Teste", style="cyan")
    tabela.add_column("Status", style="green")

    todos_passaram = True
    for nome, resultado in resultados.items():
        status = "[green]✅ Passou[/green]" if resultado else "[red]❌ Falhou[/red]"
        tabela.add_row(nome, status)
        if not resultado:
            todos_passaram = False

    console.print(tabela)

    if todos_passaram:
        logger.info("Todos os testes passaram")
        console.print("\n[green bold]✅ Todos os testes passaram![/green bold]")
    else:
        logger.error("Alguns testes falharam")
        console.print("\n[red bold]❌ Alguns testes falharam[/red bold]")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.warning("Verificação interrompida pelo usuário")
        console.print("\n[yellow]Verificação interrompida pelo usuário[/yellow]")
    except Exception:
        logger.exception("Erro inesperado durante a execução")
        console.print("\n[red bold]❌ Erro inesperado durante a execução[/red bold]")
