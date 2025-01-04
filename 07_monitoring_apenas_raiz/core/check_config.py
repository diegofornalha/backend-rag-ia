"""Script para verificar e corrigir configurações."""

import os
from pathlib import Path
from typing import Dict

from .config_checker import ConfigChecker

def main():
    """Função principal."""
    # Carrega variáveis de ambiente atuais
    env_dict = dict(os.environ)
    
    # Inicializa checker
    checker = ConfigChecker()
    
    # Verifica configurações
    resultado = checker.check_env_config(env_dict)
    
    print("\n=== Verificação de Configurações ===")
    print(f"Status: {resultado['status']}")
    print("\nRecomendações:")
    for rec in resultado["recomendacoes"]:
        print(f"- {rec}")
        
    if resultado["status"] == "erro":
        print("\nTentando corrigir configurações...")
        env_dict = checker.fix_env_config(env_dict)
        
        # Verifica novamente
        resultado = checker.check_env_config(env_dict)
        
        print("\n=== Após correções ===")
        print(f"Status: {resultado['status']}")
        print("\nRecomendações:")
        for rec in resultado["recomendacoes"]:
            print(f"- {rec}")
            
        if resultado["status"] == "erro":
            print("\nAtenção: Ainda existem problemas que precisam ser corrigidos manualmente!")
            print("Verifique as recomendações acima e configure as variáveis necessárias.")
        else:
            print("\nConfigurações corrigidas com sucesso!")
            
if __name__ == "__main__":
    main() 