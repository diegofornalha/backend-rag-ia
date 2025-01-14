from fastapi import APIRouter, Body, HTTPException
from typing import Dict
from ...services.agent_services.document_upload_agent import DocumentUploadAgent
from backend_rag_ai_py.engine.llms.gemini_config import get_model_config
import json

document_router = APIRouter(prefix="/api/documents")

# Obtém configuração do modelo
config = get_model_config()
api_key = config.get("api_key")

if not api_key:
    raise ValueError("API key do Gemini não encontrada na configuração")

document_agent = DocumentUploadAgent("document_upload", api_key)

@document_router.post("/validate")
async def validate_document(
    content: str = Body(...),
    cliente: str = Body(...),
    question: str | None = Body(None)  # Opcional: pergunta sobre o conteúdo
) -> Dict:
    """
    Valida e processa um documento antes do upload.
    Aceita tanto JSON quanto texto puro.
    
    Args:
        content: Conteúdo do documento (JSON ou texto)
        cliente: Nome do cliente associado ao documento
        question: Opcional - pergunta sobre o conteúdo
        
    Returns:
        Dict com resultado do processamento
    """
    # Se houver uma pergunta, processa como análise
    if question:
        result = await document_agent.process({
            "content": content,
            "cliente": cliente,
            "is_question": True,
            "question": question
        })
        
        if "error" in result:
            return {
                'success': False,
                'message': result["error"]
            }
            
        return {
            'success': True,
            'message': result["response"]
        }

    # Processa o documento
    success, message, result = document_agent.process_upload(content, cliente)
    
    if not success:
        return {
            'success': False,
            'message': document_agent.format_error_message(message)
        }
    
    # Formata a mensagem de retorno
    content_preview = json.dumps(result['content'], indent=2, ensure_ascii=False)
    
    return {
        'success': True,
        'data': result,
        'message': f"""✅ Documento processado com sucesso:

```json
{content_preview}
```

Nome sugerido para o arquivo: "{result['suggested_name']}"

Para confirmar este nome, digite "confirmar".
Para usar um nome diferente, digite o novo nome desejado."""
    } 