from backend_rag_ia.config.supabase_config import SupabaseConfig
import hashlib
import json
import logging
from datetime import datetime
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def converter_md_para_json(arquivo_md: Path) -> dict:
    """Converte um arquivo markdown para formato JSON."""
    with open(arquivo_md, 'r', encoding='utf-8') as f:
        conteudo = f.read()
    
    # Extrai título do arquivo (primeira linha H1)
    linhas = conteudo.split('\n')
    titulo = linhas[0].replace('# ', '') if linhas[0].startswith('# ') else arquivo_md.stem
    
    return {
        'titulo': titulo,
        'conteudo': conteudo,
        'metadata': {
            'fonte': 'regras_md',
            'tipo': 'markdown',
            'arquivo_original': arquivo_md.name
        }
    }

def gerar_hash(conteudo: str) -> str:
    """Gera um hash SHA-256 do conteúdo."""
    return hashlib.sha256(conteudo.encode()).hexdigest()

def upload_documento(supabase, documento: dict) -> bool:
    """Faz upload de um documento para o Supabase."""
    try:
        # Gera hash do conteúdo
        document_hash = gerar_hash(documento['conteudo'])
        
        # Verifica se já existe documento com mesmo hash
        response = supabase.table('base_conhecimento_regras_geral') \
            .select('document_hash') \
            .eq('document_hash', document_hash) \
            .execute()
            
        if len(response.data) > 0:
            logger.warning(f'Documento com hash {document_hash} já existe!')
            return False
            
        # Insere novo documento
        response = supabase.table('base_conhecimento_regras_geral').insert({
            'titulo': documento['titulo'],
            'conteudo': documento['conteudo'],
            'metadata': documento['metadata'],
            'document_hash': document_hash,
            'created_at': datetime.utcnow().isoformat(),
            'updated_at': datetime.utcnow().isoformat()
        }).execute()
        
        logger.info(f'Documento inserido com sucesso! Hash: {document_hash}')
        return True
        
    except Exception as e:
        logger.error(f'Erro ao inserir documento: {str(e)}')
        return False

def main():
    # Inicializa conexão
    supabase = SupabaseConfig().client
    
    # Pasta com os arquivos markdown
    pasta_regras = Path('backend_rag_ia/regras_md')
    
    # Lista todos os arquivos .md
    arquivos_md = list(pasta_regras.glob('*.md'))
    logger.info(f'Encontrados {len(arquivos_md)} arquivos markdown')
    
    # Tenta fazer upload de cada arquivo
    for arquivo in arquivos_md:
        logger.info(f'\nProcessando {arquivo.name}...')
        
        # Converte MD para JSON
        documento = converter_md_para_json(arquivo)
        
        # Faz upload
        sucesso = upload_documento(supabase, documento)
        
        if sucesso:
            logger.info(f'✅ Upload de {arquivo.name} concluído com sucesso')
        else:
            logger.warning(f'⚠️ Upload de {arquivo.name} falhou ou arquivo já existe')

if __name__ == '__main__':
    main() 