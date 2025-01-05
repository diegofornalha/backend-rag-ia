"""
Módulo de agentes do sistema multiagente.
"""

from .researcher import ResearcherAgent
from .analyst import AnalystAgent
from .improver import ImproverAgent
from .synthesizer import SynthesizerAgent

__all__ = [
    "ResearcherAgent",
    "AnalystAgent", 
    "ImproverAgent",
    "SynthesizerAgent"
] 