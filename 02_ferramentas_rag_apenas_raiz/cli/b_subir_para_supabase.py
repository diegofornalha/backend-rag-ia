#!/usr/bin/env python3
"""
Ferramenta CLI para fazer upload de documentos para o Supabase.
"""

import os
import json
from typing import Dict, List, Optional
from pathlib import Path
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Confirm
from supabase import create_client, Client
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()

# Configura console
console = Console()

def get_supabase_client() -> Optional[Client]:
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
        console.print(f"\n[red]Erro ao conectar com Supabase: {str(e)}[/red]")
        return None

def process_markdown_file(file_path: Path) -> Optional[Dict]:
    """
    Processa arquivo markdown.
    
    Args:
        file_path: Caminho do arquivo
        
    Returns:
        Dicionário com dados processados ou None se houver erro
    """
    try:
        # Lê conteúdo do arquivo
        content = file_path.read_text(encoding="utf-8")
        
        # Extrai título do arquivo (primeira linha após remover #)
        title = file_path.stem
        first_line = content.split("\n")[0].strip("# ").strip()
        if first_line:
            title = first_line
            
        # Prepara dados
        return {
            "titulo": title,
            "conteudo": json.dumps({"text": content}),
            "metadata": json.dumps({
                "tipo": "markdown",
                "fonte": str(file_path)
            })
        }
        
    except Exception as e:
        console.print(f"\n[red]Erro ao processar {file_path}: {str(e)}[/red]")
        return None

def upload_documents(client: Client, docs_dir: str) -> None:
    """
    Faz upload dos documentos para o Supabase.
    
    Args:
        client: Cliente do Supabase
        docs_dir: Diretório com documentos
    """
    try:
        # Verifica diretório
        docs_path = Path(docs_dir)
        if not docs_path.exists():
            console.print(f"\n[red]❌ Diretório não encontrado: {docs_dir}[/red]")
            return
            
        # Lista arquivos markdown
        files = list(docs_path.rglob("*.md"))
        if not files:
            console.print(f"\n[yellow]Nenhum arquivo markdown encontrado em: {docs_dir}[/yellow]")
            return
            
        # Confirma upload
        if not Confirm.ask(f"\nEncontrados {len(files)} arquivos. Deseja fazer upload?"):
            console.print("\n[yellow]Upload cancelado[/yellow]")
            return
            
        # Processa e faz upload dos arquivos
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            
            task = progress.add_task("Processando arquivos...", total=len(files))
            
            for file_path in files:
                # Atualiza progresso
                progress.update(task, description=f"Processando {file_path.name}...")
                
                # Processa arquivo
                doc_data = process_markdown_file(file_path)
                if not doc_data:
                    continue
                    
                try:
                    # Faz upload
                    result = client.table("01_base_conhecimento_regras_geral").insert(doc_data).execute()
                    response_data = result.data if hasattr(result, 'data') else result
                    
                    console.print(f"\nResposta do Supabase para {file_path.name}:")
                    console.print(response_data)
                    
                    if isinstance(response_data, dict) and "error" in response_data:
                        console.print(f"\n[red]Erro ao fazer upload de {file_path.name}: {response_data['error']}[/red]")
                    elif not response_data:
                        console.print(f"\n[red]Erro ao fazer upload de {file_path.name}: Resposta vazia[/red]")
                    else:
                        console.print(f"\n[green]✅ Upload de {file_path.name} concluído[/green]")
                except Exception as e:
                    console.print(f"\n[red]Erro ao fazer upload de {file_path.name}: {str(e)}[/red]")
                    continue
                    
                # Atualiza progresso
                progress.advance(task)
            
        console.print("\n[green]✅ Upload concluído com sucesso![/green]")
        
    except Exception as e:
        console.print(f"\n[red]Erro inesperado: {str(e)}[/red]")

def check_table_exists(client: Client) -> bool:
    """
    Verifica se a tabela base_conhecimento_regras_geral existe.
    
    Args:
        client: Cliente do Supabase
        
    Returns:
        True se a tabela existe, False caso contrário
    """
    try:
        # Tenta fazer uma consulta simples
        result = client.table("01_base_conhecimento_regras_geral").select("*").limit(1).execute()
        return True
    except Exception as e:
        console.print(f"\n[red]Erro ao verificar tabela: {str(e)}[/red]")
        return False

def main() -> None:
    """Função principal."""
    try:
        console.print("\n[bold]📤 Upload de Documentos para Supabase[/bold]")
        
        # Inicializa cliente
        client = get_supabase_client()
        if not client:
            return
            
        # Verifica tabela
        console.print("\n[bold]Verificando tabela base_conhecimento_regras_geral...[/bold]")
        if not check_table_exists(client):
            console.print("\n[red]❌ Tabela '01_base_conhecimento_regras_geral' não encontrada no Supabase[/red]")
            console.print("\nExecute primeiro os scripts SQL em sql_apenas_raiz/1_setup/:")
            console.print("1. a_01_base_conhecimento_regras_geral.sql")
            console.print("2. b_02_embeddings_regras_geral.sql")
            console.print("3. c_setup_search.sql")
            return
            
        # Obtém diretório dos documentos
        docs_dir = os.getenv("DOCS_DIR", "docs")
        
        # Faz upload
        upload_documents(client, docs_dir)
        
    except KeyboardInterrupt:
        console.print("\n\n[bold]👋 Upload cancelado![/bold]")
    except Exception as e:
        console.print(f"\n[red]Erro inesperado: {str(e)}[/red]")

if __name__ == "__main__":
    main()