"""Testes de integração para o fluxo de embates."""

import pytest
import asyncio
from datetime import datetime
import subprocess
import os

from backend_rag_ia.monitoring.metrics import Metrica

def executar_commit_push(ciclo: int):
    """Executa commit e push das alterações."""
    try:
        # Verifica se há alterações para commitar
        status = subprocess.run(['git', 'status', '--porcelain'], 
                              capture_output=True, 
                              text=True, 
                              check=True)
        
        if status.stdout.strip():
            # Há alterações para commitar
            subprocess.run(['git', 'add', '.'], check=True)
            subprocess.run(['git', 'commit', '-m', f'✨ Ciclo {ciclo}: Melhorias automáticas do embate'], check=True)
            
            # Push para o repositório remoto
            subprocess.run(['git', 'push'], check=True)
            print(f"\n✅ Commit e push do ciclo {ciclo} realizados com sucesso!")
        else:
            print(f"\n⏭️  Ciclo {ciclo} sem alterações para commitar")
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Erro ao executar git: {e}")

@pytest.mark.asyncio
async def test_continuous_embate_flow():
    """Testa o fluxo contínuo de embates com diferentes cenários em loop."""
    
    ciclo = 1
    intervencao_manual = False
    
    while not intervencao_manual:
        print(f"\n🔄 Iniciando Ciclo {ciclo} de Melhorias")
        print("=" * 50)
        
        # Cenário 1: Embate técnico contínuo
        print("\n=== Cenário 1: Embate Técnico ===")
        metrica_tecnica = Metrica(
            nome=f"debate_tecnico_ciclo_{ciclo}",
            valor=1.0,
            timestamp=datetime.now()
        )
        
        for i in range(5):
            print(f"\n>> Iteração Técnica {i+1}:")
            resultado = metrica_tecnica.incrementar_tools()
            if resultado:
                print("✅ Análise técnica em andamento")
                await asyncio.sleep(0.5)
            else:
                print("⏸️ Pausa para revisão técnica")
                await asyncio.sleep(2)
                if not metrica_tecnica.embate_ativo:
                    intervencao_manual = True
                    break
        
        if intervencao_manual:
            break
        
        # Cenário 2: Embate ético
        print("\n=== Cenário 2: Embate Ético ===")
        metrica_etica = Metrica(
            nome=f"debate_etico_ciclo_{ciclo}",
            valor=1.0,
            timestamp=datetime.now()
        )
        
        for i in range(5):
            print(f"\n>> Iteração Ética {i+1}:")
            resultado = metrica_etica.incrementar_tools()
            if resultado:
                print("✅ Análise ética em andamento")
                await asyncio.sleep(0.5)
            else:
                print("⏸️ Pausa para reflexão ética")
                await asyncio.sleep(2)
                if not metrica_etica.embate_ativo:
                    intervencao_manual = True
                    break
        
        if intervencao_manual:
            break
        
        # Cenário 3: Embate de performance
        print("\n=== Cenário 3: Embate de Performance ===")
        metrica_performance = Metrica(
            nome=f"debate_performance_ciclo_{ciclo}",
            valor=1.0,
            timestamp=datetime.now()
        )
        
        for i in range(3):
            print(f"\n>> Iteração Performance {i+1}:")
            resultado = metrica_performance.incrementar_tools()
            if resultado:
                print("✅ Análise de performance em andamento")
                await asyncio.sleep(0.5)
            else:
                print("⏸️ Pausa para otimização")
                await asyncio.sleep(2)
                if not metrica_performance.embate_ativo:
                    intervencao_manual = True
                    break
        
        if intervencao_manual:
            break
            
        # Executa commit e push ao final do ciclo
        executar_commit_push(ciclo)
        
        print(f"\n✨ Ciclo {ciclo} concluído!")
        print("Iniciando próximo ciclo em 5 segundos...")
        await asyncio.sleep(5)
        
        ciclo += 1
    
    print("\n🛑 Loop de melhorias interrompido por intervenção manual")
    print(f"Total de ciclos completados: {ciclo-1}")
    
    # Verifica estados finais
    assert not metrica_tecnica.modo_contencao, "Embate técnico deve estar fora do modo de contenção"
    assert not metrica_etica.modo_contencao, "Embate ético deve estar fora do modo de contenção"
    assert not metrica_performance.embate_ativo, "Embate de performance deve estar inativo" 