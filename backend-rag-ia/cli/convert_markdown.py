#!/usr/bin/env python3

import os
import sys
import json
from pathlib import Path
from rich.console import Console
from dotenv import load_dotenv

# Adiciona o diretório raiz ao PYTHONPATH
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from services.md_converter import MarkdownConverter

console = Console()
load_dotenv()

def convert_markdown_files():
    """Converte todos os arquivos markdown para JSON."""
    try:
        # Diretórios
        md_dir = project_root / "regras_md"
        json_dir = project_root / "regras_json"
        
        # Verifica se os diretórios existem
        if not md_dir.exists():
            console.print(f"❌ Diretório {md_dir} não encontrado!")
            return
            
        # Cria diretório JSON se não existir
        json_dir.mkdir(exist_ok=True)
        
        # Lista todos os arquivos markdown
        md_files = list(md_dir.glob("*.md"))
        console.print(f"\n📝 Encontrados {len(md_files)} arquivos markdown para conversão.")
        
        # Converte cada arquivo
        converter = MarkdownConverter()
        for md_file in md_files:
            try:
                # Nome do arquivo JSON correspondente
                json_file = json_dir / f"{md_file.stem.lower()}.json"
                
                console.print(f"\n🔄 Convertendo {md_file.name}...")
                
                # Lê o conteúdo do arquivo markdown
                with open(md_file, 'r', encoding='utf-8') as f:
                    markdown_content = f.read()
                
                # Converte para o formato JSON
                result = converter.convert_md_to_json(
                    md_content=markdown_content,
                    metadata={
                        "title": md_file.stem,
                        "tipo": "regra",
                        "autor": "sistema",
                        "filename": md_file.name,
                        "categorias": ["regras"],
                        "tags": ["documentação", "regras"],
                        "versao": "1.0"
                    }
                )
                
                # Salva o resultado
                with open(json_file, 'w', encoding='utf-8') as f:
                    json.dump(result, f, ensure_ascii=False, indent=2)
                    
                console.print(f"✅ Arquivo {json_file.name} criado com sucesso!")
                
            except Exception as e:
                console.print(f"❌ Erro ao converter {md_file.name}: {e}")
                continue
        
        console.print("\n✨ Conversão concluída!")
        
    except Exception as e:
        console.print(f"❌ Erro durante a conversão: {e}")

if __name__ == "__main__":
    convert_markdown_files() 