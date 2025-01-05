"""
Teste do sistema de embates integrado ao multiagente.
"""

import pytest
import asyncio
from datetime import datetime

from backend_rag_ia.services.agent_services.embate_agent import EmbateSystem
from backend_rag_ia.config.multiagent_config import GEMINI_CONFIG

async def test_embate_limite_ferramentas():
    """Testa o limite de ferramentas no embate."""
    print("\n=== Teste de Limite de Ferramentas ===")
    
    system = EmbateSystem(config=GEMINI_CONFIG)
    
    # Executa várias vezes para atingir limite
    print("\n[Executando até atingir limite]")
    for i in range(5):
        task = f"Tarefa de teste {i+1}"
        result = await system.process_task(task)
        
        print(f"\nIteração {i+1}:")
        for agent_name, agent_result in result.items():
            if "error" in agent_result:
                print(f"{agent_name}: ❌ {agent_result['error']}")
            else:
                print(f"{agent_name}: ✅ Sucesso")

async def test_embate_interrupcao():
    """Testa a interrupção manual do embate."""
    print("\n=== Teste de Interrupção Manual ===")
    
    system = EmbateSystem(config=GEMINI_CONFIG)
    
    # Primeira execução
    print("\n[Primeira execução]")
    result = await system.process_task("Tarefa inicial")
    
    # Interrompe no meio
    print("\n[Interrompendo embates]")
    system.interromper_todos_embates()
    
    # Tenta executar novamente
    print("\n[Tentando executar após interrupção]")
    result = await system.process_task("Tarefa pós-interrupção")
    
    status = system.get_status_embates()
    for name, agent_status in status.items():
        print(f"\nAgente {name}:")
        print(f"Ativo: {'🟢' if agent_status['ativo'] else '🔴'}")

async def test_embate_parametros_invalidos():
    """Testa o comportamento com parâmetros inválidos."""
    print("\n=== Teste de Parâmetros Inválidos ===")
    
    system = EmbateSystem(config=GEMINI_CONFIG)
    
    # Testa com temperatura inválida
    print("\n[Testando temperatura inválida]")
    result = await system.process_task(
        "Tarefa teste",
        {
            "tema": "teste",
            "parametros": {
                "temperatura": 2.0,  # Inválido
                "max_tokens": 100
            }
        }
    )
    
    # Testa sem tema
    print("\n[Testando sem tema]")
    result = await system.process_task(
        "Tarefa teste",
        {
            "tema": None,
            "parametros": {
                "temperatura": 0.7,
                "max_tokens": 100
            }
        }
    )

async def test_embate_multiagente():
    """Testa o sistema de embates integrado ao multiagente."""
    print("\n=== Teste de Embate com Multiagente ===")
    
    system = EmbateSystem(config=GEMINI_CONFIG)
    
    # Primeira rodada - Pesquisa inicial
    print("\n[Primeira Rodada - Pesquisa]")
    task = "Analise as implicações éticas da IA generativa"
    result = await system.process_task(task, {"tema": "etica_ia"})
    
    # Verifica resultados
    print("\n[Verificando Resultados]")
    for agent_name, agent_result in result.items():
        print(f"\nAgente: {agent_name}")
        if "error" in agent_result:
            print(f"❌ Erro: {agent_result['error']}")
        else:
            print("✅ Sucesso")
            
    # Verifica status dos embates
    print("\n[Status dos Embates]")
    status = system.get_status_embates()
    for agent_name, agent_status in status.items():
        print(f"\nAgente: {agent_name}")
        print(f"Ativo: {'🟢' if agent_status['ativo'] else '🔴'}")
        print(f"Tools usadas: {agent_status['tools_count']}")
        print(f"Valor: {agent_status['valor']:.1f}")
    
    # Interrompe embates
    print("\n[Interrompendo Embates]")
    system.interromper_todos_embates()
    
    # Verifica status final
    status = system.get_status_embates()
    todos_inativos = all(not s["ativo"] for s in status.values())
    assert todos_inativos, "Todos os embates deveriam estar inativos"
    
    print("\n✅ Teste concluído com sucesso")

async def test_ativacao_automatica():
    """Testa a ativação automática de embates baseada no prompt."""
    print("\n=== Teste de Ativação Automática de Embates ===")
    
    system = EmbateSystem(config=GEMINI_CONFIG)
    
    # Lista de prompts para teste
    prompts = [
        # Deve ativar embate
        "Compare Python e JavaScript para desenvolvimento web",
        "Analise os prós e contras do TypeScript",
        "Debata sobre microserviços versus monolito",
        "Avalie diferentes ORMs do Python",
        
        # Não deve ativar embate
        "Qual é a sintaxe do for loop em Python?",
        "Como criar uma lista em Python",
        "Explique o que é uma função",
        "Mostre um exemplo de classe"
    ]
    
    for prompt in prompts:
        print(f"\n[Testando Prompt]: {prompt}")
        
        # Verifica se deve ativar embate
        requires_embate = any(agent.requer_embate(prompt) for agent in system.agents.values())
        print(f"Requer embate: {'🟢 Sim' if requires_embate else '🔴 Não'}")
        
        # Executa a tarefa
        result = await system.process_task(prompt)
        
        # Verifica resultados
        print("\nResultados:")
        for agent_name, agent_result in result.items():
            if "error" in agent_result:
                print(f"{agent_name}: ❌ {agent_result['error']}")
            else:
                print(f"{agent_name}: ✅ Sucesso")
        
        # Verifica status se ativou embate
        if requires_embate:
            status = system.get_status_embates()
            print("\nStatus dos agentes:")
            for name, agent_status in status.items():
                print(f"{name}:")
                print(f"  Tools: {agent_status['tools_count']}")
                print(f"  Valor: {agent_status['valor']:.1f}")
        
        print("\n" + "="*50)

if __name__ == "__main__":
    # Executa todos os testes
    asyncio.run(test_embate_limite_ferramentas())
    asyncio.run(test_embate_interrupcao())
    asyncio.run(test_embate_parametros_invalidos())
    asyncio.run(test_embate_multiagente())
    # Executa o teste de ativação automática
    asyncio.run(test_ativacao_automatica()) 