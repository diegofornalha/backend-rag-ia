"""Implementação do cluster para ambiente local."""
from datetime import datetime
from typing import Dict, Any, Optional, List
import json
import os
from pathlib import Path
from sentence_transformers import SentenceTransformer
import numpy as np
from .base import BaseCluster
from .utils.messages import MessageTemplate
from .utils.logger import get_logger

logger = get_logger(__name__, rag_debug=True)

class LocalCluster(BaseCluster):
    """Implementação do cluster para ambiente local usando arquivos JSON"""
    
    def __init__(self, settings):
        super().__init__(settings)
        self.model = SentenceTransformer(settings.MODEL_NAME)
        self.data_dir = Path("data")
        self.data_dir.mkdir(exist_ok=True)
        
        # Inicializa arquivos de dados
        self.docs_file = self.data_dir / "documents.json"
        self.embeddings_file = self.data_dir / "embeddings.json"
        self.stats_file = self.data_dir / "statistics.json"
        
        # Cria arquivos se não existirem
        for file in [self.docs_file, self.embeddings_file, self.stats_file]:
            if not file.exists():
                file.write_text("{}")
    
    def _load_json(self, file: Path) -> Dict:
        """Carrega dados de um arquivo JSON"""
        try:
            return json.loads(file.read_text())
        except Exception:
            return {}
    
    def _save_json(self, file: Path, data: Dict) -> None:
        """Salva dados em um arquivo JSON"""
        file.write_text(json.dumps(data, indent=2))
    
    async def get_documents_count(self) -> int:
        """Retorna a contagem de documentos"""
        try:
            docs = self._load_json(self.docs_file)
            return len(docs)
        except Exception as e:
            logger.error(MessageTemplate.DB_QUERY_ERROR.format(
                query="get documents count",
                error=str(e)
            ))
            return 0
    
    async def get_embeddings_count(self) -> int:
        """Retorna a contagem de embeddings"""
        try:
            embeddings = self._load_json(self.embeddings_file)
            return len(embeddings)
        except Exception as e:
            logger.error(MessageTemplate.DB_QUERY_ERROR.format(
                query="get embeddings count",
                error=str(e)
            ))
            return 0
    
    async def get_health_check(self) -> Dict[str, Any]:
        """Retorna informações de saúde do cluster local"""
        try:
            docs_count = await self.get_documents_count()
            embeddings_count = await self.get_embeddings_count()
            stats = self._load_json(self.stats_file)
            
            return {
                "status": "healthy",
                "message": "Sistema local funcionando normalmente",
                "documents_count": docs_count,
                "embeddings_count": embeddings_count,
                "last_update": datetime.now().isoformat(),
                "model_info": {
                    "name": self.settings.MODEL_NAME,
                    "embedding_size": self.model.get_sentence_embedding_dimension()
                }
            }
        except Exception as e:
            logger.error(MessageTemplate.OPERATION_ERROR.format(
                operation="health check",
                reason=str(e)
            ))
            return {
                "status": "unhealthy",
                "message": f"Erro ao verificar saúde do sistema local: {str(e)}",
                "last_update": datetime.now().isoformat()
            }
    
    async def update_documents_count(self) -> Optional[int]:
        """Atualiza a contagem de documentos"""
        try:
            count = await self.get_documents_count()
            stats = self._load_json(self.stats_file)
            
            stats["documents_count"] = count
            stats["updated_at"] = datetime.now().isoformat()
            
            self._save_json(self.stats_file, stats)
            return count
            
        except Exception as e:
            logger.error(MessageTemplate.OPERATION_ERROR.format(
                operation="update documents count",
                reason=str(e)
            ))
            return None
    
    async def create_embeddings(self, document_id: str, text: str) -> Dict[str, Any]:
        """Cria embeddings para um documento"""
        try:
            logger.info(MessageTemplate.CHUNK_PROCESSING.format(doc_id=document_id))
            
            # Gera embedding
            embedding = self.model.encode(text)
            
            # Carrega embeddings existentes
            embeddings = self._load_json(self.embeddings_file)
            
            # Cria novo registro
            embedding_id = str(len(embeddings) + 1)
            embeddings[embedding_id] = {
                "id": embedding_id,
                "document_id": document_id,
                "embedding": embedding.tolist(),
                "text": text,
                "created_at": datetime.now().isoformat()
            }
            
            # Salva embeddings
            self._save_json(self.embeddings_file, embeddings)
            
            logger.info(MessageTemplate.EMBEDDING_SUCCESS.format(doc_id=document_id))
            
            return {
                "id": embedding_id,
                "document_id": document_id,
                "vector_dim": len(embedding)
            }
            
        except Exception as e:
            logger.error(MessageTemplate.EMBEDDING_ERROR.format(
                doc_id=document_id,
                error=str(e)
            ))
            raise
    
    async def search_similar(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Busca documentos similares baseado em uma query"""
        try:
            logger.info(MessageTemplate.QUERY_PROCESSING.format(query_text=query))
            
            # Gera embedding da query
            query_embedding = self.model.encode(query)
            
            # Carrega todos os embeddings
            embeddings = self._load_json(self.embeddings_file)
            
            # Calcula similaridade com todos os documentos
            results = []
            for emb_id, emb_data in embeddings.items():
                doc_embedding = np.array(emb_data["embedding"])
                similarity = np.dot(query_embedding, doc_embedding) / (
                    np.linalg.norm(query_embedding) * np.linalg.norm(doc_embedding)
                )
                
                if similarity >= self.settings.SIMILARITY_THRESHOLD:
                    results.append({
                        "id": emb_id,
                        "document_id": emb_data["document_id"],
                        "text": emb_data["text"],
                        "similarity": float(similarity)
                    })
            
            # Ordena por similaridade e limita resultados
            results.sort(key=lambda x: x["similarity"], reverse=True)
            results = results[:limit]
            
            logger.info(MessageTemplate.QUERY_RESULTS.format(count=len(results)))
            
            return results
            
        except Exception as e:
            logger.error(MessageTemplate.QUERY_ERROR.format(
                query_text=query,
                error=str(e)
            ))
            return []
    
    async def delete_embeddings(self, document_id: str) -> bool:
        """Remove embeddings de um documento"""
        try:
            embeddings = self._load_json(self.embeddings_file)
            
            # Remove embeddings do documento
            embeddings = {
                k: v for k, v in embeddings.items()
                if v["document_id"] != document_id
            }
            
            # Salva alterações
            self._save_json(self.embeddings_file, embeddings)
            
            logger.info(MessageTemplate.OPERATION_SUCCESS.format(
                operation=f"delete embeddings for document {document_id}"
            ))
            return True
            
        except Exception as e:
            logger.error(MessageTemplate.VECTOR_STORE_ERROR.format(
                operation=f"delete embeddings for document {document_id}",
                error=str(e)
            ))
            return False
    
    async def update_embeddings(self, document_id: str, text: str) -> Dict[str, Any]:
        """Atualiza embeddings de um documento"""
        try:
            # Remove embeddings antigos
            await self.delete_embeddings(document_id)
            
            # Cria novos embeddings
            return await self.create_embeddings(document_id, text)
            
        except Exception as e:
            logger.error(MessageTemplate.VECTOR_STORE_ERROR.format(
                operation=f"update embeddings for document {document_id}",
                error=str(e)
            ))
            raise 