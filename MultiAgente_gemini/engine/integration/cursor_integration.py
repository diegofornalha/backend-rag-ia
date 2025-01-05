"""
Integração do sistema multi-agent com o Cursor.
"""

from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from dotenv import load_dotenv

from gemini.engine.coordinator.multi_agent import MultiAgentSystem
from gemini.engine.continuity.improvements.interfaces import IAgent, AnalysisContext, AnalysisResult, AgentRole

@dataclass
class CursorContext:
    """Contexto da interação com o Cursor."""
    query: str
    workspace_path: str
    current_file: Optional[str] = None
    open_files: List[str] = field(default_factory=list)
    cursor_position: Optional[Dict[str, int]] = None

class CursorAgent(IAgent):
    """Agente especializado em integração com o Cursor."""
    
    def __init__(self):
        load_dotenv()
        self.role = AgentRole.CURSOR_AI
        self.system = MultiAgentSystem()
        
    def analyze(self, context: AnalysisContext) -> AnalysisResult:
        """Analisa o contexto do Cursor e coordena os outros agentes."""
        # Processa a query através do sistema multi-agent
        results = self.system.process(context.metadata.get('query', ''))
        
        # Organiza os resultados
        findings = {
            'research': results['research'],
            'criticism': results['criticism'],
            'improvements': results['improved'],
            'synthesis': results['synthesis']
        }
        
        # Gera recomendações baseadas na síntese
        recommendations = self._extract_recommendations(results['synthesis'])
        
        return AnalysisResult(
            agent_name="CursorAI",
            findings=findings,
            recommendations=recommendations,
            priority=1,
            metadata={'role': self.role.value}
        )
    
    def process_message(self, message: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Processa mensagens do Cursor."""
        if 'type' not in message:
            return None
            
        if message['type'] == 'query':
            context = AnalysisContext(
                project_path=message.get('workspace_path', ''),
                files=message.get('open_files', []),
                config={},
                metadata={'query': message['content']}
            )
            result = self.analyze(context)
            return {
                'type': 'response',
                'content': result.findings['synthesis'],
                'details': result.findings
            }
        
        return None
    
    def get_capabilities(self) -> List[str]:
        """Retorna as capacidades do agente."""
        return ['cursor_integration', 'query_processing', 'multi_agent_coordination']
    
    def _extract_recommendations(self, synthesis: str) -> List[str]:
        """Extrai recomendações da síntese."""
        # Aqui você pode implementar uma lógica mais sofisticada para extrair
        # recomendações do texto da síntese
        recommendations: List[str] = []
        
        # Exemplo simples: divide por linhas e procura por sugestões
        for line in synthesis.split('\n'):
            if any(keyword in line.lower() for keyword in ['sugestão', 'recomendação', 'proposta']):
                recommendations.append(line.strip())
        
        return recommendations

def process_cursor_query(query: str, workspace_path: str, current_file: Optional[str] = None) -> Dict[str, Any]:
    """
    Processa uma query do Cursor usando o sistema multi-agent.
    
    Args:
        query: A pergunta ou instrução do usuário
        workspace_path: Caminho do workspace atual
        current_file: Arquivo atual aberto (opcional)
    
    Returns:
        Dict com os resultados do processamento
    """
    context = CursorContext(
        query=query,
        workspace_path=workspace_path,
        current_file=current_file
    )
    
    agent = CursorAgent()
    analysis_context = AnalysisContext(
        project_path=context.workspace_path,
        files=[context.current_file] if context.current_file else [],
        config={},
        metadata={'query': context.query}
    )
    
    result = agent.analyze(analysis_context)
    
    return {
        'response': result.findings['synthesis'],
        'details': {
            'research': result.findings['research'],
            'analysis': result.findings['criticism'],
            'improvements': result.findings['improvements']
        },
        'recommendations': result.recommendations
    } 