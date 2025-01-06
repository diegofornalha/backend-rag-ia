from typing import Dict, List
from datetime import datetime


class EmbateTemplates:
    @staticmethod
    def create_feature_embate(titulo: str, contexto: str, autor: str) -> Dict:
        """Cria template para embate de nova funcionalidade"""
        return {
            "titulo": titulo,
            "tipo": "feature",
            "contexto": contexto,
            "status": "aberto",
            "data_inicio": datetime.now().isoformat(),
            "argumentos": [
                {
                    "autor": autor,
                    "tipo": "analise",
                    "conteudo": "Análise inicial pendente",
                    "data": datetime.now().isoformat(),
                }
            ],
            "metadata": {"impacto": "médio", "prioridade": "média", "tags": ["feature"]},
        }

    @staticmethod
    def create_bug_embate(
        titulo: str, descricao: str, autor: str, severidade: str = "média"
    ) -> Dict:
        """Cria template para embate de bug"""
        return {
            "titulo": titulo,
            "tipo": "bug",
            "contexto": descricao,
            "status": "aberto",
            "data_inicio": datetime.now().isoformat(),
            "argumentos": [
                {
                    "autor": autor,
                    "tipo": "problema",
                    "conteudo": descricao,
                    "data": datetime.now().isoformat(),
                }
            ],
            "metadata": {
                "impacto": severidade,
                "prioridade": "alta" if severidade == "alta" else "média",
                "tags": ["bug", severidade],
            },
        }

    @staticmethod
    def create_process_embate(titulo: str, contexto: str, autor: str, area: str) -> Dict:
        """Cria template para embate de processo"""
        return {
            "titulo": titulo,
            "tipo": "processo",
            "contexto": contexto,
            "status": "aberto",
            "data_inicio": datetime.now().isoformat(),
            "argumentos": [
                {
                    "autor": autor,
                    "tipo": "analise",
                    "conteudo": f"Análise de processo - Área: {area}",
                    "data": datetime.now().isoformat(),
                }
            ],
            "metadata": {"impacto": "médio", "prioridade": "média", "tags": ["processo", area]},
        }

    @staticmethod
    def create_tech_debt_embate(titulo: str, descricao: str, autor: str, componente: str) -> Dict:
        """Cria template para embate de dívida técnica"""
        return {
            "titulo": titulo,
            "tipo": "tech_debt",
            "contexto": descricao,
            "status": "aberto",
            "data_inicio": datetime.now().isoformat(),
            "argumentos": [
                {
                    "autor": autor,
                    "tipo": "analise",
                    "conteudo": f"Análise de dívida técnica - Componente: {componente}",
                    "data": datetime.now().isoformat(),
                }
            ],
            "metadata": {
                "impacto": "médio",
                "prioridade": "média",
                "tags": ["tech_debt", componente],
            },
        }

    @staticmethod
    def add_argument(embate: Dict, autor: str, tipo: str, conteudo: str) -> Dict:
        """Adiciona novo argumento a um embate existente"""
        if "argumentos" not in embate:
            embate["argumentos"] = []

        embate["argumentos"].append(
            {"autor": autor, "tipo": tipo, "conteudo": conteudo, "data": datetime.now().isoformat()}
        )

        return embate
