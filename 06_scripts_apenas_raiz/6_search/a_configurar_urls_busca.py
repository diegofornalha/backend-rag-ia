#!/usr/bin/env python3
import os

import requests
from dotenv import load_dotenv
from rich.console import Console

console = Console()

def verificar_url(url: str, descricao: str) -> bool:
    """Verifica se uma URL está acessível"""
    try:
        response = requests.get(url + "/health", timeout=5.0)
        response.raise_for_status()
        console.print(f"[green]✅ {descricao} está acessível: {url}[/green]")
        return True
    except Exception as e:
        console.print(f"[yellow]⚠️ {descricao} não está acessível: {url}[/yellow]")
        console.print(f"[red]Erro: {e!s}[/red]")
        return False

def main():
    # Carregar variáveis de ambiente
    load_dotenv()
    
    # URLs atuais
    docker_url = os.getenv("SEMANTIC_SEARCH_DOCKER_URL", "http://localhost:10000")
    render_url = os.getenv("SEMANTIC_SEARCH_RENDER_URL", "https://api.coflow.com.br")
    mode = os.getenv("SEMANTIC_SEARCH_MODE", "auto")
    
    console.print("\n[bold]Configuração Atual:[/bold]")
    console.print(f"Modo: {mode}")
    console.print(f"URL Docker: {docker_url}")
    console.print(f"URL Render: {render_url}")
    
    # Verificar URLs
    docker_ok = verificar_url(docker_url, "Servidor Docker")
    render_ok = verificar_url(render_url, "Servidor Render")
    
    # Sugestões
    console.print("\n[bold]Sugestões:[/bold]")
    
    if not docker_ok and mode in ["local", "auto"]:
        console.print("""
[yellow]Para verificar o servidor Docker:[/yellow]
1. Verifique se o container está rodando:
   docker ps
2. Verifique se a porta 10000 está mapeada corretamente:
   docker port <container_id>
3. Inicie o container se necessário:
   docker-compose up -d
""")
    
    if not render_ok and mode in ["render", "auto"]:
        console.print("""
[yellow]Para verificar o servidor Render:[/yellow]
1. Verifique se o serviço está rodando no Render
2. Confirme a URL correta no dashboard do Render
3. Verifique se as variáveis de ambiente estão configuradas
""")

if __name__ == "__main__":
    main() 