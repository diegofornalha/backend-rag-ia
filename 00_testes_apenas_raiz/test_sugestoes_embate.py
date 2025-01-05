"""
Teste da integração entre sistema de sugestões e embates.
"""

import pytest
import asyncio
from datetime import datetime

from backend_rag_ia.services import CursorAI
from backend_rag_ia.config.multiagent_config import GEMINI_CONFIG

async def test_sugestoes_com_embate():
    """Testa o sistema de sugestões com embates."""
    print("\n=== Teste de Sugestões com Embates ===")
    
    # Inicializa o CursorAI
    cursor = CursorAI()
    
    # Lista de prompts para teste
    prompts = [
        # Prompts que devem ativar embate
        {
            "texto": "Compare diferentes abordagens de arquitetura de software",
            "espera_embate": True,
            "contexto": {"tema": "arquitetura"}
        },
        {
            "texto": "Analise os prós e contras de microserviços",
            "espera_embate": True,
            "contexto": {"tema": "arquitetura"}
        },
        # Prompts que não devem ativar embate
        {
            "texto": "Como criar uma classe em Python?",
            "espera_embate": False,
            "contexto": {"tema": "python"}
        },
        {
            "texto": "Mostre um exemplo de função",
            "espera_embate": False,
            "contexto": {"tema": "codigo"}
        }
    ]
    
    for prompt in prompts:
        print(f"\n[Testando]: {prompt['texto']}")
        print(f"Espera embate: {'🟢 Sim' if prompt['espera_embate'] else '🔴 Não'}")
        
        # Testa processo completo
        context = {
            "prompt": prompt["texto"],
            "tema": prompt["contexto"]["tema"]
        }
        
        result = await cursor.process(context)
        print("\n[Resultado do Processamento]")
        if result["status"] == "success":
            print("✅ Processamento bem sucedido")
            if isinstance(result["result"], dict):
                for agent, output in result["result"].items():
                    print(f"\n{agent}:")
                    print(output if isinstance(output, str) else str(output))
        else:
            print(f"❌ Erro: {result.get('error')}")
            
        # Testa geração direta
        print("\n[Testando Geração]")
        suggestion = await cursor.generate(prompt["texto"], **prompt["contexto"])
        print(f"Sugestão gerada: {suggestion[:100]}...")
        
        print("\n" + "="*50)
        
async def test_capabilities():
    """Testa as capacidades do serviço."""
    print("\n=== Teste de Capacidades ===")
    
    cursor = CursorAI()
    capabilities = cursor.get_capabilities()
    
    print("\nCapacidades disponíveis:")
    for cap in capabilities:
        print(f"• {cap}")
        
    assert "code_analysis" in capabilities, "Deve ter capacidade de análise de código"
    assert "code_generation" in capabilities, "Deve ter capacidade de geração de código"
    
    print("\n✅ Teste de capacidades concluído")

if __name__ == "__main__":
    # Executa os testes
    asyncio.run(test_sugestoes_com_embate())
    asyncio.run(test_capabilities()) 