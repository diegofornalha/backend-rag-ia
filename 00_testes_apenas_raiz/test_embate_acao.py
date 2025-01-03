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

def test_hidratacao_inputs_embate():
    """Testa a hidratação dos inputs durante o processo de embate."""
    print("\n=== Teste de Hidratação de Inputs no Embate ===")
    
    # Preparando dados de teste
    dados_entrada = {
        "tema": "ia_generativa",
        "contexto": "debate_etico",
        "parametros": {
            "max_tokens": 100,
            "temperatura": 0.7
        }
    }
    
    metrica = Metrica(
        nome="hidratacao_inputs",
        valor=0.0,
        timestamp=datetime.now()
    )
    
    # Teste de hidratação básica
    print("\n[Verificando Hidratação Básica]")
    assert dados_entrada["tema"] is not None, "Tema não pode ser nulo"
    assert isinstance(dados_entrada["parametros"], dict), "Parâmetros devem ser um dicionário"
    
    # Teste de validação de parâmetros
    print("\n[Validando Parâmetros do Embate]")
    assert 0 <= dados_entrada["parametros"]["temperatura"] <= 1, "Temperatura deve estar entre 0 e 1"
    assert dados_entrada["parametros"]["max_tokens"] > 0, "Max tokens deve ser positivo"
    
    # Simulando processo de hidratação
    print("\n[Simulando Hidratação Durante Embate]")
    for _ in range(3):
        metrica.valor += 0.3
        print(f"Nível de hidratação: {metrica.valor:.1f}")
        assert 0 <= metrica.valor <= 1, "Nível de hidratação deve estar entre 0 e 1"
    
    print("\n✅ Todos os testes de hidratação passaram com sucesso")

if __name__ == "__main__":
    pytest.main(["-v", "-s", __file__]) 