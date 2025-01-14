#!/usr/bin/env python3
import argparse
import json
import os
from datetime import datetime
from typing import Dict, Any

from ..embates.models.embate_models import DefaultEmbateContext
from ..embates.processor.content_processor import process_content

async def process_and_save_content(
    content: str,
    output_dir: str,
    metadata: Dict[str, Any] = None
) -> str:
    """
    Processa o conteúdo e salva em um arquivo JSON
    """
    try:
        # Criar contexto do embate
        context = DefaultEmbateContext.create(
            embate_id=f"content-{hash(content)}",
            parameters={
                "model": "default",
                "chunk_size": 1000,
                "overlap": 200,
            },
            metadata=metadata or {}
        )
        
        # Processar conteúdo
        result = await process_content(context, content)
        
        if not result.success:
            print("Erro ao processar conteúdo:", result.errors)
            return None
            
        # Criar nome do arquivo
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"processed_content_{timestamp}.json"
        filepath = os.path.join(output_dir, filename)
        
        # Criar diretório se não existir
        os.makedirs(output_dir, exist_ok=True)
        
        # Salvar resultado
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(result.data, f, indent=2, ensure_ascii=False)
            
        print(f"\nConteúdo processado e salvo em: {filepath}")
        print("\nMetadados do processamento:")
        print(f"- Chunks gerados: {len(result.data['processed_content']['chunks'])}")
        print(f"- Palavras: {result.data['processed_content']['metadata']['word_count']}")
        print(f"- Sentenças: {result.data['processed_content']['metadata']['sentence_count']}")
        
        return filepath
            
    except Exception as e:
        print(f"Erro durante o processamento: {e}")
        return None

def simulate_ragie_upload(filepath: str):
    """
    Simula o upload do arquivo para o Ragie
    """
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = json.load(f)
            
        print("\nSimulando upload para Ragie:")
        print("- Tamanho do arquivo:", os.path.getsize(filepath), "bytes")
        print("- Número de chunks:", len(content["processed_content"]["chunks"]))
        print("- Metadados:", json.dumps(content["processed_content"]["metadata"], indent=2))
        
        print("\nUpload simulado com sucesso!")
        return True
        
    except Exception as e:
        print(f"Erro ao simular upload: {e}")
        return False

async def main():
    parser = argparse.ArgumentParser(description="Processa conteúdo e simula envio para Ragie")
    parser.add_argument("--input", "-i", help="Arquivo de entrada com o conteúdo", required=True)
    parser.add_argument("--output", "-o", help="Diretório de saída", default="processed_files")
    parser.add_argument("--scope", "-s", help="Escopo do documento", default="test")
    parser.add_argument("--type", "-t", help="Tipo do documento", default="text")
    parser.add_argument("--author", "-a", help="Autor do documento")
    
    args = parser.parse_args()
    
    # Ler conteúdo do arquivo
    try:
        with open(args.input, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        print(f"Erro ao ler arquivo de entrada: {e}")
        return
        
    # Preparar metadados
    metadata = {
        "scope": args.scope,
        "tipo": args.type,
        "source": "cli",
    }
    if args.author:
        metadata["autor"] = args.author
        
    # Processar conteúdo
    print(f"\nProcessando arquivo: {args.input}")
    print("Metadados:", json.dumps(metadata, indent=2))
    
    filepath = await process_and_save_content(content, args.output, metadata)
    if not filepath:
        return
        
    # Simular upload
    simulate_ragie_upload(filepath)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main()) 