import os
from supabase import create_client
from rich.console import Console
from rich.table import Table
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()

console = Console()

# Inicializa Supabase
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")
supabase = create_client(url, key)

def buscar_documentos(texto_busca: str, similaridade_minima: float = 0.5, limite: int = 5):
    """
    Realiza busca semântica nos documentos usando embeddings.
    
    Args:
        texto_busca: O que você quer encontrar
        similaridade_minima: Quão similar o documento precisa ser (0.1 a 1.0)
        limite: Quantos resultados retornar
    """
    try:
        # Inicializa o modelo de embeddings
        console.print("\n🤖 Carregando modelo de embeddings...")
        modelo = SentenceTransformer('multi-qa-MiniLM-L6-cos-v1')
        
        # Gera embedding para o texto da busca
        console.print("🔄 Gerando embedding para busca...")
        embedding_busca = modelo.encode(texto_busca)
        
        # Faz a busca no Supabase usando a função match_documents
        console.print("🔍 Buscando documentos similares...")
        resultado = supabase.rpc(
            'match_documents',
            {
                'query_embedding': embedding_busca.tolist(),
                'match_threshold': similaridade_minima,
                'match_count': limite
            }
        ).execute()

        documentos = resultado.data

        if not documentos:
            console.print("\n❌ Nenhum documento similar encontrado.")
            return

        # Mostra resultados em uma tabela bonita
        table = Table(title=f"\n📚 Documentos Similares a: '{texto_busca}'")
        table.add_column("Similaridade", justify="center", style="cyan")
        table.add_column("Conteúdo", style="green")
        table.add_column("ID", justify="right", style="magenta")

        for doc in documentos:
            similaridade = doc.get('similarity', 0)
            conteudo = doc.get('content', '')
            # Limita tamanho do conteúdo para melhor visualização
            conteudo_resumido = conteudo[:100] + '...' if len(conteudo) > 100 else conteudo
            doc_id = doc.get('id', '')
            
            table.add_row(
                f"{similaridade:.1%}",
                conteudo_resumido,
                str(doc_id)
            )

        console.print(table)
        console.print(f"\n✨ Encontrados {len(documentos)} documentos similares!")

    except Exception as e:
        console.print(f"\n❌ Erro durante a busca: {str(e)}")

def main():
    console.print("\n🔍 Sistema de Busca Semântica com Embeddings\n")
    
    # Solicita parâmetros da busca
    texto = input("O que você quer encontrar? ")
    similaridade = float(input("Similaridade mínima (0.1 a 1.0): "))
    limite = int(input("Número máximo de resultados: "))
    
    # Realiza a busca
    buscar_documentos(texto, similaridade, limite)

if __name__ == "__main__":
    main() 