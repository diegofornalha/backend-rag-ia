#!/usr/bin/env python3

import os
import json
import google.generativeai as genai
from rich.console import Console
from rich.panel import Panel
from rich import print
from rich.progress import track
import requests
from dotenv import load_dotenv

load_dotenv()

console = Console()

def search_documents(query):
    api_url = "http://localhost:10000"
    search_endpoint = f"{api_url}/api/v1/api/v1/search"
    
    try:
        response = requests.post(
            search_endpoint,
            json={"query": query, "limit": 10},
            headers={"Content-Type": "application/json"}
        )
        response.raise_for_status()
        return response.json().get("results", {}).get("results", [])
    except Exception as e:
        print(f"❌ Erro ao buscar documentos: {str(e)}")
        return None

def process_with_gemini(query, documents):
    try:
        genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
        model = genai.GenerativeModel('gemini-pro')
        
        context = "Documentos encontrados:\n"
        for doc in documents:
            content = doc.get("content", "")
            if isinstance(content, dict):
                content = content.get("text", "")
            context += f"\n- {content}"
        
        prompt = f"""Com base nos documentos fornecidos, responda à pergunta do usuário em uma única frase clara e objetiva em português.
        
        Documentos: {context}
        
        Pergunta: {query}
        
        Responda em uma única frase, mantendo a resposta concisa e direta."""
        
        response = model.generate_content(prompt)
        
        if response and response.text:
            # Remove caracteres especiais e formata a resposta
            clean_response = response.text.strip().replace('\n', ' ').replace('  ', ' ')
            return clean_response
        else:
            return "Não foi possível gerar uma resposta com base nos documentos encontrados."
            
    except Exception as e:
        print(f"❌ Erro ao processar com Gemini: {str(e)}")
        return f"Erro ao processar a resposta: {str(e)}"

def format_response(query, documents, response):
    if not documents:
        return Panel("❌ Nenhum documento encontrado para sua consulta.", title="Resposta do Sistema RAG")
    
    num_docs = len(documents)
    confidence = documents[0].get("similarity", 0) * 100 if documents else 0
    
    formatted_response = f"[red]🔍 BUSCA[/red] ({confidence:.0f}%) [blue][+{num_docs-1} docs relacionados][/blue]\n\n{response}"
    
    return Panel(formatted_response, title="Resposta do Sistema RAG")

def main():
    if len(os.sys.argv) < 2:
        print("❌ Por favor, forneça uma pergunta como argumento.")
        return
    
    query = " ".join(os.sys.argv[1:])
    
    print("\n🔍 Processando sua solicitação...")
    
    for _ in track(range(1), description="Buscando documentos..."):
        documents = search_documents(query)
    
    if not documents:
        print(Panel("❌ Erro ao buscar documentos.", title="Erro"))
        return
    
    response = process_with_gemini(query, documents)
    print(format_response(query, documents, response))

if __name__ == "__main__":
    main()
