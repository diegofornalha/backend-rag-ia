import os
from dotenv import load_dotenv
from supabase import create_client, Client
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Carregar variáveis de ambiente
load_dotenv()

# Inicializar cliente Supabase
supabase: Client = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_KEY")
)

def testar_estrutura():
    """Testa se as tabelas foram criadas corretamente"""
    try:
        # Testar tabela de documentos
        response = supabase.table("01_base_conhecimento_regras_geral").select("*").limit(1).execute()
        logger.info("✅ Tabela 01_base_conhecimento_regras_geral está acessível")
        
        # Testar tabela de embeddings
        response = supabase.table("02_embeddings_regras_geral").select("*").limit(1).execute()
        logger.info("✅ Tabela 02_embeddings_regras_geral está acessível")
        
        return True
    except Exception as e:
        logger.error(f"❌ Erro ao testar estrutura: {str(e)}")
        return False

def testar_insercao():
    """Testa a inserção de um documento e seu embedding"""
    try:
        # Inserir documento
        doc_data = {
            "titulo": "Documento de Teste",
            "conteudo": "Este é um documento de teste para validar a estrutura.",
            "metadata": {"public": True}
        }
        
        response = supabase.table("01_base_conhecimento_regras_geral").insert(doc_data).execute()
        doc_id = response.data[0]['id']
        logger.info(f"✅ Documento inserido com ID: {doc_id}")
        
        # Inserir embedding
        embedding_data = {
            "documento_id": doc_id,
            "embedding": [0.1] * 384  # Embedding de teste
        }
        
        response = supabase.table("02_embeddings_regras_geral").insert(embedding_data).execute()
        logger.info("✅ Embedding inserido com sucesso")
        
        return True
    except Exception as e:
        logger.error(f"❌ Erro ao testar inserção: {str(e)}")
        return False

def testar_busca():
    """Testa a função de busca semântica"""
    try:
        # Criar embedding de teste
        query_embedding = [0.1] * 384
        
        # Executar busca
        response = supabase.rpc(
            'match_documents',
            {
                'query_embedding': query_embedding,
                'match_threshold': 0.5,
                'match_count': 5
            }
        ).execute()
        
        logger.info(f"✅ Busca semântica retornou {len(response.data)} resultados")
        return True
    except Exception as e:
        logger.error(f"❌ Erro ao testar busca: {str(e)}")
        return False

def main():
    logger.info("🔄 Iniciando testes da base de conhecimento...")
    
    # Testar estrutura
    if not testar_estrutura():
        logger.error("❌ Falha ao testar estrutura")
        return
    
    # Testar inserção
    if not testar_insercao():
        logger.error("❌ Falha ao testar inserção")
        return
    
    # Testar busca
    if not testar_busca():
        logger.error("❌ Falha ao testar busca")
        return
    
    logger.info("✅ Todos os testes concluídos com sucesso!")

if __name__ == "__main__":
    main() 