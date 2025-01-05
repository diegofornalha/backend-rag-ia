"""
Coordenador central do sistema multi-agente.
"""

from typing import Dict, Any, List
from ..llm_services.providers.gemini import GeminiProvider
from ..embedding_services.vector_store import VectorStore

class AgentCoordinator:
    def __init__(
        self,
        llm_provider: GeminiProvider,
        vector_store: VectorStore
    ):
        self.llm = llm_provider
        self.vector_store = vector_store

    async def process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        task_type = task.get("type", "analysis")
        
        if task_type == "analysis":
            return await self._process_analysis(task)
        elif task_type == "suggestion":
            return await self._process_suggestion(task)
        else:
            raise ValueError(f"Tipo de tarefa desconhecido: {task_type}")

    async def _process_analysis(self, task: Dict[str, Any]) -> Dict[str, Any]:
        content = task["content"]
        embeddings = task.get("embeddings")
        
        # Se não tiver embeddings, gerar e armazenar
        if not embeddings:
            embeddings = await self.vector_store.store_content(content)
        
        # Buscar conteúdo similar para contexto
        similar_content = await self.vector_store.search_similar(content)
        
        # Preparar prompt com contexto
        prompt = f"""
        Analise o seguinte conteúdo e forneça insights relevantes.
        
        Conteúdo principal:
        {content}
        
        Conteúdo similar encontrado:
        {[item['content'] for item in similar_content]}
        
        Por favor, forneça:
        1. Principais temas e conceitos
        2. Relações com o conteúdo similar
        3. Insights e recomendações
        """
        
        # Gerar análise
        response = await self.llm.generate_content(prompt)
        
        return {
            "analysis": response,
            "similar_content": similar_content,
            "embeddings": embeddings
        }

    async def _process_suggestion(self, task: Dict[str, Any]) -> Dict[str, Any]:
        query = task["query"]
        similar_content = task.get("similar_content") or await self.vector_store.search_similar(query)
        
        # Preparar prompt
        prompt = f"""
        Com base na seguinte consulta e conteúdo similar encontrado, gere sugestões relevantes.
        
        Consulta:
        {query}
        
        Conteúdo similar:
        {[item['content'] for item in similar_content]}
        
        Por favor, forneça:
        1. Sugestões diretas relacionadas à consulta
        2. Insights baseados no conteúdo similar
        3. Possíveis próximos passos
        """
        
        # Gerar sugestões
        response = await self.llm.generate_content(prompt)
        
        return {
            "suggestions": response,
            "similar_content": similar_content
        } 