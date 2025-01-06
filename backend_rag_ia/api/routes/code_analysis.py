"""
Rotas para análise de código usando o sistema multiagente.
"""

from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from backend_rag_ia.services.llm_manager import LLMManager

router = APIRouter()


class CodeAnalysisRequest(BaseModel):
    """Modelo para requisição de análise de código."""

    code: str
    language: str
    context: Dict[str, Any] = {}


class CodeAnalysisResponse(BaseModel):
    """Modelo para resposta da análise de código."""

    analysis: Dict[str, Any]
    recommendations: list[str]
    metrics: Dict[str, Any]


@router.post("/analyze", response_model=CodeAnalysisResponse)
async def analyze_code(
    request: CodeAnalysisRequest, llm_manager: LLMManager = Depends()
) -> Dict[str, Any]:
    """
    Analisa código usando o sistema multiagente.

    O sistema irá:
    1. Analisar o código fornecido
    2. Gerar recomendações
    3. Fornecer métricas do processo
    """
    try:
        # Prepara o contexto para análise
        analysis_context = {"code": request.code, "language": request.language, **request.context}

        # Processa com o sistema multiagente
        result = await llm_manager.process_task(task="code_analysis", context=analysis_context)

        # Extrai informações relevantes
        analysis_data = result.get("results", [])
        if not analysis_data:
            raise HTTPException(status_code=500, detail="Nenhuma análise foi gerada")

        # Formata resposta
        response = {
            "analysis": {
                "findings": result["metadata"]["initial_analysis"]["findings"],
                "code_quality": analysis_data[0].get("analysis", {}),
                "security_issues": analysis_data[1].get("analysis", {})
                if len(analysis_data) > 1
                else {},
            },
            "recommendations": result["metadata"]["initial_analysis"]["recommendations"],
            "metrics": {
                "agents_used": result["metadata"]["agents_used"],
                "processing_status": result["status"],
            },
        }

        return response

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro na análise: {str(e)}")


@router.post("/improve")
async def improve_code(
    request: CodeAnalysisRequest, llm_manager: LLMManager = Depends()
) -> Dict[str, Any]:
    """
    Gera sugestões de melhorias para o código.

    O sistema irá:
    1. Analisar o código atual
    2. Gerar sugestões de melhorias
    3. Fornecer exemplos de implementação
    """
    try:
        # Prepara prompt para geração
        improvement_prompt = f"""
        Analise este código {request.language} e sugira melhorias:
        
        ```{request.language}
        {request.code}
        ```
        
        Por favor, forneça:
        1. Sugestões de otimização
        2. Melhorias de legibilidade
        3. Boas práticas aplicáveis
        4. Exemplos de implementação
        """

        # Gera sugestões
        result = await llm_manager.generate_response(
            prompt=improvement_prompt, context=request.context
        )

        return {
            "status": "success",
            "improvements": result["response"],
            "metadata": result["metadata"],
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao gerar melhorias: {str(e)}")
