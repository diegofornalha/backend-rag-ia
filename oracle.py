from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Dict
import google.generativeai as genai
import os
from dotenv import load_dotenv
import logging

# Configuração de logs
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Carrega variáveis de ambiente
load_dotenv()

# Configura a chave da API do Gemini
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
if not GEMINI_API_KEY:
    raise ValueError('GEMINI_API_KEY não encontrada nas variáveis de ambiente')

genai.configure(api_key=GEMINI_API_KEY)

# Configura o modelo
model = genai.GenerativeModel('gemini-1.0-pro')

# Cria a aplicação FastAPI com metadados
app = FastAPI(
    title="Oráculo API",
    description="""
    API do Oráculo que utiliza o modelo Gemini 1.0 Pro para gerar respostas inteligentes.
    
    ## Funcionalidades
    
    * Processamento de mensagens em linguagem natural
    * Geração de respostas contextualizadas
    * Integração com o modelo Gemini 1.0 Pro
    
    ## Como usar
    
    1. Envie uma mensagem através do endpoint `/api/chat`
    2. Receba a resposta gerada pelo modelo
    """,
    version="1.0.0",
    contact={
        "name": "Asimov Academy",
        "url": "https://asimov.academy/",
    },
)

# Lista de origens permitidas
ALLOWED_ORIGINS = [
    "http://localhost:3000",    # Frontend React
    "http://localhost:5173",    # Frontend Vite
    "http://127.0.0.1:3000",   # Frontend React alternativo
    "http://127.0.0.1:5173",   # Frontend Vite alternativo
    "https://oraculo-asimov.vercel.app",  # Produção
    "*"  # Temporariamente permitindo todas as origens para teste
]

# Configura CORS com todas as opções necessárias
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permite todas as origens temporariamente
    allow_credentials=False,  # Desabilita credentials
    allow_methods=["*"],  # Permite todos os métodos
    allow_headers=["*"],  # Permite todos os headers
    expose_headers=["*"],  # Expõe todos os headers
    max_age=3600,  # Cache das respostas OPTIONS por 1 hora
)

class ChatRequest(BaseModel):
    message: str = Field(
        ...,
        description="Mensagem do usuário para o modelo",
        example="Qual é a diferença entre machine learning e deep learning?",
        min_length=1
    )

    class Config:
        json_schema_extra = {
            "example": {
                "message": "Qual é a diferença entre machine learning e deep learning?"
            }
        }

class ChatResponse(BaseModel):
    response: str = Field(
        ...,
        description="Resposta gerada pelo modelo",
        example="Machine Learning é um subcampo da Inteligência Artificial que permite que sistemas aprendam com dados, enquanto Deep Learning é uma técnica específica de Machine Learning que utiliza redes neurais profundas para aprendizado."
    )

    class Config:
        json_schema_extra = {
            "example": {
                "response": "Machine Learning é um subcampo da Inteligência Artificial que permite que sistemas aprendam com dados, enquanto Deep Learning é uma técnica específica de Machine Learning que utiliza redes neurais profundas para aprendizado."
            }
        }

class ErrorResponse(BaseModel):
    detail: str = Field(
        ...,
        description="Descrição detalhada do erro",
        example="Não foi possível gerar uma resposta"
    )

@app.post(
    "/api/chat",
    response_model=ChatResponse,
    responses={
        200: {
            "description": "Resposta gerada com sucesso",
            "model": ChatResponse,
        },
        500: {
            "description": "Erro interno do servidor",
            "model": ErrorResponse,
        },
    },
    tags=["Chat"],
    summary="Gera uma resposta para a mensagem do usuário",
    description="""
    Endpoint que recebe uma mensagem do usuário e retorna uma resposta gerada pelo modelo Gemini 1.0 Pro.
    
    A mensagem deve conter pelo menos 1 caractere.
    """,
)
async def chat(request: ChatRequest) -> ChatResponse:
    try:
        logger.info(f"Recebida mensagem: {request.message}")
        
        # Gera resposta usando o modelo Gemini
        response = model.generate_content(request.message)
        
        # Verifica se a resposta foi gerada com sucesso
        if not response.text:
            logger.error("Resposta vazia do modelo")
            raise HTTPException(
                status_code=500,
                detail="Não foi possível gerar uma resposta"
            )
        
        logger.info("Resposta gerada com sucesso")
        return ChatResponse(response=response.text)
        
    except Exception as e:
        logger.error(f"Erro ao processar mensagem: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao processar mensagem: {str(e)}"
        )

@app.get("/health")
async def health_check():
    """Endpoint para verificar a saúde da API"""
    return {"status": "healthy", "model": "gemini-1.0-pro"}

@app.options("/api/chat")
async def chat_options():
    """Endpoint para lidar com requisições OPTIONS"""
    return {"message": "OK"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=int(os.getenv("PORT", "8000")),
        log_level="info"
    ) 