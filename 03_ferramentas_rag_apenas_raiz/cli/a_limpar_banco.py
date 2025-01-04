#!/usr/bin/env python3
"""
Ferramenta CLI para limpar a tabela de documentos no Supabase.
"""

import os

from dotenv import load_dotenv
from rich.console import Console
from rich.prompt import Confirm
from supabase import Client, create_client

# Carrega variáveis de ambiente
load_dotenv()

# Configura console
console = Console()

def get_supabase_client() -> Client | None:
    """
    Inicializa cliente do Supabase.
    
    Returns:
        Client do Supabase ou None se houver erro
    """
    try:
        # Obtém credenciais
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
        
        if not url or not key:
            console.print("\n[red]❌ Credenciais do Supabase não encontradas no .env[/red]")
            return None
            
        # Cria cliente
        return create_client(url, key)
        
    except Exception as e:
        console.print("\n[red]Erro ao conectar com Supabase: %s[/red]", str(e))
        return None

def clear_documents(client: Client) -> None:
    """
    Limpa a tabela de documentos.
    
    Args:
        client: Cliente do Supabase
    """
    try:
        # Primeiro verifica se há documentos
        result = client.table("rag.01_base_conhecimento_regras_geral").select("count(*)", count="exact").execute()
        total_docs = result.count if hasattr(result, 'count') else 0
        
        if total_docs == 0:
            console.print("\n[yellow]ℹ️ A base já está vazia! Não há documentos para remover.[/yellow]")
            return
            
        # Se houver documentos, confirma operação
        if not Confirm.ask(f"\n⚠️ Existem {total_docs} documentos. Deseja realmente apagar todos?"):
            console.print("\n[yellow]Operação cancelada pelo usuário[/yellow]")
            return
            
        # Deleta todos os documentos
        client.table("rag.01_base_conhecimento_regras_geral").delete().execute()
        console.print("\n[green]✅ Tabela limpa com sucesso![/green]")
        
    except Exception as e:
        if 'relation "rag.01_base_conhecimento_regras_geral" does not exist' in str(e):
            console.print("\n[yellow]ℹ️ A tabela ainda não foi criada ou não está acessível.[/yellow]")
        else:
            console.print(f"\n[red]Erro ao limpar tabela: {e}[/red]")

def main() -> None:
    """Função principal."""
    try:
        console.print("\n[bold]🗑️ Limpeza da Base de Conhecimento[/bold]")
        
        # Inicializa cliente
        client = get_supabase_client()
        if not client:
            return
            
        # Limpa documentos
        clear_documents(client)
        
    except KeyboardInterrupt:
        console.print("\n\n[bold]👋 Operação cancelada![/bold]")
    except Exception as e:
        console.print("\n[red]Erro inesperado: %s[/red]", str(e))

if __name__ == "__main__":
    main() 