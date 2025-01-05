"""
Sistema de continuidade automática para o multi-agent.
"""

from typing import Dict, Any, Optional, List, Generator, cast
from dataclasses import dataclass, field
from enum import Enum
import logging
from dotenv import load_dotenv

from gemini.engine.coordinator.multi_agent import MultiAgentSystem
from gemini.engine.continuity.improvements.interfaces import IAgent, AnalysisContext, AnalysisResult, AgentRole

class ContinuationState(Enum):
    """Estados possíveis da continuidade."""
    WAITING = "waiting"
    PROCESSING = "processing"
    COMPLETED = "completed"
    INTERRUPTED = "interrupted"

@dataclass
class ContinuationContext:
    """Contexto da continuidade automática."""
    query: str
    workspace_path: str
    current_file: Optional[str] = None
    open_files: List[str] = field(default_factory=list)
    state: ContinuationState = ContinuationState.WAITING
    last_agent: Optional[str] = None
    iteration: int = 0

class AutoContinuationAgent(IAgent):
    """Agente especializado em continuidade automática."""
    
    def __init__(self):
        load_dotenv()
        self.role = AgentRole.CURSOR_AI
        self.system = MultiAgentSystem()
        self.logger = logging.getLogger(__name__)
        self.context: Optional[ContinuationContext] = None
        
    def start_continuation(self, query: str, workspace_path: str, current_file: Optional[str] = None) -> None:
        """Inicia o processo de continuidade."""
        self.context = ContinuationContext(
            query=query,
            workspace_path=workspace_path,
            current_file=current_file,
            state=ContinuationState.WAITING,
            iteration=0
        )
        
    def analyze(self, context: AnalysisContext) -> AnalysisResult:
        """Analisa o contexto e coordena a continuidade."""
        if not self.context:
            raise ValueError("Continuação não iniciada")
            
        self.context.state = ContinuationState.PROCESSING
        self.context.iteration += 1
        
        # Processa através do sistema multi-agent
        results = self.system.process(context.metadata.get('query', ''))
        
        # Organiza os resultados
        findings = {
            'research': results['research'],
            'criticism': results['criticism'],
            'improvements': results['improved'],
            'synthesis': results['synthesis'],
            'iteration': self.context.iteration
        }
        
        # Gera recomendações e próximos passos
        recommendations = self._extract_recommendations(results['synthesis'])
        next_steps = self._generate_next_steps(findings)
        
        # Gera próxima query baseada nos resultados
        next_query = self._generate_next_query(findings, next_steps)
        if next_query and self.context:
            self.context.query = next_query
        
        self.context.state = ContinuationState.COMPLETED
        
        return AnalysisResult(
            agent_name="AutoContinuation",
            findings=findings,
            recommendations=recommendations + next_steps,
            priority=1,
            metadata={
                'role': self.role.value,
                'state': self.context.state.value,
                'iteration': self.context.iteration,
                'next_query': next_query
            }
        )
    
    def process_message(self, message: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Processa mensagens e mantém a continuidade."""
        if not self.context:
            return None
            
        if message.get('type') == 'interrupt':
            self.context.state = ContinuationState.INTERRUPTED
            return {'status': 'interrupted'}
            
        if message.get('type') == 'query':
            context = AnalysisContext(
                project_path=self.context.workspace_path,
                files=[self.context.current_file] if self.context.current_file else [],
                config={},
                metadata={'query': message['content']}
            )
            result = self.analyze(context)
            
            # Prepara próxima continuação automaticamente
            self.context.state = ContinuationState.WAITING
            
            return {
                'type': 'response',
                'content': result.findings['synthesis'],
                'details': result.findings,
                'next_steps': result.recommendations,
                'next_query': result.metadata.get('next_query'),
                'iteration': self.context.iteration
            }
        
        return None
    
    def get_capabilities(self) -> List[str]:
        """Retorna as capacidades do agente."""
        return ['auto_continuation', 'query_processing', 'multi_agent_coordination']
    
    def _extract_recommendations(self, synthesis: str) -> List[str]:
        """Extrai recomendações da síntese."""
        recommendations: List[str] = []
        
        for line in synthesis.split('\n'):
            if any(keyword in line.lower() for keyword in ['sugestão', 'recomendação', 'proposta', 'próximo passo']):
                recommendations.append(line.strip())
        
        return recommendations
    
    def _generate_next_steps(self, findings: Dict[str, Any]) -> List[str]:
        """Gera próximos passos baseados nos findings."""
        next_steps: List[str] = []
        
        # Analisa críticas para gerar melhorias
        if 'criticism' in findings:
            criticisms = findings['criticism'].split('\n')
            for criticism in criticisms:
                if criticism.strip():
                    next_steps.append(f"Resolver: {criticism.strip()}")
        
        # Analisa melhorias sugeridas
        if 'improvements' in findings:
            improvements = findings['improvements'].split('\n')
            for improvement in improvements:
                if improvement.strip():
                    next_steps.append(f"Implementar: {improvement.strip()}")
        
        return next_steps
    
    def _generate_next_query(self, findings: Dict[str, Any], next_steps: List[str]) -> Optional[str]:
        """Gera a próxima query baseada nos resultados atuais."""
        if not next_steps:
            return "Analise o projeto em busca de novas oportunidades de melhoria"
            
        # Pega o próximo passo mais relevante
        next_step = next_steps[0]
        
        # Gera query baseada no tipo do próximo passo
        if next_step.startswith("Resolver:"):
            return f"Como resolver o problema: {next_step[9:]}"
        elif next_step.startswith("Implementar:"):
            return f"Como implementar a melhoria: {next_step[12:]}"
        else:
            return f"Como proceder com: {next_step}"

def start_auto_continuation(query: str, workspace_path: str, current_file: Optional[str] = None) -> Generator[Dict[str, Any], None, None]:
    """
    Inicia o processo de continuidade automática.
    
    Args:
        query: A pergunta ou instrução do usuário
        workspace_path: Caminho do workspace atual
        current_file: Arquivo atual aberto (opcional)
    
    Yields:
        Dict com os resultados do processamento e próximos passos
    """
    agent = AutoContinuationAgent()
    agent.start_continuation(query, workspace_path, current_file)
    
    while True:
        if not agent.context:
            break
            
        context = AnalysisContext(
            project_path=workspace_path,
            files=[current_file] if current_file else [],
            config={},
            metadata={'query': agent.context.query}
        )
        
        try:
            result = agent.analyze(context)
            
            response = {
                'response': result.findings['synthesis'],
                'details': {
                    'research': result.findings['research'],
                    'analysis': result.findings['criticism'],
                    'improvements': result.findings['improvements']
                },
                'next_steps': result.recommendations,
                'state': agent.context.state.value if agent.context else None,
                'iteration': result.findings.get('iteration', 0),
                'next_query': result.metadata.get('next_query')
            }
            
            yield response
            
            # Atualiza query para próxima iteração
            next_query = cast(Optional[str], response.get('next_query'))
            if next_query and agent.context:
                agent.context.query = next_query
            
        except Exception as e:
            agent.logger.error(f"Erro na iteração {agent.context.iteration if agent.context else 0}: {str(e)}")
            # Continua mesmo com erro, tentando uma nova abordagem
            if agent.context:
                agent.context.query = "Analise o projeto em busca de novas oportunidades de melhoria" 