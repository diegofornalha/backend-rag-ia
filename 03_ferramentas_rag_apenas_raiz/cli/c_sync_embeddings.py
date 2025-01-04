#!/usr/bin/env python3
import os
import sys
import json
import asyncio
import logging
from datetime import datetime
from typing import List, Dict, Any
import httpx
from dotenv import load_dotenv
from supabase import create_client, Client

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Carregar variáveis de ambiente
load_dotenv()
supabase_url = os.getenv('SUPABASE_URL')
supabase_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')

if not all([supabase_url, supabase_key]):
    logger.error("❌ Credenciais do Supabase não encontradas no .env")
    sys.exit(1)

# Inicializar cliente Supabase
supabase: Client = create_client(supabase_url, supabase_key)

async def call_coflow_api(text: str) -> List[float]:
    """Gerar embedding via API do CoFlow."""
    url = 'https://api.coflow.com.br/api/v1/embeddings'
    headers = {'Content-Type': 'application/json'}
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                url,
                json={'text': text},
                headers=headers,
                timeout=30.0
            )
            response.raise_for_status()
            return response.json()['embedding']
    except Exception as e:
        logger.error(f"Erro ao gerar embedding: {str(e)}")
        raise

async def check_missing_embeddings() -> List[Dict[str, Any]]:
    """Identificar documentos sem embedding."""
    try:
        # Usar função no schema public que acessa as tabelas do schema rag
        result = supabase.rpc('get_documents_without_embeddings', {}).execute()
        if result.data:
            logger.info(f"Documentos encontrados sem embeddings: {len(result.data)}")
            for doc in result.data[:5]:  # Mostrar os 5 primeiros como exemplo
                logger.info(f"  - Documento {doc['id']}: {doc.get('titulo', 'Sem título')}")
        return result.data
    except Exception as e:
        logger.error(f"Erro ao verificar documentos sem embedding: {str(e)}")
        raise

async def save_embedding(
    document_id: str,
    embedding: List[float],
    content_hash: str
) -> None:
    """Salvar embedding no Supabase."""
    try:
        current_time = datetime.now().isoformat()
        params = {
            'p_document_id': document_id,
            'p_embedding': embedding,
            'p_content_hash': content_hash,
            'p_created_at': current_time,
            'p_updated_at': current_time
        }
        supabase.rpc('save_document_embedding', params).execute()
        logger.info(f"✅ Embedding salvo para documento {document_id}")
    except Exception as e:
        logger.error(f"❌ Erro ao salvar embedding: {str(e)}")
        raise

async def process_document(doc: Dict[str, Any]) -> None:
    """Processar um único documento."""
    try:
        # Extrair texto do documento
        text = doc['conteudo'].get('text', '')
        if not text:
            logger.warning(f"⚠️ Documento {doc['id']} sem texto")
            return

        # Gerar e salvar embedding
        logger.info(f"🔄 Gerando embedding para documento {doc['id']}")
        embedding = await call_coflow_api(text)
        await save_embedding(doc['id'], embedding, doc['content_hash'])
        
    except Exception as e:
        logger.error(f"❌ Erro ao processar documento {doc['id']}: {str(e)}")
        # Registrar erro no documento
        params = {
            'p_document_id': doc['id'],
            'p_error_log': str(e),
            'p_updated_at': datetime.now().isoformat()
        }
        supabase.rpc('update_document_error', params).execute()

async def sync_embeddings() -> None:
    """Sincronizar embeddings para todos os documentos pendentes."""
    try:
        # Identificar documentos sem embedding
        docs = await check_missing_embeddings()
        total_docs = len(docs)
        logger.info(f"📊 Total de {total_docs} documentos para processar")

        if total_docs == 0:
            logger.info("✨ Nenhum documento pendente para processamento")
            return

        # Processar documentos em lotes
        batch_size = 5  # Reduzido para melhor controle
        for i in range(0, total_docs, batch_size):
            batch = docs[i:i + batch_size]
            logger.info(f"\n🔄 Processando lote {i//batch_size + 1} de {(total_docs + batch_size - 1)//batch_size}")
            await asyncio.gather(
                *[process_document(doc) for doc in batch]
            )
            # Rate limiting mais conservador
            if i + batch_size < total_docs:
                logger.info("⏳ Aguardando 2 segundos antes do próximo lote...")
                await asyncio.sleep(2)

    except Exception as e:
        logger.error(f"❌ Erro durante sincronização: {str(e)}")
        raise

async def show_documents_status() -> None:
    """Mostrar status atual dos documentos."""
    try:
        result = supabase.rpc('count_documents', {}).execute()
        stats = result.data[0]
        logger.info("\n📊 Status dos documentos:")
        logger.info(f"  📚 Total de documentos: {stats['total_documents']}")
        logger.info(f"  ✅ Com embeddings: {stats['documents_with_embeddings']}")
        logger.info(f"  ⏳ Sem embeddings: {stats['documents_without_embeddings']}")
    except Exception as e:
        logger.error(f"❌ Erro ao verificar status dos documentos: {str(e)}")
        raise

async def main():
    """Função principal."""
    try:
        logger.info("Iniciando sincronização de embeddings")
        
        # Mostrar status inicial
        logger.info("Status inicial:")
        await show_documents_status()
        
        # Sincronizar embeddings
        await sync_embeddings()
        
        # Mostrar status final
        logger.info("\nStatus final:")
        await show_documents_status()
        
        logger.info("Sincronização concluída com sucesso")
    except Exception as e:
        logger.error(f"Erro na sincronização: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main()) 