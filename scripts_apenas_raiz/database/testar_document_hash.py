from backend_rag_ia.config.supabase_config import SupabaseConfig
import hashlib
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def gerar_hash(conteudo: str) -> str:
    """Gera um hash SHA-256 do conteúdo."""
    return hashlib.sha256(conteudo.encode()).hexdigest()

def testar_insercao_documento(supabase, titulo: str, conteudo: str) -> bool:
    """Tenta inserir um documento e retorna True se sucesso, False se duplicata."""
    try:
        # Gera hash do conteúdo
        document_hash = gerar_hash(conteudo)
        
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
            'titulo': titulo,
            'conteudo': conteudo,
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
    
    # Teste 1: Inserir documento original
    doc1 = {
        'titulo': 'Teste Hash 1',
        'conteudo': 'Este é um documento de teste para verificar hash.'
    }
    
    logger.info('Teste 1: Inserindo documento original...')
    resultado1 = testar_insercao_documento(supabase, doc1['titulo'], doc1['conteudo'])
    
    # Teste 2: Tentar inserir documento idêntico
    logger.info('Teste 2: Tentando inserir documento idêntico...')
    resultado2 = testar_insercao_documento(supabase, doc1['titulo'], doc1['conteudo'])
    
    # Teste 3: Inserir documento com conteúdo diferente
    doc2 = {
        'titulo': 'Teste Hash 2',
        'conteudo': 'Este é um documento diferente para teste.'
    }
    
    logger.info('Teste 3: Inserindo documento diferente...')
    resultado3 = testar_insercao_documento(supabase, doc2['titulo'], doc2['conteudo'])
    
    # Resultados
    logger.info('\nResultados dos testes:')
    logger.info(f'Teste 1 (Original): {"Sucesso" if resultado1 else "Falha"}')
    logger.info(f'Teste 2 (Duplicata): {"Falha (esperado)" if not resultado2 else "Sucesso (inesperado)"}')
    logger.info(f'Teste 3 (Diferente): {"Sucesso" if resultado3 else "Falha"}')

if __name__ == '__main__':
    main() 