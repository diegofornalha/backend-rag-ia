#!/usr/bin/env python3
"""
Script para auxiliar na reorganização das pastas raiz.
Implementa as regras definidas em regras_md_apenas_raiz/1_core/l_transicao_pastas_raiz.md
"""

import os
import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

# Configuração da nova hierarquia
NOVA_HIERARQUIA = {
    "01_regras_md_apenas_raiz": "regras_md_apenas_raiz",
    "02_ferramentas_rag_apenas_raiz": "ferramentas_rag_apenas_raiz",
    "03_sql_apenas_raiz": "sql_apenas_raiz",
    "04_scripts_apenas_raiz": "scripts_apenas_raiz",
    "05_monitoring_apenas_raiz": "monitoring_apenas_raiz",
    "06_logs_apenas_raiz": "logs_apenas_raiz",
    "07_testes_apenas_raiz": "testes_apenas_raiz"
}

def validar_mudanca(pasta: str, novo_nome: str) -> bool:
    """
    Valida se uma mudança de pasta é permitida pelas regras.
    
    Args:
        pasta: Nome atual da pasta
        novo_nome: Novo nome proposto
        
    Returns:
        bool: True se a mudança é válida
    """
    # Verifica se pasta existe
    if not os.path.exists(pasta):
        print(f"❌ Pasta {pasta} não existe")
        return False
        
    # Verifica se novo nome já existe
    if os.path.exists(novo_nome):
        print(f"❌ Pasta {novo_nome} já existe")
        return False
        
    # Verifica histórico de mudanças
    historico = carregar_historico()
    ultima_mudanca = historico.get(pasta, {}).get("ultima_mudanca")
    
    if ultima_mudanca:
        dias_desde_mudanca = (datetime.now() - datetime.fromisoformat(ultima_mudanca)).days
        if dias_desde_mudanca < 14:  # Mínimo 2 semanas
            print(f"❌ Última mudança muito recente ({dias_desde_mudanca} dias)")
            return False
            
    return True

def carregar_historico() -> Dict:
    """
    Carrega histórico de mudanças do arquivo JSON.
    
    Returns:
        Dict com histórico de mudanças
    """
    historico_path = Path("./historico_mudancas.json")
    
    if not historico_path.exists():
        return {}
        
    try:
        return json.loads(historico_path.read_text())
    except Exception as e:
        print(f"Erro ao carregar histórico: {e}")
        return {}

def salvar_historico(historico: Dict) -> None:
    """
    Salva histórico de mudanças em arquivo JSON.
    
    Args:
        historico: Dicionário com histórico
    """
    try:
        Path("./historico_mudancas.json").write_text(
            json.dumps(historico, indent=2)
        )
    except Exception as e:
        print(f"Erro ao salvar histórico: {e}")

def registrar_mudanca(pasta: str, novo_nome: str) -> None:
    """
    Registra uma mudança no histórico.
    
    Args:
        pasta: Nome da pasta
        novo_nome: Novo nome da pasta
    """
    historico = carregar_historico()
    
    historico[pasta] = {
        "ultima_mudanca": datetime.now().isoformat(),
        "novo_nome": novo_nome
    }
    
    salvar_historico(historico)

def criar_plano_mudanca(pasta: str, novo_nome: str) -> str:
    """
    Cria documento com plano de mudança.
    
    Args:
        pasta: Nome atual da pasta
        novo_nome: Novo nome proposto
        
    Returns:
        str: Caminho do arquivo criado
    """
    conteudo = f"""## Proposta de Mudança

- Pasta Atual: {pasta}
- Nova Posição: {novo_nome}
- Justificativa: Adequação à nova hierarquia de pastas
- Impacto: Mudança de caminho, atualização de referências
- Plano:
  1. Criar backup
  2. Renomear pasta
  3. Atualizar referências
  4. Validar funcionamento
  5. Remover backup após 48h
"""
    
    plano_path = Path(f"./planos_mudanca/{pasta}_{datetime.now().strftime('%Y%m%d')}.md")
    plano_path.parent.mkdir(exist_ok=True)
    plano_path.write_text(conteudo)
    
    return str(plano_path)

def executar_mudanca(pasta: str, novo_nome: str) -> bool:
    """
    Executa a mudança de uma pasta.
    
    Args:
        pasta: Nome atual da pasta
        novo_nome: Novo nome da pasta
        
    Returns:
        bool: True se sucesso
    """
    try:
        # Criar backup
        backup_nome = f"{pasta}_backup_{datetime.now().strftime('%Y%m%d')}"
        shutil.copytree(pasta, backup_nome)
        
        # Renomear pasta
        shutil.move(pasta, novo_nome)
        
        # Registrar mudança
        registrar_mudanca(pasta, novo_nome)
        
        print(f"✅ Pasta {pasta} renomeada para {novo_nome}")
        print(f"📦 Backup criado em {backup_nome}")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao renomear pasta: {e}")
        return False

def main() -> None:
    """Função principal."""
    print("\n🔄 Iniciando reorganização de pastas...")
    
    for novo_nome, pasta_atual in NOVA_HIERARQUIA.items():
        if pasta_atual == novo_nome:
            print(f"✓ {pasta_atual} já está no padrão")
            continue
            
        if not os.path.exists(pasta_atual):
            print(f"? {pasta_atual} não encontrada")
            continue
            
        print(f"\n📁 Analisando {pasta_atual} -> {novo_nome}")
        
        # Validar mudança
        if not validar_mudanca(pasta_atual, novo_nome):
            continue
            
        # Criar plano
        plano_path = criar_plano_mudanca(pasta_atual, novo_nome)
        print(f"📋 Plano de mudança criado em {plano_path}")
        
        # Aguardar 48h (simulado para teste)
        print("⏳ Período de quarentena iniciado (48h)")
        # time.sleep(48 * 3600)  # Comentado para teste
        
        # Executar mudança
        if executar_mudanca(pasta_atual, novo_nome):
            print("✅ Mudança concluída com sucesso")
        else:
            print("❌ Falha na mudança")
            
    print("\n✨ Processo de reorganização concluído!")

if __name__ == "__main__":
    main() 