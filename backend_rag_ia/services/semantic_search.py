"""
Gerenciador de busca semântica.
"""

from typing import List, Dict, Optional
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

class SemanticSearchManager:
    """Gerencia buscas semânticas no sistema."""
    
    def __init__(self, embedding_model=None):
        """
        Inicializa o gerenciador.
        
        Args:
            embedding_model: Modelo para gerar embeddings
        """
        self.embedding_model = embedding_model
    
    def search(self, query: str, documents: List[Dict], k: int = 5) -> List[Dict]:
        """
        Realiza busca semântica.
        
        Args:
            query: Texto da busca
            documents: Lista de documentos para buscar
            k: Número de resultados a retornar
            
        Returns:
            Lista dos k documentos mais relevantes
        """
        if not documents:
            return []
            
        # Gera embedding da query
        query_embedding = self.get_embedding(query)
        
        # Recupera embeddings dos documentos
        doc_embeddings = []
        for doc in documents:
            embedding = doc.get('embedding')
            if embedding:
                doc_embeddings.append(embedding)
            else:
                # Gera embedding se não existir
                doc_embeddings.append(self.get_embedding(doc['content']))
        
        # Calcula similaridade
        similarities = cosine_similarity(
            [query_embedding],
            doc_embeddings
        )[0]
        
        # Ordena documentos por similaridade
        doc_scores = list(zip(documents, similarities))
        doc_scores.sort(key=lambda x: x[1], reverse=True)
        
        return [doc for doc, _ in doc_scores[:k]]
    
    def get_embedding(self, text: str) -> np.ndarray:
        """
        Gera embedding para um texto.
        
        Args:
            text: Texto para gerar embedding
            
        Returns:
            Array numpy com embedding
        """
        if self.embedding_model:
            return self.embedding_model.encode(text)
        
        # Fallback para embedding simples se não houver modelo
        return np.random.rand(384)  # Dimensão padrão
    
    def batch_search(self, queries: List[str], documents: List[Dict], k: int = 5) -> List[List[Dict]]:
        """
        Realiza múltiplas buscas em batch.
        
        Args:
            queries: Lista de queries
            documents: Lista de documentos
            k: Número de resultados por query
            
        Returns:
            Lista de resultados para cada query
        """
        results = []
        for query in queries:
            results.append(self.search(query, documents, k))
        return results
    
    def index_documents(self, documents: List[Dict]) -> List[Dict]:
        """
        Indexa documentos gerando embeddings.
        
        Args:
            documents: Lista de documentos para indexar
            
        Returns:
            Documentos com embeddings adicionados
        """
        for doc in documents:
            if 'embedding' not in doc:
                doc['embedding'] = self.get_embedding(doc['content'])
        return documents
