import logging

from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer

from backend_rag_ia.config.supabase_config import SupabaseConfig

# Configurando logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Carregando variáveis de ambiente
load_dotenv()

def generate_embedding(text: str) -> list[float]:
    """Gera embedding para o texto usando sentence-transformers."""
    model = SentenceTransformer('all-MiniLM-L6-v2')
    embedding = model.encode(text)
    return embedding.tolist()

def insert_test_documents():
    """Insere documentos de teste no Supabase."""
    try:
        supabase = SupabaseConfig()
        
        # Documentos de teste
        documents = [
            {
                "titulo": "Autenticação JWT",
                "conteudo": """
                Para implementar autenticação JWT em uma API FastAPI:
                1. Instale python-jose e passlib
                2. Configure uma chave secreta
                3. Crie funções para gerar e verificar tokens
                4. Use o decorator @requires_auth nos endpoints
                """
            },
            {
                "titulo": "Configuração PostgreSQL",
                "conteudo": """
                Passos para configurar PostgreSQL com pgvector:
                1. Instale a extensão pgvector
                2. Crie uma tabela com coluna do tipo vector
                3. Configure índices para busca por similaridade
                4. Implemente funções de busca vetorial
                """
            },
            {
                "titulo": "Deploy no Render",
                "conteudo": """
                Como fazer deploy de uma API FastAPI no Render:
                1. Crie uma conta no Render
                2. Configure o arquivo requirements.txt
                3. Defina as variáveis de ambiente
                4. Configure o comando de start
                """
            }
        ]
        
        logger.info("🔄 Gerando embeddings e inserindo documentos...")
        
        for doc in documents:
            # Gera embedding para o conteúdo
            embedding = generate_embedding(doc["conteudo"])
            
            # Insere documento com embedding
            response = supabase.client.table("documentos").insert({
                "titulo": doc["titulo"],
                "conteudo": doc["conteudo"],
                "embedding": embedding
            }).execute()
            
            if hasattr(response, 'error') and response.error:
                logger.error(f"❌ Erro ao inserir documento: {response.error}")
            else:
                logger.info(f"✅ Documento inserido: {doc['titulo']}")
        
        logger.info("✨ Documentos de teste inseridos com sucesso")
        
    except Exception as e:
        logger.error(f"❌ Erro ao inserir documentos: {e}")

if __name__ == "__main__":
    insert_test_documents() 