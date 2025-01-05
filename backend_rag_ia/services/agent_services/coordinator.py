"""
Coordenador central do sistema multi-agente.
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass
import logging

from ..agents import (
    ResearcherAgent,
    AnalystAgent, 
    ImproverAgent,
    SynthesizerAgent,
    AgentContext,
    AgentResult
)
from ..infrastructure.config import Config

@dataclass
class CoordinationResult:
    """Resultado da coordenação multi-agente."""
    research: AgentResult
    analysis: AgentResult
    improvements: AgentResult
    synthesis: AgentResult
    metadata: Dict[str, Any]

class MultiAgentCoordinator:
    """Coordena a interação entre os agentes do sistema."""
    
    def __init__(self):
        """Inicializa o coordenador com os agentes necessários."""
        self.config = Config()
        self.logger = logging.getLogger(__name__)
        
        # Inicializa os agentes
        self.researcher = ResearcherAgent()
        self.analyst = AnalystAgent()
        self.improver = ImproverAgent()
        self.synthesizer = SynthesizerAgent()
        
        # Estado interno
        self._current_context: Optional[AgentContext] = None
        self._results_cache: Dict[str, AgentResult] = {}
        
    def process_topic(self, topic: str, context_data: Dict[str, Any] = None) -> CoordinationResult:
        """Processa um tópico através do pipeline multi-agente."""
        self.logger.info(f"Iniciando processamento do tópico: {topic}")
        
        # Prepara o contexto
        context = AgentContext(
            topic=topic,
            data=context_data or {},
            metadata={
                'config': self.config.to_dict(),
                'timestamp': self._get_timestamp()
            }
        )
        self._current_context = context
        
        try:
            # 1. Pesquisa
            research_result = self._execute_research(context)
            self._results_cache['research'] = research_result
            
            # 2. Análise
            analysis_context = self._prepare_analysis_context(context, research_result)
            analysis_result = self._execute_analysis(analysis_context)
            self._results_cache['analysis'] = analysis_result
            
            # 3. Melhorias
            improvement_context = self._prepare_improvement_context(
                context, research_result, analysis_result
            )
            improvement_result = self._execute_improvements(improvement_context)
            self._results_cache['improvements'] = improvement_result
            
            # 4. Síntese
            synthesis_context = self._prepare_synthesis_context(
                context, research_result, analysis_result, improvement_result
            )
            synthesis_result = self._execute_synthesis(synthesis_context)
            self._results_cache['synthesis'] = synthesis_result
            
            # Prepara o resultado final
            result = CoordinationResult(
                research=research_result,
                analysis=analysis_result,
                improvements=improvement_result,
                synthesis=synthesis_result,
                metadata={
                    'topic': topic,
                    'context': context.metadata,
                    'status': 'success'
                }
            )
            
            self.logger.info(f"Processamento do tópico concluído: {topic}")
            return result
            
        except Exception as e:
            self.logger.error(f"Erro no processamento do tópico {topic}: {str(e)}")
            raise
            
    def _execute_research(self, context: AgentContext) -> AgentResult:
        """Executa a fase de pesquisa."""
        self.logger.debug("Iniciando fase de pesquisa")
        return self.researcher.process(context)
    
    def _execute_analysis(self, context: AgentContext) -> AgentResult:
        """Executa a fase de análise."""
        self.logger.debug("Iniciando fase de análise")
        return self.analyst.process(context)
    
    def _execute_improvements(self, context: AgentContext) -> AgentResult:
        """Executa a fase de melhorias."""
        self.logger.debug("Iniciando fase de melhorias")
        return self.improver.process(context)
    
    def _execute_synthesis(self, context: AgentContext) -> AgentResult:
        """Executa a fase de síntese."""
        self.logger.debug("Iniciando fase de síntese")
        return self.synthesizer.process(context)
    
    def _prepare_analysis_context(
        self, 
        base_context: AgentContext,
        research_result: AgentResult
    ) -> AgentContext:
        """Prepara o contexto para a fase de análise."""
        return AgentContext(
            topic=base_context.topic,
            data={
                'content': research_result.findings.get('main_topics', []),
                'evidence': research_result.findings.get('evidence', []),
                'original_context': base_context.data
            },
            metadata={
                **base_context.metadata,
                'previous_stage': 'research'
            }
        )
    
    def _prepare_improvement_context(
        self,
        base_context: AgentContext,
        research_result: AgentResult,
        analysis_result: AgentResult
    ) -> AgentContext:
        """Prepara o contexto para a fase de melhorias."""
        return AgentContext(
            topic=base_context.topic,
            data={
                'content': research_result.findings.get('main_topics', []),
                'criticism': analysis_result.findings.get('weaknesses', []),
                'original_context': base_context.data
            },
            metadata={
                **base_context.metadata,
                'previous_stage': 'analysis'
            }
        )
    
    def _prepare_synthesis_context(
        self,
        base_context: AgentContext,
        research_result: AgentResult,
        analysis_result: AgentResult,
        improvement_result: AgentResult
    ) -> AgentContext:
        """Prepara o contexto para a fase de síntese."""
        return AgentContext(
            topic=base_context.topic,
            data={
                'research': research_result.findings,
                'criticism': analysis_result.findings,
                'improvements': improvement_result.findings,
                'original_context': base_context.data
            },
            metadata={
                **base_context.metadata,
                'previous_stage': 'improvement'
            }
        )
    
    def _get_timestamp(self) -> str:
        """Retorna o timestamp atual."""
        from datetime import datetime
        return datetime.now().isoformat()
    
    def get_agent_capabilities(self) -> Dict[str, List[str]]:
        """Retorna as capacidades de todos os agentes."""
        return {
            'researcher': self.researcher.get_capabilities(),
            'analyst': self.analyst.get_capabilities(),
            'improver': self.improver.get_capabilities(),
            'synthesizer': self.synthesizer.get_capabilities()
        }
    
    def get_last_result(self, stage: str) -> Optional[AgentResult]:
        """Retorna o último resultado de um estágio específico."""
        return self._results_cache.get(stage) 