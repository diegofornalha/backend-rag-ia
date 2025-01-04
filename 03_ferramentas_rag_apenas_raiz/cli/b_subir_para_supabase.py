#!/usr/bin/env python3
"""
Script para subir dados para o Supabase.
"""

import asyncio
import hashlib
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List
import httpx
from supabase import create_client, Client
from dotenv import load_dotenv
import os

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def load_env_variables() -> Dict[str, str]:
    """Carrega variáveis de ambiente necessárias."""
    load_dotenv()
    
    required_vars = ['SUPABASE_URL', 'SUPABASE_SERVICE_ROLE_KEY']
    env_vars = {}
    
    for var in required_vars:
        value = os.getenv(var)
        if not value:
            raise ValueError(f"Variável de ambiente {var} não encontrada")
        env_vars[var] = value
    
    return env_vars

def calculate_hash(content: str) -> str:
    """Calcula o hash do conteúdo."""
    return hashlib.sha256(content.encode()).hexdigest()

def read_markdown_files(base_path: str) -> List[Dict[str, Any]]:
    """Lê todos os arquivos markdown recursivamente."""
    documents = []
    base_path = Path(base_path)
    
    for md_file in base_path.rglob("*.md"):
        try:
            content = md_file.read_text(encoding='utf-8')
            relative_path = md_file.relative_to(base_path)
            
            # Extrair título do nome do arquivo ou primeira linha
            title = md_file.stem
            if content.strip().startswith('#'):
                title = content.strip().split('\n')[0].lstrip('#').strip()
            
            doc = {
                'version_key': str(relative_path),
                'titulo': title,
                'conteudo': {
                    'text': content,
                    'path': str(relative_path)
                },
                'content_hash': calculate_hash(content),
                'document_hash': calculate_hash(str(relative_path)),
                'metadata': {
                    'file_path': str(relative_path),
                    'file_name': md_file.name,
                    'file_size': md_file.stat().st_size
                }
            }
            documents.append(doc)
            logger.info(f"Arquivo processado: {relative_path}")
        except Exception as e:
            logger.error(f"Erro ao processar {md_file}: {str(e)}")
    
    return documents

async def generate_embedding(text: str) -> List[float]:
    """Gera embedding usando a API publicada."""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                'https://api.coflow.com.br/api/v1/embeddings',
                json={'text': text},
                headers={'Content-Type': 'application/json'},
                timeout=30.0
            )
            response.raise_for_status()
            data = response.json()
            return data['embedding']
    except Exception as e:
        logger.error(f"Erro ao gerar embedding: {str(e)}")
        if isinstance(e, httpx.HTTPError):
            logger.error(f"HTTP Status: {e.response.status_code}")
            logger.error(f"Response: {e.response.text}")
        return []

async def upload_to_supabase(documents: List[Dict[str, Any]]) -> None:
    """Faz upload dos documentos para o Supabase."""
    try:
        env_vars = load_env_variables()
        supabase: Client = create_client(
            env_vars['SUPABASE_URL'],
            env_vars['SUPABASE_SERVICE_ROLE_KEY']
        )
        
        for doc in documents:
            current_time = datetime.utcnow().isoformat()
            
            # Gerar embedding para o conteúdo
            embedding = await generate_embedding(doc['conteudo']['text'])
            
            # Preparar documento com todos os campos necessários
            document_data = {
                'version_key': doc['version_key'],
                'titulo': doc['titulo'],
                'conteudo': doc['conteudo'],
                'error_log': None,
                'created_at': current_time,
                'updated_at': current_time,
                'processing_status': 'pending',
                'content_hash': doc['content_hash'],
                'last_embedding_update': None,
                'embedding_attempts': 0,
                'metadata': doc['metadata'],
                'document_hash': doc['document_hash']
            }
            
            try:
                # Inserir documento na tabela principal
                result = supabase.table('rag.01').insert(document_data).execute()
                
                if not result.data:
                    raise Exception("Nenhum dado retornado após inserção do documento")
                
                document_id = result.data[0]['id']
                
                # Se temos um embedding válido, inserir na tabela de embeddings
                if embedding:
                    embedding_data = {
                        'document_id': document_id,
                        'embedding': embedding,
                        'content_hash': doc['content_hash'],
                        'processing_status': 'completed',
                        'last_embedding_update': current_time
                    }
                    
                    embedding_result = supabase.table('rag.02_embeddings_regras_geral').insert(embedding_data).execute()
                    logger.info(f"Embedding gerado e inserido para documento '{doc['titulo']}'")
                
                logger.info(f"Documento '{doc['titulo']}' inserido com sucesso")
            except Exception as e:
                logger.error(f"Erro ao inserir documento '{doc['titulo']}': {str(e)}")
                logger.error(f"Detalhes do erro: {repr(e)}")
                logger.error(f"Dados do documento: {json.dumps(document_data, indent=2)}")
                continue
    
    except Exception as err:
        logger.error(f"Erro no upload: {str(err)}")
        raise

async def main():
    """Função principal."""
    try:
        # Ler documentos do diretório de regras
        documents = read_markdown_files("01_regras_md_apenas_raiz")
        logger.info(f"Total de documentos encontrados: {len(documents)}")
        
        # Fazer upload para o Supabase
        await upload_to_supabase(documents)
        logger.info("Processo de upload concluído com sucesso")
    
    except Exception as e:
        logger.error(f"Erro durante o processo: {str(e)}")
        raise

if __name__ == "__main__":
    asyncio.run(main())