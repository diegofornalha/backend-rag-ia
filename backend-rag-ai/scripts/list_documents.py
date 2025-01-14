import os
from ragie import Ragie
from rich.console import Console
from rich.table import Table

# Configurar a chave da API
api_key = os.getenv("NEXT_PUBLIC_RAGIE_API_KEY")
ragie = Ragie(api_key)

# Criar uma tabela bonita
console = Console()
table = Table(show_header=True, header_style="bold magenta")
table.add_column("ID", style="dim")
table.add_column("Nome")
table.add_column("Status")
table.add_column("Criado em")
table.add_column("Atualizado em")
table.add_column("Chunks")
table.add_column("Metadata")

# Buscar e mostrar os documentos
documents = ragie.documents.list()
for doc in documents.result.documents:
    table.add_row(
        str(doc.id),
        doc.name,
        doc.status,
        doc.created_at.strftime("%Y-%m-%d %H:%M:%S"),
        doc.updated_at.strftime("%Y-%m-%d %H:%M:%S"),
        str(doc.chunk_count),
        str(doc.metadata)
    )

console.print(table) 