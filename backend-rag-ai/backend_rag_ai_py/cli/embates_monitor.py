import os
import asyncio
import json
from datetime import datetime
from typing import Dict, List, Optional
import aiohttp
from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from rich.console import Console
from rich.table import Table
from rich.text import Text
import google.generativeai as genai

# Configuração do Gemini
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY não encontrada nas variáveis de ambiente")

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-pro')

# Configuração do FastAPI
app = FastAPI(title="Monitor de Embates em Tempo Real")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

console = Console()

class EmbatesMonitor:
    def __init__(self):
        self.messages: List[Dict] = []
        self.console = Console()
        self.last_message_count = 0
        self.connected = False
        self.url = "http://localhost:3000"
        self.embates_history = []

    def create_message_table(self, messages: List[Dict]) -> Table:
        table = Table(
            title="🤖 Monitor de Embates em Tempo Real",
            show_header=True,
            header_style="bold magenta"
        )
        table.add_column("Hora", style="cyan", width=10)
        table.add_column("Tipo", style="green", width=10)
        table.add_column("Mensagem", style="white", width=50)
        table.add_column("Análise", style="yellow", width=30)

        for msg in messages:
            time = datetime.fromtimestamp(msg.get("timestamp", 0)).strftime("%H:%M:%S")
            role = msg.get("role", "unknown")
            content = msg.get("content", "")
            analysis = msg.get("analysis", "")
            
            role_color = {
                "user": "green",
                "assistant": "blue",
                "system": "yellow",
                "error": "red"
            }.get(role, "white")
            
            table.add_row(
                time,
                Text(role, style=role_color),
                content,
                analysis
            )

        return table

    def display_messages(self, messages: List[Dict]):
        if not messages:
            return
        
        table = self.create_message_table(messages)
        console.clear()
        console.print(table)

    async def analyze_message(self, message: str) -> str:
        try:
            prompt = f"""
            Analise a seguinte mensagem em um contexto de debate ou embate:
            "{message}"
            
            Forneça uma análise curta (máximo 50 caracteres) sobre:
            1. Tom da mensagem (cordial/agressivo)
            2. Qualidade da argumentação
            3. Possíveis falácias
            """
            
            response = model.generate_content(prompt)
            return response.text[:50]  # Limita a 50 caracteres
        except Exception as e:
            return f"Erro na análise: {str(e)[:30]}"

    async def process_message(self, message: Dict) -> Dict:
        if message.get("role") == "user":
            analysis = await self.analyze_message(message.get("content", ""))
            message["analysis"] = analysis
        else:
            message["analysis"] = ""
        return message

    async def fetch_messages(self) -> List[Dict]:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.url}/api/chat") as response:
                    if response.status == 200:
                        messages = await response.json()
                        # Processa apenas mensagens novas
                        new_messages = messages[self.last_message_count:]
                        processed_messages = []
                        for msg in new_messages:
                            processed_msg = await self.process_message(msg)
                            processed_messages.append(processed_msg)
                        return messages[:self.last_message_count] + processed_messages
                    else:
                        print(f"Erro ao buscar mensagens: Status {response.status}")
                        return []
        except Exception as e:
            print(f"Erro ao buscar mensagens: {str(e)}")
            return []

    async def monitor(self):
        print(f"\n🔍 Monitorando embates em: {self.url}")
        print("Pressione Ctrl+C para sair\n")

        while True:
            try:
                messages = await self.fetch_messages()
                if messages and len(messages) != self.last_message_count:
                    self.display_messages(messages)
                    self.last_message_count = len(messages)
                await asyncio.sleep(1)
            except Exception as e:
                print(f"Erro no monitor: {str(e)}")
                await asyncio.sleep(5)

@app.on_event("startup")
async def startup_event():
    monitor = EmbatesMonitor()
    asyncio.create_task(monitor.monitor())

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            try:
                message = json.loads(data)
                processed_message = await EmbatesMonitor().process_message(message)
                console.print(f"\n📩 Nova mensagem analisada: {processed_message}")
            except json.JSONDecodeError:
                console.print(f"\n⚠️ Mensagem inválida recebida: {data}")
    except Exception as e:
        console.print(f"\n❌ Erro na conexão WebSocket: {str(e)}")

def main():
    port = 10000
    print(f"\n🚀 Iniciando monitor de embates na porta {port}...")
    print(f"Usando Gemini API para análise de mensagens")
    uvicorn.run(app, host="0.0.0.0", port=port)

if __name__ == "__main__":
    main() 