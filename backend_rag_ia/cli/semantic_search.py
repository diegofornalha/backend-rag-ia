#!/usr/bin/env python3

import os
import json
import sys
from typing import Any, Dict
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.markdown import Markdown
from dotenv import load_dotenv

from backend_rag_ia.services.semantic_search import SemanticSearchManager

# Carrega variáveis de ambiente
load_dotenv()

console = Console()

class SemanticSearchCLI:
    """CLI para busca semântica."""
    
    def __init__(self):
        """Inicializa o CLI."""
        self.search_manager = SemanticSearchManager()
        
    def buscar_documentos(self, query: str) -> Dict[str, Any]:
        """Busca e processa documentos usando o SemanticSearchManager.
        
        Args:
            query: Texto para buscar
            
        Returns:
            Resultados processados
        """
        try:
            console.print("\n🔍 Iniciando busca...")
            
            # Usa o SemanticSearchManager para busca
            results = self.search_manager.search(query)
            
            if not results.get("results"):
                return {
                    "answer": "Nenhum documento relevante encontrado",
                    "results": []
                }
                
            return results

        except Exception as e:
            console.print(f"❌ Erro na busca: {e}")
            return {
                "answer": f"Erro na busca: {str(e)}",
                "results": []
            }
            
    def exibir_resultados(self, query: str, processed: Dict[str, Any]) -> None:
        """Exibe resultados formatados.
        
        Args:
            query: Query de busca
            processed: Resultados processados
        """
        console.print(f"\n🔍 Resultados para: '{query}'")
        
        # Exibe resposta gerada
        if "answer" in processed:
            console.print("\n🤖 Resposta gerada:")
            console.print(Panel(
                Markdown(processed["answer"]),
                title="Resposta",
                border_style="green"
            ))
            
        # Exibe documentos encontrados
        results = processed.get("results", [])
        if not results:
            console.print("\n❌ Nenhum documento encontrado!")
            return
            
        console.print(f"\n📚 Documentos relevantes ({len(results)} encontrados):")
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("ID", style="dim")
        table.add_column("Título", style="green")
        table.add_column("Conteúdo", style="white", width=60)
        table.add_column("Relevância", style="cyan")
        
        for result in results:
            doc_id = str(result.get("id", ""))[:8]
            title = result.get("titulo", "Sem título")
            similarity = result.get("similarity", 0)
            
            # Extrai o texto do conteúdo JSON
            content_json = result.get("conteudo", {})
            if isinstance(content_json, str):
                try:
                    content_json = json.loads(content_json)
                except:
                    content_json = {"text": content_json}
            content = content_json.get("text", "")[:200] + "..."
            
            table.add_row(
                doc_id,
                title,
                content,
                f"{similarity:.1%}" if similarity else "N/A"
            )
            
        console.print(table)
        
        # Exibe estatísticas
        if "total_results" in processed:
            console.print(f"\n📊 Total de resultados: {processed['total_results']}")
        if "reranked_results" in processed:
            console.print(f"🔄 Resultados reordenados: {processed['reranked_results']}")

def main() -> None:
    """Função principal."""
    if len(sys.argv) < 2:
        console.print("❌ Erro: Informe o texto para buscar")
        console.print("Exemplo: python semantic_search.py 'como configurar ambiente'")
        sys.exit(1)
        
    query = sys.argv[1]
    cli = SemanticSearchCLI()
    results = cli.buscar_documentos(query)
    cli.exibir_resultados(query, results)

if __name__ == "__main__":
    main()
