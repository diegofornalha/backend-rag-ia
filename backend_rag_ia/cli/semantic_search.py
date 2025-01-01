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

# Debug: Verifica se as variáveis foram carregadas
print(f"SUPABASE_URL: {os.getenv('SUPABASE_URL')}")
print(f"SUPABASE_KEY: {os.getenv('SUPABASE_KEY')}")

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
        # Exibe query
        console.print(f"\nResultados para: '{query}'", style="blue bold")
        
        # Exibe resposta gerada
        if "answer" in processed:
            console.print("\nResposta gerada:", style="blue bold")
            
            # Formata a resposta em tópicos numerados
            answer = processed["answer"]
            
            # Remove numeração existente se houver
            answer = answer.replace("*", "").replace("#", "")
            lines = [line.strip() for line in answer.split("\n") if line.strip()]
            
            # Remove numeração no início das linhas
            lines = [line[line.find(" ")+1:] if (line[0].isdigit() and " " in line) else line for line in lines]
            
            # Reformata com numeração consistente
            formatted_lines = []
            count = 1
            for line in lines:
                if line.strip():
                    formatted_lines.append(f"{count} {line}")
                    count += 1
            
            formatted_answer = "\n".join(formatted_lines)
            
            console.print(Panel(
                Markdown(formatted_answer),
                title="Resposta",
                border_style="green",
                padding=(1,2)
            ))
            
        # Exibe documentos encontrados
        results = processed.get("results", [])
        if not results:
            console.print("\n❌ Nenhum documento encontrado!")
            return
            
        console.print(f"\nDocumentos relevantes ({len(results)} encontrados):", style="blue bold")
        
        # Cria tabela formatada
        table = Table(show_header=True, header_style="bold magenta", padding=(0,1))
        table.add_column("ID", style="dim", width=8)
        table.add_column("Título", style="green", width=20)
        table.add_column("Conteúdo", style="white", width=60)
        
        for result in results:
            doc_id = str(result.get("id", ""))[:8]
            title = result.get("titulo", "Sem título")
            
            # Extrai o texto do conteúdo JSON
            content_json = result.get("conteudo", {})
            if isinstance(content_json, str):
                try:
                    content_json = json.loads(content_json)
                except:
                    content_json = {"text": content_json}
            content = content_json.get("text", "")
            
            # Limita o conteúdo e adiciona reticências
            if len(content) > 100:
                content = content[:100] + "..."
            
            table.add_row(
                doc_id,
                title,
                content
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
