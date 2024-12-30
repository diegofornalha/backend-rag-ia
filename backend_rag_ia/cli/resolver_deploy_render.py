import os

from dotenv import load_dotenv
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.table import Table
from sentence_transformers import SentenceTransformer
from supabase import create_client

# Carrega variáveis de ambiente
load_dotenv()

console = Console()

# Inicializa Supabase
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")
supabase = create_client(url, key)


def resolver_problema_deploy(
    descricao_problema: str, similaridade_minima: float = 0.3, limite: int = 5
):
    """
    Busca soluções para problemas de deploy no Render.

    Args:
        descricao_problema: Descrição do problema que está enfrentando
        similaridade_minima: Quão similar a solução precisa ser (0.1 a 1.0)
        limite: Número máximo de soluções
    """
    try:
        console.print("\n🔍 Analisando seu problema de deploy no Render...\n")

        # Lista de arquivos essenciais para verificar
        arquivos_essenciais = [
            "render.yaml",
            "Dockerfile",
            "build.sh",
            "requirements.txt",
            ".render-buildpacks.json",
        ]

        # Verifica arquivos locais
        console.print("📋 Checando arquivos essenciais:")
        table = Table()
        table.add_column("Arquivo")
        table.add_column("Status")

        for arquivo in arquivos_essenciais:
            if os.path.exists(arquivo):
                table.add_row(arquivo, "✅ Presente")
            else:
                table.add_row(arquivo, "❌ Faltando")

        console.print(table)
        console.print()

        # Inicializa o modelo de embeddings
        console.print("🤖 Buscando soluções relacionadas...")
        modelo = SentenceTransformer("multi-qa-MiniLM-L6-cos-v1")

        # Gera embedding para a descrição do problema
        embedding_problema = modelo.encode(descricao_problema)

        # Busca soluções similares
        resultado = supabase.rpc(
            "match_documents",
            {
                "query_embedding": embedding_problema.tolist(),
                "match_threshold": similaridade_minima,
                "match_count": limite,
            },
        ).execute()

        solucoes = resultado.data

        if not solucoes:
            console.print("\n❌ Não encontrei soluções específicas para este problema.")
            return

        # Mostra soluções encontradas
        console.print("\n🎯 Soluções Potenciais Encontradas:\n")

        for i, doc in enumerate(solucoes, 1):
            similaridade = doc.get("similarity", 0)
            conteudo = doc.get("content", "")

            panel = Panel(
                Markdown(conteudo),
                title=f"Solução #{i} (Relevância: {similaridade:.1%})",
                border_style="green",
            )
            console.print(panel)
            console.print()

        # Dicas gerais
        console.print("\n💡 Dicas Gerais para Deploy no Render:")
        console.print(
            "1. Certifique-se que todos os arquivos de configuração estão na raiz do projeto"
        )
        console.print("2. Verifique se o render.yaml está configurado corretamente")
        console.print("3. Confirme se todas as dependências estão no requirements.txt")
        console.print("4. Verifique as variáveis de ambiente necessárias")

    except Exception as e:
        console.print(f"\n❌ Erro ao buscar soluções: {e!s}")


def main():
    console.print("\n🚀 Assistente de Deploy Render\n")

    # Solicita descrição do problema
    problema = input("Descreva o problema que está tendo com o deploy: ")
    similaridade = float(input("Nível de relevância das soluções (0.1 a 1.0): "))
    limite = int(input("Quantas soluções você quer ver? "))

    # Busca soluções
    resolver_problema_deploy(problema, similaridade, limite)


if __name__ == "__main__":
    main()
