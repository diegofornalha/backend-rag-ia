#!/usr/bin/env python3
import sys
import time
import json
import argparse
from datetime import datetime
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.live import Live
from rich.panel import Panel
import aiohttp
import asyncio
from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os

# Adiciona o diretório raiz ao PYTHONPATH
root_dir = Path(__file__).parent.parent.parent.parent
sys.path.append(str(root_dir))

from .embates.models import Embate, Argumento
from .embates.manager import EmbateManager

app = FastAPI(title="Debug Monitor")
console = Console()

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class DebugMonitor:
    def __init__(self, url="http://localhost:3000"):
        self.url = url
        self.console = Console()
        self.seen_messages = set()
        self.api_errors = []
        self.embate_manager = EmbateManager()
        self.current_embate = None
        
    async def create_monitoring_embate(self):
        """Cria um embate para monitorar a sessão atual."""
        embate = Embate(
            titulo="Monitoramento de Frontend",
            tipo="técnico",
            contexto="Monitoramento de mensagens e erros do frontend em tempo real",
            status="aberto"
        )
        result = await self.embate_manager.create_embate(embate)
        if result["status"] == "success":
            self.current_embate = embate
            self.console.print("[green]Embate de monitoramento criado com sucesso[/green]")
        
    def create_message_table(self):
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Timestamp", style="dim")
        table.add_column("Tipo", style="green")
        table.add_column("Mensagem", style="cyan")
        table.add_column("Análise", style="yellow")
        return table

    async def analyze_message(self, msg):
        """Analisa uma mensagem e cria um argumento no embate atual."""
        if not self.current_embate:
            await self.create_monitoring_embate()
            
        if isinstance(msg, dict):
            if "error" in msg:
                argumento = Argumento(
                    autor="monitor",
                    tipo="erro",
                    conteudo=f"Erro detectado: {msg['error']}"
                )
                analysis = "⚠️ Erro crítico - requer atenção"
            elif "role" in msg:
                argumento = Argumento(
                    autor=msg["role"],
                    tipo="mensagem",
                    conteudo=msg.get("content", "")
                )
                analysis = "✓ Mensagem processada"
            else:
                argumento = Argumento(
                    autor="sistema",
                    tipo="evento",
                    conteudo=str(msg)
                )
                analysis = "ℹ️ Evento do sistema"
                
            if self.current_embate:
                self.current_embate.argumentos.append(argumento)
                await self.embate_manager.update_embate(
                    self.current_embate.id,
                    {"argumentos": [arg.model_dump() for arg in self.current_embate.argumentos]}
                )
            return analysis
        return "N/A"

    async def display_messages(self, messages):
        if not messages:
            return
            
        table = self.create_message_table()
        
        for msg in messages:
            if isinstance(msg, dict):
                msg_id = json.dumps(msg)
                if msg_id not in self.seen_messages:
                    self.seen_messages.add(msg_id)
                    timestamp = datetime.now().strftime("%H:%M:%S")
                    
                    analysis = await self.analyze_message(msg)
                    
                    if "error" in msg:
                        table.add_row(
                            timestamp,
                            "Erro",
                            str(msg["error"]),
                            analysis
                        )
                    elif "role" in msg:
                        table.add_row(
                            timestamp,
                            msg["role"],
                            msg.get("content", ""),
                            analysis
                        )
                    elif "type" in msg:
                        table.add_row(
                            timestamp,
                            msg["type"],
                            str(msg.get("data", "")),
                            analysis
                        )

        if table.row_count > 0:
            self.console.print("\n")
            self.console.print(Panel(table, title="Monitor de Debug"))

    async def fetch_messages(self):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.url}/api/chat") as response:
                    if response.status == 200:
                        try:
                            data = await response.json()
                            return data.get("messages", [])
                        except json.JSONDecodeError as e:
                            print(f"\033[33mAviso: Resposta não é JSON válido: {e}\033[0m")
                            return None
                    else:
                        error_text = await response.text()
                        self.console.print(f"[red]Erro {response.status}: {error_text}[/red]")
                        return None
        except Exception as e:
            self.console.print(f"[red]Erro de conexão: {str(e)}[/red]")
            return None

    async def monitor(self):
        self.console.print(f"[green]Monitor de Debug em Tempo Real[/green]")
        self.console.print(f"[blue]Monitorando URL: {self.url}[/blue]")
        self.console.print("[yellow]Pressione Ctrl+C para sair[/yellow]\n")

        await self.create_monitoring_embate()

        while True:
            try:
                messages = await self.fetch_messages()
                if messages:
                    await self.display_messages(messages)
                await asyncio.sleep(1)
            except Exception as e:
                self.console.print(f"[red]Erro no monitor: {str(e)}[/red]")
                await asyncio.sleep(5)

monitor = DebugMonitor()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            try:
                message = json.loads(data)
                await monitor.display_messages([message])
            except json.JSONDecodeError:
                console.print(f"[red]Erro ao decodificar mensagem: {data}[/red]")
    except Exception as e:
        console.print(f"[red]Erro na conexão WebSocket: {str(e)}[/red]")

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(monitor.monitor())

def main():
    parser = argparse.ArgumentParser(description="Monitor de chat em tempo real")
    parser.add_argument("--url", type=str, default="http://localhost:3000", help="URL do frontend")
    parser.add_argument("--port", type=int, default=10000, help="Porta do monitor")
    args = parser.parse_args()
    
    monitor = DebugMonitor(args.url)
    
    # Iniciar o servidor FastAPI
    uvicorn.run(app, host="0.0.0.0", port=args.port, log_level="info")

if __name__ == "__main__":
    main() 