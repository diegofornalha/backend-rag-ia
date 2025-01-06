"""
CLI para testar o sistema multiagente.
"""

import asyncio
import argparse
from typing import Optional
from rich.console import Console
from rich.table import Table
from backend_rag_ia.services.agent_services.multi_agent import MultiAgentSystem
from backend_rag_ia.config.multiagent_config import AGENT_CONFIG, GEMINI_CONFIG

console = Console()

async def test_task_processing(
    system: MultiAgentSystem,
    task: str
) -> None:
    """Testa o processamento de uma tarefa."""
    console.print(f"\n[bold blue]Testando processamento da tarefa:[/] {task}")
    
    try:
        result = await system.process_task(task)
        
        table = Table(title="Resultado do Processamento")
        table.add_column("Campo", style="cyan")
        table.add_column("Valor", style="green")
        
        for key, value in result.items():
            table.add_row(key, str(value))
        
        console.print(table)
        
    except Exception as e:
        console.print(f"[bold red]Erro:[/] {str(e)}")

async def test_response_generation(
    system: MultiAgentSystem,
    prompt: str
) -> None:
    """Testa a geração de resposta."""
    console.print(f"\n[bold blue]Testando geração de resposta para prompt:[/] {prompt}")
    
    try:
        result = await system.generate_response(prompt)
        
        table = Table(title="Resposta Gerada")
        table.add_column("Campo", style="cyan")
        table.add_column("Valor", style="green")
        
        for key, value in result.items():
            table.add_row(key, str(value))
        
        console.print(table)
        
    except Exception as e:
        console.print(f"[bold red]Erro:[/] {str(e)}")

def show_system_status(system: MultiAgentSystem) -> None:
    """Mostra o status do sistema."""
    status = system.get_system_status()
    
    # Status do Coordenador
    coord_table = Table(title="Status do Coordenador")
    coord_table.add_column("Campo", style="cyan")
    coord_table.add_column("Valor", style="green")
    
    for key, value in status["coordinator"].items():
        coord_table.add_row(key, str(value))
    
    console.print(coord_table)
    
    # Métricas do Tracker
    metrics_table = Table(title="Métricas do Sistema")
    metrics_table.add_column("Métrica", style="cyan")
    metrics_table.add_column("Valor", style="yellow")
    
    for key, value in status["tracker"].items():
        metrics_table.add_row(key, str(value))
    
    console.print(metrics_table)
    
    # Configuração
    config_table = Table(title="Configuração")
    config_table.add_column("Parâmetro", style="cyan")
    config_table.add_column("Valor", style="green")
    
    for key, value in status["config"].items():
        config_table.add_row(key, str(value))
    
    console.print(config_table)

async def main(
    task: Optional[str] = None,
    prompt: Optional[str] = None,
    show_status: bool = False
) -> None:
    """Função principal do CLI."""
    console.print("[bold]Inicializando sistema multiagente...[/]")
    
    try:
        # Inicialização do sistema
        system = MultiAgentSystem()
        
        # Mostra configurações
        console.print("\n[bold cyan]Configurações carregadas:[/]")
        console.print(f"Modelo: {GEMINI_CONFIG['model']}")
        console.print(f"Timeout: {GEMINI_CONFIG['timeout']}s")
        console.print(f"Agentes disponíveis: {len(AGENT_CONFIG)}")
        
        # Executa testes conforme parâmetros
        if task:
            await test_task_processing(system, task)
        
        if prompt:
            await test_response_generation(system, prompt)
        
        if show_status:
            show_system_status(system)
            
    except Exception as e:
        console.print(f"\n[bold red]Erro na inicialização:[/] {str(e)}")
        return

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="CLI para testar o sistema multiagente")
    
    parser.add_argument(
        "--task",
        "-t",
        help="Tarefa para testar processamento"
    )
    
    parser.add_argument(
        "--prompt",
        "-p",
        help="Prompt para testar geração de resposta"
    )
    
    parser.add_argument(
        "--status",
        "-s",
        action="store_true",
        help="Mostra status do sistema"
    )
    
    args = parser.parse_args()
    
    if not any([args.task, args.prompt, args.status]):
        parser.print_help()
    else:
        asyncio.run(main(
            task=args.task,
            prompt=args.prompt,
            show_status=args.status
        )) 