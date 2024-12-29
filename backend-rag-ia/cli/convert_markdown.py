#!/usr/bin/env python3

import json
import os
from pathlib import Path
from services.md_converter import MarkdownConverter
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
import asyncio
from supabase import create_client, Client
from dotenv import load_dotenv

console = Console()
load_dotenv()

class MarkdownProcessor:
    def __init__(self):
        self.converter = MarkdownConverter()
        self.supabase = self._get_supabase_client()
    
    def _get_supabase_client(self) -> Client:
        """Inicializa cliente Supabase."""
        url = os.getenv('SUPABASE_URL')
        key = os.getenv('SUPABASE_KEY')
        
        if not url or not key:
            raise ValueError("SUPABASE_URL e SUPABASE_KEY devem ser configurados!")
        
        return create_client(url, key)
    
    async def process_single_file(self, md_file: Path, output_dir: Path = None):
        """Processa um único arquivo markdown."""
        try:
            # Lê o conteúdo do arquivo
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Prepara os metadados
            rule_type = md_file.stem.replace('REGRAS_', '').replace('_RULES', '')
            metadata = {
                "title": md_file.stem,
                "tipo": "regra",
                "autor": "sistema",
                "filename": md_file.name,
                "categorias": ["regras", rule_type.lower()],
                "tags": ["documentação", "regras", rule_type.lower()],
                "versao": "1.0"
            }
            
            # Converte para JSON
            result = self.converter.convert_md_to_json(
                md_content=content,
                metadata=metadata
            )
            
            # Se especificado, salva em arquivo
            if output_dir:
                output_dir = Path(output_dir)
                output_dir.mkdir(parents=True, exist_ok=True)
                json_file = output_dir / f"{md_file.stem.lower()}.json"
                
                with open(json_file, 'w', encoding='utf-8') as f:
                    json.dump(result, f, ensure_ascii=False, indent=2)
                console.print(f"[green]✓ JSON gerado: {json_file.name}")
            
            # Envia para o Supabase
            response = await self.supabase.table("documents").insert(result).execute()
            
            if response.data:
                console.print(f"[green]✓ Enviado para Supabase: {md_file.name}")
                return True
            return False
            
        except Exception as e:
            console.print(f"[red]Erro ao processar {md_file.name}: {str(e)}")
            return False
    
    async def process_directory(self, input_dir: Path, output_dir: Path = None):
        """Processa todos os arquivos markdown de um diretório."""
        md_files = list(input_dir.glob('*.md'))
        total_files = len(md_files)
        
        console.print(f"\n[bold cyan]Encontrados {total_files} arquivos markdown.")
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("Processando...", total=total_files)
            
            for md_file in md_files:
                progress.update(task, description=f"Processando {md_file.name}")
                await self.process_single_file(md_file, output_dir)
                progress.advance(task)

async def main():
    # Define diretórios
    base_dir = Path(__file__).parent.parent
    input_dir = base_dir / 'regras_md'
    output_dir = base_dir / 'regras_json'
    
    if not input_dir.exists():
        console.print("[red]Diretório regras_md não encontrado!")
        return
    
    console.print("[bold]Iniciando processamento dos arquivos markdown...")
    console.print(f"Diretório de entrada: {input_dir}")
    if output_dir:
        console.print(f"Diretório de saída: {output_dir}\n")
    
    processor = MarkdownProcessor()
    
    try:
        await processor.process_directory(input_dir, output_dir)
        console.print("\n[bold green]Processamento concluído!")
        
    except Exception as e:
        console.print(f"[bold red]Erro durante o processamento: {str(e)}")

if __name__ == '__main__':
    asyncio.run(main()) 