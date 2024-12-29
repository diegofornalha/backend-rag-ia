import json
from typing import List
from datetime import datetime
from models.document import Document
import os

def load_document_file(file_path: str) -> Document:
    """Carrega um documento individual de um arquivo JSON"""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
            
        metadata_global = {
            **data['metadata_global'],
            "timestamp": datetime.now().isoformat()
        }
        
        doc_data = data['document']
        document = Document(
            content=doc_data['content'],
            metadata={
                **metadata_global,
                **doc_data['metadata']
            }
        )
        return document
    except Exception as e:
        print(f"Erro ao carregar {file_path}: {str(e)}")
        return None

def load_knowledge_base(vector_store):
    """Carrega documentos da base de conhecimento"""
    try:
        documents = []
        documents_dir = "documents"
        
        # Lista todos os arquivos JSON no diretório
        for filename in os.listdir(documents_dir):
            if filename.endswith('.json'):
                print(f"Carregando {filename}...")
                file_path = os.path.join(documents_dir, filename)
                
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                    # Processa o formato específico do documento
                    if 'document' in data and 'content' in data['document']:
                        # Combina os metadados globais com os específicos do documento
                        metadata = {
                            'source': filename,
                            'type': 'knowledge_base'
                        }
                        
                        # Adiciona metadados globais se existirem
                        if 'metadata_global' in data:
                            metadata.update(data['metadata_global'])
                            
                        # Adiciona metadados específicos do documento se existirem
                        if 'metadata' in data['document']:
                            metadata.update(data['document']['metadata'])
                            
                        doc = Document(
                            content=data['document']['content'],
                            metadata=metadata
                        )
                        documents.append(doc)
                        print(f"Documento {filename} processado com sucesso")
        
        if documents:
            print(f"Adicionando {len(documents)} documentos ao vector store...")
            vector_store.add_documents(documents)
            print(f"Carregados {len(documents)} documentos na base de conhecimento")
        else:
            print("Nenhum documento encontrado para carregar")
            
    except Exception as e:
        print(f"Erro ao carregar documentos: {e}")
        raise 