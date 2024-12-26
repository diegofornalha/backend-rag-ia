import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from typing import List, Optional
import os
import json
from datetime import datetime
import logging
from models.document import Document
import google.generativeai as genai
from langchain.text_splitter import RecursiveCharacterTextSplitter

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VectorStore:
    """Classe otimizada para gerenciar o índice FAISS e embeddings"""
    def __init__(self, 
                 embedding_model: str = "all-MiniLM-L6-v2",
                 index_path: str = "faiss_index",
                 batch_size: int = 32):
        # Configuração do Gemini
        genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
        self.model = genai.GenerativeModel('gemini-pro')
        
        # Configuração do embedding model
        self.embedding_model = SentenceTransformer(embedding_model)
        self.dimension = self.embedding_model.get_sentence_embedding_dimension()
        self.index_path = index_path
        self.batch_size = batch_size
        
        # Configuração do índice FAISS e documentos
        self.index: Optional[faiss.Index] = None
        self.documents: List[Document] = []
        self.document_map = {}  # Mapa de ID para documento
        self.metadata_index = {}  # Índice invertido para metadados
        
        # Inicialização do índice e documentos
        self._initialize_index()
        
    def _initialize_index(self):
        """Inicializa o índice FAISS com configurações otimizadas"""
        try:
            if os.path.exists(f"{self.index_path}.faiss"):
                logger.info("Carregando índice FAISS existente...")
                self.index = faiss.read_index(f"{self.index_path}.faiss")
                self._load_documents()
            else:
                logger.info("Criando novo índice FAISS...")
                # Usando IVF para melhor performance em grandes datasets
                quantizer = faiss.IndexFlatL2(self.dimension)
                nlist = max(4, int(np.sqrt(1000)))  # número de clusters
                self.index = faiss.IndexIVFFlat(quantizer, self.dimension, nlist)
                
                # Treinamento inicial do índice
                sample_size = max(2 * nlist, 1000)
                samples = np.random.rand(sample_size, self.dimension).astype('float32')
                self.index.train(samples)
                
        except Exception as e:
            logger.error(f"Erro na inicialização do índice: {e}")
            raise
    
    def _load_documents(self) -> None:
        """Carrega documentos do JSON com indexação otimizada"""
        try:
            docs_path = f"{self.index_path}_docs.json"
            metadata_path = f"{self.index_path}_metadata.json"
            
            if os.path.exists(docs_path):
                with open(docs_path, 'r') as f:
                    docs_data = json.load(f)
                
                # Carrega documentos com indexação
                for doc_data in docs_data:
                    doc = Document(
                        content=doc_data['content'],
                        metadata=doc_data['metadata'],
                        embedding_id=doc_data['embedding_id']
                    )
                    self.documents.append(doc)
                    self.document_map[doc.embedding_id] = doc
                    
                    # Indexa metadados para busca rápida
                    for key, value in doc.metadata.items():
                        if isinstance(value, (list, dict)):
                            # Converte listas e dicionários para tuplas imutáveis
                            if isinstance(value, list):
                                values = tuple(value)
                            else:
                                values = tuple(sorted(value.items()))
                        else:
                            values = (str(value),)
                        
                        if key not in self.metadata_index:
                            self.metadata_index[key] = {}
                        
                        for v in values:
                            v_str = str(v)
                            if v_str not in self.metadata_index[key]:
                                self.metadata_index[key][v_str] = set()
                            self.metadata_index[key][v_str].add(doc.embedding_id)
                
                logger.info(f"Carregados {len(self.documents)} documentos com metadados indexados")
            
        except Exception as e:
            logger.error(f"Erro ao carregar documentos: {e}")
            raise
    
    def _save_metadata_index(self, path: str) -> None:
        """Salva índice de metadados em formato otimizado"""
        try:
            # Converte sets para listas para serialização JSON
            serializable_index = {}
            for key, value_map in self.metadata_index.items():
                serializable_index[key] = {
                    str(value): list(doc_ids)
                    for value, doc_ids in value_map.items()
                }
            
            with open(path, 'w') as f:
                json.dump(serializable_index, f, ensure_ascii=False, indent=2)
            
        except Exception as e:
            logger.error(f"Erro ao salvar índice de metadados: {e}")
            raise
    
    def add_documents(self, documents: List[Document]) -> None:
        """Adiciona documentos ao índice de forma otimizada"""
        try:
            if not documents:
                logger.warning("Nenhum documento para adicionar")
                return
            
            logger.info(f"Processando {len(documents)} documentos...")
            
            # Processa embeddings em lotes
            all_embeddings = []
            for i in range(0, len(documents), self.batch_size):
                batch = documents[i:i + self.batch_size]
                texts = [doc.content for doc in batch]
                embeddings = self.embedding_model.encode(texts)
                all_embeddings.extend(embeddings)
            
            # Converte para o formato correto do FAISS
            embeddings_array = np.array(all_embeddings).astype('float32')
            
            # Adiciona ao índice
            start_id = len(self.documents)
            self.index.add(embeddings_array)
            
            # Atualiza documentos e índices
            for i, doc in enumerate(documents):
                doc.embedding_id = start_id + i
                self.documents.append(doc)
                self.document_map[doc.embedding_id] = doc
                
                # Indexa metadados
                for key, value in doc.metadata.items():
                    if key not in self.metadata_index:
                        self.metadata_index[key] = {}
                        
                    # Converte valor para string para garantir que seja hashable
                    value_str = str(value)
                    if value_str not in self.metadata_index[key]:
                        self.metadata_index[key][value_str] = set()
                    self.metadata_index[key][value_str].add(doc.embedding_id)
            
            # Salva o estado atual
            self.save()
            logger.info(f"Adicionados {len(documents)} documentos ao índice")
            
        except Exception as e:
            logger.error(f"Erro ao adicionar documentos: {e}")
            raise
    
    def _is_conversational_query(self, query: str) -> bool:
        """Verifica se a query é conversacional"""
        conversational_patterns = {
            'oi', 'olá', 'ola', 'hi', 'hello', 'bom dia', 'boa tarde', 'boa noite',
            'tudo bem', 'como vai', 'como está', 'obrigado', 'obrigada', 'tchau',
            'até logo', 'falou'
        }
        return (
            query.lower().strip() in conversational_patterns or
            len(query.split()) <= 3  # Queries muito curtas provavelmente são conversacionais
        )

    async def chat_response(self, query: str) -> str:
        """Gera resposta conversacional usando Gemini"""
        try:
            response = await self.model.generate_content_async(
                f"""Você é um assistente amigável e profissional.
                Responda de forma natural e concisa à mensagem do usuário: {query}"""
            )
            return response.text
        except Exception as e:
            logger.error(f"Erro ao gerar resposta com Gemini: {e}")
            return "Desculpe, não consegui processar sua mensagem. Como posso ajudar de outra forma?"

    async def similarity_search(self, query: str, k: int = 4) -> List[Document]:
        """Realiza busca por similaridade com configurações otimizadas"""
        if not self.index or self.index.ntotal == 0:
            return []
        
        try:
            # Verifica se é uma query conversacional
            if self._is_conversational_query(query):
                response = await self.chat_response(query)
                return [Document(
                    content=response,
                    metadata={"type": "conversation"},
                    embedding_id=None
                )]

            # Para queries não conversacionais, faz busca semântica
            query_embedding = self.embedding_model.encode(
                [query],
                normalize_embeddings=True
            ).astype('float32')
            
            if isinstance(self.index, faiss.IndexIVFFlat):
                self.index.nprobe = min(16, self.index.nlist)
            
            # Aumenta o número de resultados iniciais para ter mais opções de deduplicação
            D, I = self.index.search(query_embedding, min(k * 4, self.index.ntotal))
            
            seen_contents = {}  # Dicionário para rastrear similaridade entre conteúdos
            results = []
            
            for idx in I[0]:
                if idx != -1 and idx < len(self.documents):
                    doc = self.documents[idx]
                    content = doc.content.strip()
                    
                    # Verifica similaridade com documentos já vistos
                    is_duplicate = False
                    for seen_content in seen_contents:
                        # Calcula similaridade usando distância de Levenshtein normalizada
                        similarity = 1 - (sum(1 for i, j in zip(content, seen_content) 
                                          if i != j) / max(len(content), len(seen_content)))
                        if similarity > 0.8:  # Threshold de similaridade
                            is_duplicate = True
                            break
                    
                    if not is_duplicate:
                        seen_contents[content] = doc
                        results.append(doc)
                        if len(results) >= k:
                            break
            
            # Se encontrou resultados, usa Gemini para gerar uma resposta contextualizada
            if results:
                # Ordena resultados por relevância e limita o contexto
                context = "\n---\n".join([
                    f"Documento {i+1}:\n{doc.content}" 
                    for i, doc in enumerate(results[:3])  # Limita a 3 documentos mais relevantes
                ])
                
                response = await self.model.generate_content_async(
                    f"""Com base no seguinte contexto, responda à pergunta do usuário de forma natural e concisa.
                    Evite repetir informações e combine o conhecimento dos documentos em uma única resposta coerente.
                    Se a pergunta não estiver relacionada ao contexto, ignore-o.
                    
                    Contexto:
                    {context}
                    
                    Pergunta: {query}
                    
                    Lembre-se:
                    1. Não repita informações
                    2. Combine o conhecimento dos documentos
                    3. Seja conciso e direto
                    4. Mantenha um tom natural de conversa"""
                )
                return [Document(
                    content=response.text,
                    metadata={"type": "contextual_response"},
                    embedding_id=None
                )]
            
            return results
            
        except Exception as e:
            logger.error(f"Erro na busca: {e}")
            return []
    
    def save(self) -> None:
        """Salva o estado atual do índice e documentos"""
        try:
            # Salva o índice FAISS
            faiss.write_index(self.index, f"{self.index_path}.faiss")
            
            # Salva os documentos
            docs_data = []
            for doc in self.documents:
                doc_data = {
                    'content': doc.content,
                    'metadata': doc.metadata,
                    'embedding_id': doc.embedding_id
                }
                docs_data.append(doc_data)
            
            with open(f"{self.index_path}_docs.json", 'w', encoding='utf-8') as f:
                json.dump(docs_data, f, ensure_ascii=False, indent=2)
            
            # Salva o índice de metadados
            self._save_metadata_index(f"{self.index_path}_metadata.json")
            
            logger.info("Estado do vector store salvo com sucesso")
            
        except Exception as e:
            logger.error(f"Erro ao salvar vector store: {e}")
            raise
    
    def filter_by_metadata(self, filters: dict) -> List[Document]:
        """Filtra documentos por metadados usando índice invertido"""
        try:
            result_set = None
            
            for key, value in filters.items():
                if key in self.metadata_index and value in self.metadata_index[key]:
                    doc_ids = self.metadata_index[key][value]
                    if result_set is None:
                        result_set = set(doc_ids)
                    else:
                        result_set &= doc_ids
            
            if result_set:
                return [self.document_map[doc_id] for doc_id in result_set]
            return []
            
        except Exception as e:
            logger.error(f"Erro ao filtrar por metadados: {e}")
            return [] 