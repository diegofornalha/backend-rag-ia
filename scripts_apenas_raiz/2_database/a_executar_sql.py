import os
import logging
from pathlib import Path
from dotenv import load_dotenv
from backend_rag_ia.config.supabase_config import SupabaseConfig

# Configurando logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Carregando variáveis de ambiente
load_dotenv()

def read_sql_file(file_path):
    """Lê o conteúdo de um arquivo SQL."""
    try:
        with open(file_path, 'r') as file:
            return file.read()
    except Exception as e:
        logger.error(f"❌ Erro ao ler arquivo {file_path}: {e}")
        return None

def execute_sql_file(supabase, sql_content, file_name):
    """Executa o conteúdo SQL de um arquivo."""
    try:
        logger.info(f"🔄 Executando {file_name}...")
        
        response = supabase.client.rpc(
            'exec_sql',
            {'sql_query': sql_content}
        ).execute()
        
        if hasattr(response, 'error') and response.error:
            logger.error(f"❌ Erro ao executar {file_name}: {response.error}")
            return False
        else:
            logger.info(f"✅ {file_name} executado com sucesso")
            return True
            
    except Exception as e:
        logger.error(f"❌ Erro ao executar {file_name}: {e}")
        return False

def execute_all_sql():
    """Executa todos os arquivos SQL na ordem correta."""
    try:
        supabase = SupabaseConfig()
        sql_dir = Path('backend_rag_ia/sql')
        
        # Ordem de execução dos arquivos
        files_order = [
            '00_setup_exec_sql.sql',       # Função para executar SQL
            'init.sql',                    # Inicialização básica
            'setup_security.sql',          # Configurações de segurança base
            'setup_embeddings.sql',        # Configuração de embeddings
            'setup_search.sql',            # Configuração de busca
            'setup_maintenance.sql',       # Funções de manutenção
            'setup_metrics.sql',           # Funções de métricas
            'setup_security_all.sql',      # Políticas de segurança completas
            'setup_functions_security.sql' # Segurança das funções
        ]
        
        success_count = 0
        total_files = len(files_order)
        
        for file_name in files_order:
            file_path = sql_dir / file_name
            if not file_path.exists():
                logger.warning(f"⚠️ Arquivo não encontrado: {file_name}")
                continue
                
            sql_content = read_sql_file(file_path)
            if sql_content and execute_sql_file(supabase, sql_content, file_name):
                success_count += 1
                
        logger.info(f"📊 Execução concluída: {success_count}/{total_files} arquivos processados com sucesso")
        
    except Exception as e:
        logger.error(f"❌ Erro ao executar arquivos SQL: {e}")

if __name__ == "__main__":
    execute_all_sql() 