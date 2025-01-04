
from supabase import Client


def buscar_documentos(supabase: Client, query: str, k: int = 5) -> list[dict]:
    """Busca documentos por similaridade textual."""
    try:
        docs = supabase.table("rag.01_base_conhecimento_regras_geral").select("*").textSearch("conteudo", f"%{query}%").limit(k).execute()
        return docs.data if docs.data else []
    except Exception as e:
        print(f"Erro ao buscar documentos: {e}")
        return []

def listar_tabelas(supabase: Client) -> list[str]:
    """Lista todas as tabelas disponíveis."""
    try:
        tables = supabase.table("rag.01_base_conhecimento_regras_geral").select("*").limit(1).execute()
        return [t['table'] for t in tables.data] if tables.data else []
    except Exception as e:
        print(f"Erro ao listar tabelas: {e}")
        return [] 