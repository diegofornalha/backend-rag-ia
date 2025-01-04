"""Testes de inserção de embates."""

import hashlib
import json

import requests
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()

def calculate_hash(content: str) -> str:
    return hashlib.sha256(content.encode()).hexdigest()

def main():
    print("\nVerificando backend local...")
    backend_url = "http://0.0.0.0:10000"
    
    try:
        # Verifica se o backend está rodando usando o endpoint /docs
        health_check = requests.get(f"{backend_url}/docs")
        if health_check.status_code != 200:
            print("\n❌ Erro: Backend local não está respondendo")
            return
        print("✅ Backend local está rodando")
    except Exception as e:
        print(f"\n❌ Erro ao conectar com backend local: {e}")
        print("Certifique-se que o backend está rodando com 'python main.py'")
        return
    
    print("\nPreparando embate...")
    
    # Prepara o conteúdo do embate
    embate_content = """# Unificação dos Diretórios de Testes de Integração

## Contexto
Atualmente existem dois diretórios com testes de integração:
1. `/00_testes_apenas_raiz/integration/`
2. `/00_testes_apenas_raiz/core/integration/`

Esta duplicação viola a regra de não repetir nomes de diretórios para evitar confusão.

## Impacto
- Confusão sobre onde adicionar novos testes
- Dificuldade de manutenção
- Possível duplicação de testes
- Violação das regras de organização do projeto

## Análise Técnica
1. O diretório `/00_testes_apenas_raiz/integration/` contém a maioria dos testes
2. O diretório `/00_testes_apenas_raiz/core/integration/` tem apenas:
   - test_embates_integration.py (vazio)
   - __init__.py (vazio)

## Decisão
Unificar os diretórios de teste movendo todo o conteúdo para `/00_testes_apenas_raiz/integration/` e remover o diretório `/00_testes_apenas_raiz/core/integration/`.

## Plano de Implementação
1. Verificar se há conteúdo relevante em `/core/integration/`
2. Mover qualquer conteúdo necessário para `/integration/`
3. Remover o diretório `/core/integration/`
4. Atualizar documentação e referências se necessário

## Status
Resolvido

## Implementação Realizada
1. Verificado conteúdo dos arquivos em `/core/integration/`:
   - test_embates_integration.py estava vazio
   - __init__.py estava vazio
2. Não foi necessário mover conteúdo pois os arquivos estavam vazios
3. Removidos os arquivos:
   - /00_testes_apenas_raiz/core/integration/test_embates_integration.py
   - /00_testes_apenas_raiz/core/integration/__init__.py
4. Diretório `/core/integration/` removido
5. Todos os testes de integração agora estão unificados em `/00_testes_apenas_raiz/integration/`

## Impacto da Mudança
- Melhor organização do código
- Conformidade com as regras do projeto
- Facilita manutenção e adição de novos testes"""
    
    # Calcula o hash do documento
    document_hash = calculate_hash(embate_content)
    
    # Prepara os dados para inserção
    document_data = {
        "content": embate_content,
        "metadata": {
            "titulo": "Unificação dos Diretórios de Testes de Integração",
            "version_key": "unificacao_testes_integracao_v1",
            "tipo": "embate",
            "status": "resolvido"
        },
        "document_hash": document_hash
    }
    
    print("\nDados do documento:")
    print(json.dumps(document_data, indent=2))
    
    print("\nInserindo documento via API local...")
    try:
        # Envia para o endpoint de inserção de documentos
        response = requests.post(
            f"{backend_url}/api/v1/api/v1/documents",
            json=document_data
        )
        
        if response.status_code == 200:
            print("\n✅ Documento inserido com sucesso!")
            print("\nDetalhes do registro inserido:")
            print(json.dumps(response.json(), indent=2))
        else:
            print(f"\n❌ Erro ao inserir documento: {response.status_code}")
            print(f"Detalhes: {response.text}")
            print("\n❌ Falha ao inserir documento")
        
    except Exception as e:
        print(f"\n❌ Erro ao inserir documento: {e}")
        print("\n❌ Falha ao inserir documento")

if __name__ == "__main__":
    main() 