#!/usr/bin/env python3

import os
import requests
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()

console = Console()

def search_documents(query: str):
    """Realiza busca semântica via API."""
    try:
        # Obtém a URL da API do ambiente
        api_url = os.getenv("LOCAL_URL", "http://localhost:10000")
        
        # Endpoint de busca (corrigido)
        search_endpoint = f"{api_url}/api/v1/api/v1/search"
        
        # Faz requisição para a API
        response = requests.post(
            search_endpoint,
            json={"query": query},
            headers={"Content-Type": "application/json"}
        )
        
        # Verifica se a requisição foi bem sucedida
        response.raise_for_status()
        
        # Retorna os resultados
        data = response.json()
        
        # Extrai os resultados da resposta
        if isinstance(data, dict) and "results" in data:
            return data["results"]
        elif isinstance(data, dict):
            return data
        else:
            return None
        
    except requests.exceptions.RequestException as e:
        console.print(f"\n[red]Erro ao conectar com a API: {str(e)}[/red]")
        console.print(f"\n[yellow]Tentando conectar em: {search_endpoint}[/yellow]")
        return None

def main():
    """Função principal."""
    import sys
    
    # Verifica argumentos
    if len(sys.argv) < 2:
        console.print("\n[red]Por favor forneça uma query para busca[/red]")
        console.print("\nExemplo: python c_busca_semantica_simples.py 'como funciona o sistema RAG?'")
        return
        
    # Obtém query dos argumentos
    query = " ".join(sys.argv[1:])
    
    console.print("\n🔍 Iniciando busca...")
    
    # Realiza busca
    results = search_documents(query)
    
    if not results:
        console.print("\n[red]Nenhum resultado encontrado[/red]")
        return
        
    console.print(f"\nResultados para: '{query}'\n")
    
    # Mostra resposta gerada
    console.print("Resposta gerada:")
    console.print(Panel(
        results.get("answer", "Nenhuma resposta gerada"),
        title="Resposta",
        expand=True
    ))
    
    # Mostra documentos relevantes
    docs = results.get("results", [])
    if docs:
        console.print(f"\nDocumentos relevantes ({len(docs)} encontrados):")
        
        # Cria tabela
        table = Table(show_header=True, header_style="bold")
        table.add_column("ID", style="dim")
        table.add_column("Título")
        table.add_column("Conteúdo")
        
        # Adiciona resultados
        for doc in docs:
            content = doc.get("conteudo", {})
            if isinstance(content, str):
                try:
                    import json
                    content = json.loads(content)
                except:
                    content = {"text": content}
                    
            text = content.get("text", "")
            if len(text) > 100:
                text = text[:100] + "..."
                
            table.add_row(
                str(doc.get("id", ""))[:10],
                doc.get("titulo", ""),
                text
            )
            
        console.print(table)
        
    # Mostra estatísticas
    console.print(f"\n📊 Total de resultados: {results.get('total_results', 0)}")
    console.print(f"🔄 Resultados reordenados: {results.get('reranked_results', 0)}")

if __name__ == "__main__":
    main()
