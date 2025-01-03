"""Verificador de configurações."""

import os
from pathlib import Path
from typing import Dict, List, Optional
import json

from .refactoring_metrics import ConfigAnalyzer, ConfigMetrics

class ConfigChecker:
    """Verifica e corrige configurações."""
    
    def __init__(self, project_root: Optional[Path] = None):
        self.project_root = project_root or Path.cwd()
        self.config_analyzer = ConfigAnalyzer()
        
    def check_env_config(self, env_dict: Dict) -> Dict[str, str]:
        """Verifica configurações de ambiente."""
        campos_obrigatorios = [
            "SUPABASE_KEY",
            "SUPABASE_URL",
            "API_VERSION",
            "GEMINI_API_KEY"
        ]
        
        metricas = self.config_analyzer.analyze_config(env_dict, campos_obrigatorios)
        
        recomendacoes = []
        
        # Verifica campos faltantes
        if metricas.campos_faltantes:
            recomendacoes.append(
                f"Campos obrigatórios faltando: {', '.join(metricas.campos_faltantes)}"
            )
            recomendacoes.append(
                "Adicione estes campos ao arquivo .env ou configure as variáveis de ambiente"
            )
            
        # Verifica campos inválidos
        if metricas.campos_invalidos:
            recomendacoes.append(
                f"Campos com valores inválidos: {', '.join(metricas.campos_invalidos)}"
            )
            recomendacoes.append(
                "Verifique se os valores estão configurados corretamente"
            )
            
        # Verifica campos opcionais
        if metricas.campos_opcionais:
            recomendacoes.append(
                f"Campos opcionais encontrados: {', '.join(metricas.campos_opcionais)}"
            )
            
        return {
            "status": "erro" if metricas.campos_faltantes or metricas.campos_invalidos else "ok",
            "recomendacoes": recomendacoes
        }
        
    def fix_env_config(self, env_dict: Dict) -> Dict:
        """Tenta corrigir configurações de ambiente."""
        # Verifica se existe arquivo .env
        env_file = self.project_root / ".env"
        env_example = self.project_root / ".env.example"
        
        if not env_file.exists() and env_example.exists():
            # Copia .env.example para .env
            with open(env_example) as f:
                env_content = f.read()
            with open(env_file, "w") as f:
                f.write(env_content)
                
        # Carrega valores do .env se existir
        if env_file.exists():
            with open(env_file) as f:
                for line in f:
                    if "=" in line:
                        key, value = line.strip().split("=", 1)
                        if key not in env_dict or not env_dict[key]:
                            env_dict[key] = value
                            
        return env_dict 