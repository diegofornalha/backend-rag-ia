"""
Script para executar o exemplo do sistema multiagente.
"""

import asyncio
import os
import sys

# Adiciona diretório raiz ao path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from backend_rag_ai_py.examples.multiagent_example import main

if __name__ == "__main__":
    # Executa exemplo
    asyncio.run(main())
