import os
from dotenv import load_dotenv
from supabase import create_client
import logging
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def verificar_documentos():
    try:
        # Carrega variáveis de ambiente
        load_dotenv()
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_KEY")
        
        if not supabase_url or not supabase_key:
            logger.error("❌ Variáveis SUPABASE_URL ou SUPABASE_KEY não encontradas")
            return
            
        # Conecta ao Supabase
        supabase = create_client(supabase_url, supabase_key)
        
        # Verifica documentos
        logger.info("📊 Verificando documentos...")
        
        # Consulta direta
        docs = supabase.table("documents").select("*").execute()
        logger.info(f"📝 Total de documentos (select *): {len(docs.data)}")
        
        # Consulta com count
        count = supabase.table("documents").select("*", count="exact").execute()
        logger.info(f"📝 Contagem exata: {count.count}")
        
        # Verifica embeddings
        embeddings = supabase.table("embeddings").select("*").execute()
        logger.info(f"🔤 Total de embeddings: {len(embeddings.data)}")
        
        # Verifica joins
        joined = supabase.table("documents")\
            .select("documents.id, documents.content, embeddings.id")\
            .join("embeddings", "documents.id=embeddings.document_id")\
            .execute()
        logger.info(f"🔗 Documentos com embeddings: {len(joined.data)}")
        
        return {
            "documentos": len(docs.data),
            "embeddings": len(embeddings.data),
            "documentos_com_embeddings": len(joined.data)
        }
            
    except Exception as e:
        logger.error(f"❌ Erro ao verificar documentos: {str(e)}")
        return None

async def reindex_documents(supabase):
    """Recria os embeddings para todos os documentos."""
    try:
        from sentence_transformers import SentenceTransformer
        model = SentenceTransformer("all-MiniLM-L6-v2")
        
        # Busca todos os documentos
        documents = supabase.table("documents").select("*").execute()
        logger.info(f"🔄 Reindexando {len(documents.data)} documentos...")
        
        for doc in documents.data:
            # Gera novo embedding
            embedding = model.encode(doc["content"]).tolist()
            
            # Atualiza embedding
            supabase.table("embeddings")\
                .upsert({
                    "document_id": doc["id"],
                    "embedding": embedding
                })\
                .execute()
            
            logger.info(f"✅ Documento {doc['id']} reindexado")
            
        return True
    except Exception as e:
        logger.error(f"❌ Erro ao reindexar documentos: {str(e)}")
        return False

if __name__ == "__main__":
    while True:
        resultados = verificar_documentos()
        if resultados:
            print("\n📊 Resumo:")
            print(f"- Documentos totais: {resultados['documentos']}")
            print(f"- Embeddings totais: {resultados['embeddings']}")
            print(f"- Docs com embeddings: {resultados['documentos_com_embeddings']}")
            
            # Se houver discrepância, tenta reindexar
            if resultados['documentos'] != resultados['embeddings']:
                print("\n⚠️ Discrepância encontrada! Iniciando reindexação...")
                reindex_documents()
        
        print("\n⏳ Verificando novamente em 10 segundos...")
        time.sleep(10) 