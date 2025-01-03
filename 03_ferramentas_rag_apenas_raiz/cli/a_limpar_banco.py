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
        key = os.getenv("SUPABASE_SERVICE_KEY")
        
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
        # Confirma operação
        if not Confirm.ask("\n⚠️ Isso irá apagar TODOS os documentos. Deseja continuar?"):
            console.print("\n[yellow]Operação cancelada[/yellow]")
            return
            
        # Deleta todos os documentos
        client.table("rag.01_base_conhecimento_regras_geral").delete().execute()
        
        console.print("\n[green]✅ Tabela limpa com sucesso![/green]")
        
    except Exception as e:
        console.print("\n[red]Erro ao limpar tabela: %s[/red]", str(e))

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