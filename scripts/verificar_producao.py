#!/usr/bin/env python3
import subprocess
import json
import time
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.panel import Panel
from rich.table import Table
from rich.live import Live
from datetime import datetime

console = Console()

def executar_comando(comando):
    try:
        resultado = subprocess.check_output(comando, shell=True).decode()
        return True, resultado
    except subprocess.CalledProcessError as e:
        return False, str(e)
    except Exception as e:
        return False, str(e)

def verificar_pull_local():
    console.print("\n[bold blue]1. Verificando Pull Local[/bold blue]")
    # Verificar se já temos a imagem localmente
    sucesso, resultado = executar_comando("docker images fornalha/backend:latest --format '{{.ID}}'")
    if sucesso and "1971c92916a2" in resultado:
        console.print("[green]✅ Imagem correta já presente localmente (ID: 1971c92916a2)[/green]")
        return True
    
    # Se não tiver ou for diferente, fazer o pull
    sucesso, resultado = executar_comando("docker pull fornalha/backend:latest")
    if sucesso:
        # Verificar se pegamos a imagem correta
        sucesso2, resultado2 = executar_comando("docker images fornalha/backend:latest --format '{{.ID}}'")
        if sucesso2 and "1971c92916a2" in resultado2:
            console.print("[green]✅ Pull realizado com sucesso - Imagem correta (ID: 1971c92916a2)[/green]")
            return True
        else:
            console.print("[red]❌ Pull realizado mas ID da imagem não corresponde ao esperado[/red]")
            return False
    else:
        console.print(f"[red]❌ Erro no pull local: {resultado}[/red]")
        return False

def verificar_portas():
    console.print("\n[bold blue]2. Verificando Portas Expostas[/bold blue]")
    sucesso, resultado = executar_comando("docker inspect fornalha/backend:latest")
    if sucesso:
        config = json.loads(resultado)[0]["Config"]
        portas = config.get("ExposedPorts", {})
        if "10000/tcp" in portas:
            console.print("[green]✅ Porta 10000 corretamente exposta[/green]")
            return True
        else:
            console.print("[red]❌ Porta 10000 não encontrada[/red]")
            return False
    return False

def verificar_variaveis():
    console.print("\n[bold blue]3. Verificando Variáveis de Ambiente[/bold blue]")
    sucesso, resultado = executar_comando("docker inspect fornalha/backend:latest")
    if sucesso:
        config = json.loads(resultado)[0]["Config"]
        env_vars = config.get("Env", [])
        variaveis_necessarias = {
            "HOST": False,
            "PORT": False,
            "PYTHON_VERSION": False
        }
        
        for var in env_vars:
            nome = var.split('=')[0]
            if nome in variaveis_necessarias:
                variaveis_necessarias[nome] = True
                console.print(f"[green]✅ Variável {nome} encontrada[/green]")
        
        faltando = [var for var, presente in variaveis_necessarias.items() if not presente]
        if faltando:
            console.print(f"[red]❌ Variáveis faltando: {', '.join(faltando)}[/red]")
            return False
        return True
    return False

def testar_local():
    console.print("\n[bold blue]1. Teste Local[/bold blue]")
    
    # Verificar se a imagem existe localmente
    sucesso, resultado = executar_comando("docker images fornalha/backend:latest --format '{{.ID}}'")
    if not sucesso or "1971c92916a2" not in resultado:
        console.print("[red]❌ Imagem não encontrada localmente ou ID não corresponde[/red]")
        return False
    
    # Testar execução básica
    console.print("Testando execução básica...")
    sucesso, resultado = executar_comando("docker run --rm fornalha/backend:latest python --version")
    if not sucesso:
        console.print("[red]❌ Falha ao executar Python na imagem[/red]")
        return False
    console.print(f"[green]✅ Python versão: {resultado.strip()}[/green]")
    
    # Verificar tamanho da imagem
    sucesso, resultado = executar_comando("docker images fornalha/backend:latest --format '{{.Size}}'")
    if sucesso:
        console.print(f"[green]✅ Tamanho da imagem: {resultado.strip()}[/green]")
    
    console.print("[green]✅ Teste local passou[/green]")
    return True

def testar_execucao_completa():
    console.print("\n[bold blue]2. Teste de Execução Completa[/bold blue]")
    
    # Teste de importações individuais
    pacotes = ["torch", "transformers", "sentence_transformers", "faiss"]
    for pacote in pacotes:
        console.print(f"Testando importação de {pacote}...")
        comando = f"docker run --rm fornalha/backend:latest python -c 'import {pacote}; print(\"OK\")'"""
        sucesso, resultado = executar_comando(comando)
        if not sucesso:
            console.print(f"[red]❌ Falha ao importar {pacote}: {resultado}[/red]")
            return False
        console.print(f"[green]✅ {pacote} importado com sucesso[/green]")
    
    # Teste de execução com todos os pacotes
    console.print("\nTestando execução completa...")
    comando_teste = """docker run --rm fornalha/backend:latest python -c '
import torch
import transformers
import sentence_transformers
import faiss
print("Versão PyTorch:", torch.__version__)
print("Versão Transformers:", transformers.__version__)
print("OK")
'"""
    sucesso, resultado = executar_comando(comando_teste)
    if not sucesso:
        console.print(f"[red]❌ Falha na execução completa: {resultado}[/red]")
        return False
    
    console.print(f"[green]Saída do teste completo:[/green]\n{resultado}")
    console.print("[green]✅ Teste de execução completa passou[/green]")
    return True

def main():
    console.print(Panel.fit("🚀 Verificação de Execução Local", style="bold blue"))
    
    checklist = {
        "Teste Local": testar_local,
        "Execução Completa": testar_execucao_completa
    }
    
    resultados = {}
    for nome, funcao in checklist.items():
        resultados[nome] = funcao()
    
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
        console.print("\n[green bold]✅ Todos os testes passaram![/green bold]")
    else:
        console.print("\n[red bold]❌ Alguns testes falharam[/red bold]")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n[yellow]Verificação interrompida pelo usuário[/yellow]") 