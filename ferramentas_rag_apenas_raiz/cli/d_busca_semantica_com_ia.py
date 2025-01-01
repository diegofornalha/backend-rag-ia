#!/usr/bin/env python3
"""
Ferramenta CLI para realizar buscas semânticas com processamento LLM e interface conversacional.
"""

import os
import json
import requests
from typing import List, Dict, Optional
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt
from rich.spinner import Spinner
from rich.markdown import Markdown
from contextlib import contextmanager
from dotenv import load_dotenv
import google.generativeai as genai

# Carrega variáveis de ambiente
load_dotenv()

# Configura console
console = Console()

def get_api_url(endpoint: str = "") -> str:
    """
    Constrói a URL da API.
    
    Args:
        endpoint: Endpoint da API (opcional)
        
    Returns:
        str: URL completa da API
    """
    base_url = os.getenv("ACTIVE_URL", os.getenv("LOCAL_URL", "http://localhost:10000"))
    api_version = os.getenv("API_VERSION", "v1")
    base = f"{base_url}/api/{api_version}"
    return f"{base}/{endpoint.lstrip('/')}" if endpoint else base

class GeminiChat:
    """Gerencia chat com Gemini."""
    
    def __init__(self):
        """Inicializa modelo Gemini em modo chat."""
        gemini_key = os.getenv("GEMINI_API_KEY")
        if not gemini_key:
            raise ValueError("GEMINI_API_KEY não encontrada no .env")
            
        genai.configure(api_key=gemini_key)
        self.model = genai.GenerativeModel('gemini-pro')
        self.chat = self.model.start_chat(history=[])
        
        # Define o papel do assistente
        system_prompt = """Você é um assistente amigável e conversacional que ajuda usuários a encontrar informações.
        
        Seu objetivo é primeiro entender claramente o que o usuário precisa antes de buscar informações.
        
        Diretrizes:
        1. Seja amigável e conversacional
        2. Se a pergunta for vaga ou genérica, faça perguntas para clarificar
        3. Quando entender bem a necessidade, use [BUSCAR] para indicar que está pronto para pesquisar
        4. Após receber documentos, baseie suas respostas apenas neles
        5. Use markdown para formatar respostas
        
        Exemplos:
        Usuário: "oi"
        Você: "Olá! Como posso ajudar você hoje?"
        
        Usuário: "me fala sobre as regras"
        Você: "Claro! Mas para ajudar melhor, você gostaria de saber sobre quais regras específicas? Por exemplo:
        • Regras de desenvolvimento
        • Regras de documentação
        • Regras de organização
        • Ou outro tipo específico?"
        
        Usuário: "quero saber sobre as regras de documentação"
        Você: "[BUSCAR] Vou pesquisar informações sobre as regras de documentação do projeto."
        """
        
        self.chat.send_message(system_prompt, stream=False)
        
    def should_search(self, response: str) -> bool:
        """Verifica se a resposta indica que deve realizar busca."""
        return "[BUSCAR]" in response
        
    def process_initial_response(self, query: str) -> str:
        """Processa query inicial do usuário para entender a intenção.
        
        Args:
            query: Pergunta do usuário
            
        Returns:
            Resposta inicial ou indicação para busca
        """
        try:
            response = self.chat.send_message(query, stream=False)
            if response and hasattr(response, 'text'):
                return response.text
            return "Desculpe, não consegui processar sua mensagem. Pode reformular?"
        except Exception as e:
            console.print(f"\n[red]Erro ao processar com Gemini: {str(e)}[/red]")
            return "Desculpe, ocorreu um erro ao processar sua mensagem."
    
    def process_search_response(self, query: str, documents: List[Dict]) -> str:
        """Processa resposta após busca nos documentos.
        
        Args:
            query: Pergunta do usuário
            documents: Lista de documentos relevantes
            
        Returns:
            Resposta processada
        """
        try:
            # Prepara contexto com documentos
            context = "Documentos relevantes encontrados:\n\n"
            
            # Garante que documents é uma lista
            if not isinstance(documents, list):
                documents = []
            
            for doc in documents:
                # Extrai conteúdo com tratamento de erro
                try:
                    content = doc.get("conteudo", {})
                    if isinstance(content, str):
                        try:
                            content = json.loads(content)
                        except:
                            content = {"text": content}
                    
                    text = content.get("text", "").strip()
                    if text:
                        # Limita tamanho do texto para evitar exceder limites do Gemini
                        if len(text) > 1000:
                            text = text[:1000] + "..."
                        context += f"---\n{text}\n"
                except Exception as e:
                    console.print(f"\n[yellow]Aviso ao processar documento: {str(e)}[/yellow]")
                    continue
            
            # Se não houver documentos válidos
            if context == "Documentos relevantes encontrados:\n\n":
                context = "Não foram encontrados documentos relevantes."
            
            # Envia contexto e query para o chat
            prompt = f"""Com base nestes documentos:

{context}

Por favor, responda à pergunta do usuário: {query}

Lembre-se:
1. Use apenas as informações dos documentos
2. Se não houver informação suficiente, diga isso
3. Seja amigável e conversacional
4. Use markdown para formatar a resposta"""
            
            # Tenta gerar resposta
            try:
                response = self.chat.send_message(prompt, stream=False)
                if response and hasattr(response, 'text'):
                    return response.text
                else:
                    return "Desculpe, não consegui gerar uma resposta adequada."
            except Exception as e:
                console.print(f"\n[red]Erro ao gerar resposta: {str(e)}[/red]")
                return "Desculpe, ocorreu um erro ao gerar a resposta."
            
        except Exception as e:
            console.print(f"\n[red]Erro ao processar com Gemini: {str(e)}[/red]")
            return "Desculpe, ocorreu um erro ao processar sua pergunta."

class ChatHistory:
    """Gerencia o histórico da conversa."""
    
    def __init__(self, max_history: int = 5):
        self.messages: List[Dict[str, str]] = []
        self.max_history = max_history
        
    def add_message(self, role: str, content: str) -> None:
        """Adiciona mensagem ao histórico."""
        self.messages.append({"role": role, "content": content})
        if len(self.messages) > self.max_history:
            self.messages.pop(0)
            
    def get_context(self) -> str:
        """Retorna contexto da conversa para a próxima query."""
        context = []
        for msg in self.messages:
            prefix = "Usuário" if msg["role"] == "user" else "Assistente"
            context.append(f"{prefix}: {msg['content']}")
        return "\n".join(context)
    
    def clear(self) -> None:
        """Limpa o histórico."""
        self.messages.clear()

@contextmanager
def ChatSpinner():
    """Context manager para mostrar spinner durante processamento."""
    with console.status("[bold green]Processando...", spinner="dots") as status:
        try:
            yield status
        finally:
            pass

def search_documents(query: str, context: str = "") -> Optional[Dict]:
    """Realiza busca semântica via API.
    
    Args:
        query: Pergunta do usuário
        context: Contexto da conversa
        
    Returns:
        Resultados da busca ou None se houver erro
    """
    try:
        # Constrói endpoint de busca
        search_endpoint = get_api_url("search")
        
        # Prepara query com contexto
        full_query = f"{context}\nNova pergunta: {query}" if context else query
        
        # Faz requisição para a API
        response = requests.post(
            search_endpoint,
            json={"query": full_query},
            headers={"Content-Type": "application/json"}
        )
        
        # Verifica se a requisição foi bem sucedida
        response.raise_for_status()
        
        # Processa resultado
        try:
            data = response.json()
            
            # Verifica formato e ajusta se necessário
            if isinstance(data, dict):
                if "results" in data:
                    # Formato esperado
                    return data
                else:
                    # Encapsula em results se necessário
                    return {"results": data}
            else:
                console.print("\n[yellow]Aviso: Formato de resposta inesperado[/yellow]")
                return None
                
        except json.JSONDecodeError:
            console.print("\n[red]Erro ao decodificar resposta da API[/red]")
            return None
        
    except requests.exceptions.RequestException as e:
        console.print(f"\n[red]Erro ao conectar com a API: {str(e)}[/red]")
        console.print(f"\n[yellow]Tentando conectar em: {search_endpoint}[/yellow]")
        return None
    except Exception as e:
        console.print(f"\n[red]Erro inesperado: {str(e)}[/red]")
        return None

def format_response(response: str, docs: List[Dict]) -> None:
    """Formata e exibe a resposta.
    
    Args:
        response: Resposta processada
        docs: Lista de documentos relevantes
    """
    # Exibe resposta principal
    console.print("\n[bold]Resposta:[/bold]")
    console.print(Markdown(response))
    
    # Exibe documentos relevantes
    if docs:
        console.print(f"\n[bold]Documentos relevantes ({len(docs)} encontrados):[/bold]")
        
        # Cria tabela
        table = Table(show_header=True, header_style="bold")
        table.add_column("ID", style="dim")
        table.add_column("Título")
        table.add_column("Relevância", justify="right")
        
        # Adiciona resultados
        for doc in docs:
            similarity = doc.get("similarity", 0)
            table.add_row(
                str(doc.get("id", ""))[:10],
                doc.get("titulo", ""),
                f"{similarity*100:.0f}%"
            )
            
        console.print(table)

def main() -> None:
    """Função principal."""
    try:
        # Inicializa chat e histórico
        chat = GeminiChat()
        history = ChatHistory()
        
        console.print("\n[bold]🤖 Assistente de Busca Semântica[/bold]")
        console.print("Digite 'sair' para encerrar ou 'limpar' para reiniciar a conversa.")
        
        while True:
            # Obtém query do usuário
            query = Prompt.ask("\n[bold]Você[/bold]")
            
            # Verifica comandos especiais
            if query.lower() == "sair":
                console.print("\n[bold]👋 Até logo![/bold]")
                break
            elif query.lower() == "limpar":
                history.clear()
                chat = GeminiChat()
                console.print("\n[bold]🔄 Conversa reiniciada![/bold]")
                continue
            
            # Adiciona query ao histórico
            history.add_message("user", query)
            
            with ChatSpinner():
                # Processa query inicial
                initial_response = chat.process_initial_response(query)
                
                # Verifica se deve realizar busca
                if chat.should_search(initial_response):
                    # Remove tag [BUSCAR] da resposta
                    search_msg = initial_response.replace("[BUSCAR]", "").strip()
                    if search_msg:
                        console.print(f"\n[bold]🤖 Assistente:[/bold] {search_msg}")
                    
                    # Realiza busca
                    results = search_documents(query, history.get_context())
                    
                    if results:
                        # Processa documentos encontrados
                        docs = results.get("results", [])
                        response = chat.process_search_response(query, docs)
                        
                        # Formata e exibe resposta
                        format_response(response, docs)
                        
                        # Adiciona resposta ao histórico
                        history.add_message("assistant", response)
                    else:
                        console.print("\n[red]❌ Não foi possível realizar a busca[/red]")
                else:
                    # Exibe resposta direta
                    console.print(f"\n[bold]🤖 Assistente:[/bold] {initial_response}")
                    
                    # Adiciona resposta ao histórico
                    history.add_message("assistant", initial_response)
                
    except KeyboardInterrupt:
        console.print("\n\n[bold]👋 Até logo![/bold]")
    except Exception as e:
        console.print(f"\n[red]Erro inesperado: {str(e)}[/red]")

if __name__ == "__main__":
    main() 