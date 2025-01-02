#!/usr/bin/env python3
"""Script para corrigir problemas de qualidade do código."""

import subprocess


def main():
    """Executa as correções automáticas de qualidade do código."""
    print("Iniciando correções automáticas...")
    
    # Corrige problemas que podem ser resolvidos automaticamente
    subprocess.run(["ruff", ".", "--fix"], check=False)
    
    # Corrige imports
    subprocess.run(["ruff", ".", "--select", "I", "--fix"], check=False)
    
    print("Correções automáticas concluídas!")
    print("\nExecutando verificação final...")
    
    # Verifica problemas restantes
    subprocess.run(["ruff", "check", "."], check=False)

if __name__ == "__main__":
    main() 