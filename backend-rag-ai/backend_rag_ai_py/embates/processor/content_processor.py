import re
from typing import List, Dict, Any
from ..models.embate_models import DefaultEmbateContext, DefaultEmbateResult

def split_into_chunks(text: str, chunk_size: int, overlap: int) -> List[str]:
    """Divide o texto em chunks com sobreposição"""
    chunks = []
    start = 0
    text_length = len(text)
    
    while start < text_length:
        end = start + chunk_size
        chunk = text[start:end]
        
        # Ajustar para não cortar palavras
        if end < text_length:
            last_space = chunk.rfind(" ")
            if last_space != -1:
                end = start + last_space
                chunk = text[start:end]
        
        chunks.append(chunk.strip())
        start = end - overlap
        
    return chunks

def clean_text(text: str) -> str:
    """Limpa e normaliza o texto"""
    # Remover caracteres especiais mantendo pontuação básica
    text = re.sub(r'[^\w\s.,!?-]', '', text)
    # Normalizar espaços
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def extract_metadata(text: str) -> Dict[str, Any]:
    """Extrai metadados do texto"""
    word_count = len(text.split())
    sentence_count = len(re.split(r'[.!?]+', text))
    
    return {
        "word_count": word_count,
        "sentence_count": sentence_count,
        "avg_words_per_sentence": word_count / max(sentence_count, 1),
        "text_length": len(text)
    }

async def process_content(context: DefaultEmbateContext, content: str) -> DefaultEmbateResult:
    """Processa o conteúdo para preparar para embeddings"""
    try:
        # Parâmetros do processamento
        chunk_size = context.parameters.get("chunk_size", 1000)
        overlap = context.parameters.get("overlap", 200)
        
        # Limpar texto
        cleaned_content = clean_text(content)
        
        # Dividir em chunks
        chunks = split_into_chunks(cleaned_content, chunk_size, overlap)
        
        # Extrair metadados
        metadata = extract_metadata(cleaned_content)
        
        # Preparar resultado
        processed_content = {
            "original_text": content,
            "cleaned_text": cleaned_content,
            "chunks": chunks,
            "metadata": {
                **metadata,
                **context.metadata
            }
        }
        
        return DefaultEmbateResult.success_result(
            embate_id=context.embate_id,
            data={"processed_content": processed_content},
            metrics={
                "chunk_count": len(chunks),
                "avg_chunk_size": sum(len(c) for c in chunks) / len(chunks)
            }
        )
        
    except Exception as e:
        return DefaultEmbateResult.error_result(
            embate_id=context.embate_id,
            error=e
        ) 