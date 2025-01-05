"""
Script para executar o exemplo do sistema multiagente.
"""

import os
import sys
import asyncio

# Adiciona diretório raiz ao path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from backend_rag_ia.examples.multiagent_example import main

if __name__ == "__main__":
    # Executa exemplo
    asyncio.run(main()) 