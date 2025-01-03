"""
Teste do embate entrando em ação.
"""

import pytest
from datetime import datetime
from backend_rag_ia.monitoring.metrics import Metrica

def test_embate_em_acao():
    """Testa o embate entrando em ação com limite de ferramentas."""
    print("\n=== Teste de Embate em Ação ===")
    print("Simulando embate contínuo sobre um tema...")
    
    metrica = Metrica(
        nome="debate_ia_etica",
        valor=1.0,
        timestamp=datetime.now()
    )
    
    # Primeira rodada - Iniciando embate
    print("\n[Primeira Rodada - Início do Embate]")
    for i in range(4):
        print(f"\n>> Iteração {i+1}:")
        resultado = metrica.incrementar_tools()
        if resultado:
            print("✅ Ferramenta liberada e em uso")
        else:
            print("❌ Acesso bloqueado pelo sistema")
    
    # Segunda rodada - Embate continua após contenção
    print("\n[Segunda Rodada - Embate Continua]")
    for i in range(4):
        print(f"\n>> Nova iteração {i+1}:")
        resultado = metrica.incrementar_tools()
        if resultado:
            print("✅ Ferramenta liberada e em uso")
        else:
            print("❌ Acesso bloqueado pelo sistema")
    
    # Terceira rodada - Interrupção manual
    print("\n[Terceira Rodada - Interrupção Manual]")
    metrica.interromper_embate()
            
    print(f"\nTotal de iterações realizadas: {metrica.tools_count}")
    print(f"Status final do embate: {'🟢 Ativo' if metrica.embate_ativo else '🔴 Interrompido'}")

if __name__ == "__main__":
    pytest.main(["-v", "-s", __file__]) 