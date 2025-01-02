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
    embate_content = """# Migração para Pinecone Turbopuffer

## Contexto
O Pinecone anunciou que os índices vetoriais não-turbopuffer foram descontinuados. Como nossa aplicação utiliza o Pinecone para armazenamento de embeddings, precisamos migrar para a nova tecnologia Turbopuffer.

## Decisão
Migrar todos os índices vetoriais para o formato Turbopuffer do Pinecone. Esta decisão é necessária pois:
- Os índices antigos foram descontinuados
- O Turbopuffer é a nova tecnologia padrão
- Precisamos manter o suporte e atualizações

## Benefícios
- Melhor performance na busca vetorial
- Maior eficiência no uso de recursos
- Suporte contínuo da plataforma
- Acesso a recursos mais modernos

## Plano de Implementação
1. Backup dos dados existentes
2. Criação de novos índices com Turbopuffer
3. Migração dos dados para os novos índices
4. Atualização das referências no código
5. Testes de performance e validação

## Código de Exemplo
```python
import pinecone

# Inicialização com Turbopuffer
pinecone.init(api_key='sua_api_key')
pinecone.create_index(
    name='seu_indice',
    dimension=1536,  # dimensão dos embeddings
    metric='cosine'
)

# Verificação do status
index_description = pinecone.describe_index('seu_indice')
print(index_description)
```

## Status
Pendente de implementação

## Impacto
- Necessidade de downtime durante a migração
- Possível necessidade de ajustes no código de busca vetorial
- Melhoria esperada na performance após a migração"""
    
    # Calcula o hash do documento
    document_hash = calculate_hash(embate_content)
    
    # Prepara os dados para inserção no formato esperado pela API
    document_data = {
        "content": embate_content,
        "metadata": {
            "titulo": "Migração para Pinecone Turbopuffer",
            "version_key": "migracao_turbopuffer_v1",
            "tipo": "embate",
            "status": "pending"
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