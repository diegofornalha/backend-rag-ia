"""
API principal do sistema.

Este módulo configura e inicializa a API FastAPI com:
- Rotas para documentos
- Rotas para busca semântica
- Rotas para estatísticas
- Rotas para cache distribuído
- Documentação interativa
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routes import documents_router, search_router, statistics_router, health_router, cache_router

# Configuração da API
app = FastAPI(
    title="Backend RAG IA",
    description="""
    API para busca semântica em documentos usando RAG (Retrieval Augmented Generation).
    
    ## Funcionalidades
    
    ### Documentos
    - Upload de documentos (PDF, TXT, DOC)
    - Listagem e busca de documentos
    - Atualização e remoção de documentos
    
    ### Busca Semântica
    - Busca por similaridade semântica
    - Busca com filtros avançados
    - Recomendação de documentos similares
    
    ### Estatísticas
    - Métricas de uso do sistema
    - Análise de performance
    - Histórico de operações
    
    ### Cache Distribuído
    - Cache com Redis
    - Métricas de performance
    - Monitoramento de saúde
    
    ## Autenticação
    
    A API usa autenticação via token JWT. Para usar a API:
    1. Obtenha um token de acesso
    2. Inclua o token no header Authorization
    
    ## Exemplos
    
    ### Python
    ```python
    import requests
    
    # Configuração
    BASE_URL = "http://localhost:10000"
    headers = {"Authorization": "Bearer seu-token"}
    
    # Upload de documento
    files = {"file": open("documento.pdf", "rb")}
    response = requests.post(f"{BASE_URL}/documents", files=files, headers=headers)
    
    # Busca semântica
    query = "como usar python para análise de dados"
    response = requests.get(
        f"{BASE_URL}/search",
        params={"query": query},
        headers=headers
    )
    
    # Estatísticas
    response = requests.get(f"{BASE_URL}/statistics/system", headers=headers)
    ```
    
    ### Curl
    ```bash
    # Upload de documento
    curl -X POST "http://localhost:10000/documents" \
         -H "Authorization: Bearer seu-token" \
         -F "file=@documento.pdf"
    
    # Busca semântica
    curl "http://localhost:10000/search?query=python" \
         -H "Authorization: Bearer seu-token"
    
    # Estatísticas
    curl "http://localhost:10000/statistics/system" \
         -H "Authorization: Bearer seu-token"
    ```
    
    ## Suporte
    
    Para dúvidas e suporte:
    - Email: suporte@exemplo.com
    - Documentação: https://docs.exemplo.com
    - GitHub: https://github.com/exemplo/backend-rag-ia
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_tags=[
        {
            "name": "Documentos",
            "description": "Operações com documentos: upload, listagem, busca, atualização e remoção"
        },
        {
            "name": "Busca",
            "description": "Operações de busca semântica e recomendação de documentos similares"
        },
        {
            "name": "Estatísticas",
            "description": "Métricas de uso, performance e histórico do sistema"
        },
        {
            "name": "Cache",
            "description": "Operações com cache distribuído: métricas e monitoramento"
        }
    ]
)

# Configuração de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registro das rotas
app.include_router(documents_router)
app.include_router(search_router)
app.include_router(statistics_router)
app.include_router(health_router)
app.include_router(cache_router)

@app.get("/", tags=["Root"])
async def root():
    """
    Rota raiz da API.
    
    Retorna informações básicas sobre a API e links úteis.
    """
    return {
        "name": "Backend RAG IA",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc",
        "status": "online"
    } 