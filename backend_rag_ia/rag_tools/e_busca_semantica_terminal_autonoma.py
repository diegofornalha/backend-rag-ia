#!/usr/bin/env python3

import os
import sys
import json
import argparse
import requests
from typing import Dict, List, Optional
from rich.console import Console
from rich.panel import Panel
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()

# Configura console
console = Console()

# Categorias de assuntos para organização
CATEGORIES = {
    "server": ["backend", "server-side", "api", "database", "supabase", "deploy"],
    "client": ["frontend", "client-side", "interface", "ui", "ux"],
    "docs": ["documentação", "regras", "padrões", "convenções", "markdown"],
    "dev": ["desenvolvimento", "código", "implementação", "testes", "qualidade"],
    "tools": ["ferramentas", "scripts", "automação", "ci", "cd"]
}

def categorize_text(text: str) -> List[str]:
    """Categoriza o texto baseado nas palavras-chave."""
    text_lower = text.lower()
    categories = []
    
    for category, keywords in CATEGORIES.items():
        if any(keyword in text_lower for keyword in keywords):
            categories.append(category)
            
    return categories or ["outros"]

def search_documents(query: str, max_length: int = 200) -> Dict[str, str]:
    """Realiza busca semântica via API e retorna resposta categorizada.
    
    Args:
        query: Pergunta do usuário
        max_length: Tamanho máximo da resposta em caracteres
        
    Returns:
        Dicionário com categoria e resposta
    """
    try:
        api_url = os.getenv("LOCAL_URL", "http://localhost:10000")
        search_endpoint = f"{api_url}/api/v1/api/v1/search"
        
        # Faz requisição para a API
        response = requests.post(
            search_endpoint,
            json={"query": query},
            headers={"Content-Type": "application/json"}
        )
        
        response.raise_for_status()
        data = response.json()
        
        # Extrai documentos
        if isinstance(data, dict) and "results" in data:
            docs = data["results"].get("results", [])
            if docs:
                # Retorna apenas o texto do primeiro documento mais relevante
                content = docs[0].get("conteudo", {})
                if isinstance(content, str):
                    try:
                        content = json.loads(content)
                    except:
                        content = {"text": content}
                
                text = content.get("text", "").strip()
                # Limita a uma linha com tamanho máximo
                text = text.split("\n")[0][:max_length] + "..."
                
                # Categoriza a resposta
                categories = categorize_text(text)
                return {
                    "categories": categories,
                    "text": text,
                    "relevance": docs[0].get("relevance", 0)
                }
                
        return {
            "categories": ["outros"],
            "text": "Não encontrei uma resposta direta para sua pergunta.",
            "relevance": 0
        }
        
    except Exception as e:
        return {
            "categories": ["erro"],
            "text": f"Erro ao buscar: {str(e)}",
            "relevance": 0
        }

def format_response(result: Dict[str, str]) -> str:
    """Formata a resposta com categorias."""
    categories = result["categories"]
    text = result["text"]
    relevance = result["relevance"]
    
    # Emoji para cada categoria
    category_emojis = {
        "server": "🖥️",
        "client": "🌐",
        "docs": "📚",
        "dev": "👨‍💻",
        "tools": "🛠️",
        "outros": "❓",
        "erro": "❌"
    }
    
    # Formata categorias
    category_tags = " ".join(
        f"[{category_emojis.get(cat, '•')} {cat}]"
        for cat in categories
    )
    
    return f"{category_tags} ({relevance:.0%}) {text}"

def main() -> None:
    """Função principal."""
    try:
        # Configura argumentos
        parser = argparse.ArgumentParser(description="Busca semântica categorizada")
        parser.add_argument("query", nargs="+", help="Pergunta a ser pesquisada")
        parser.add_argument("-l", "--length", type=int, default=200, 
                          help="Tamanho máximo da resposta (padrão: 200)")
        
        args = parser.parse_args()
        query = " ".join(args.query)
        
        if len(query.split()) < 3:
            console.print("\n❌ Por favor, faça uma pergunta completa em uma frase.")
            sys.exit(1)
            
        console.print("\n🔍 Buscando resposta...")
        result = search_documents(query, args.length)
        response = format_response(result)
        console.print(Panel(response, border_style="cyan"))
            
    except KeyboardInterrupt:
        console.print("\n\n👋 Operação cancelada!")
        sys.exit(0)
    except Exception as e:
        console.print(f"\n❌ Erro: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
