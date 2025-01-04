from typing import Dict, List, Any, Optional
from datetime import datetime
import json
import logging
from jsonschema import validate, ValidationError, Draft7Validator

logger = logging.getLogger(__name__)

class SchemaValidator:
    """Validador central de schemas para garantir consistência dos dados"""
    
    # Schema base para campos comuns
    BASE_SCHEMA = {
        "type": "object",
        "required": ["titulo", "tipo", "status", "data_inicio", "argumentos", "metadata"],
        "properties": {
            "titulo": {"type": "string", "minLength": 1},
            "tipo": {
                "type": "string",
                "enum": ["feature", "bug", "processo", "tech_debt"]
            },
            "status": {
                "type": "string",
                "enum": ["aberto", "em_andamento", "bloqueado", "fechado"]
            },
            "data_inicio": {
                "type": "string",
                "format": "date-time"
            },
            "argumentos": {
                "type": "array",
                "items": {
                    "type": "object",
                    "required": ["autor", "tipo", "conteudo", "data"],
                    "properties": {
                        "autor": {"type": "string", "minLength": 1},
                        "tipo": {
                            "type": "string",
                            "enum": ["analise", "solucao", "implementacao", "validacao"]
                        },
                        "conteudo": {"type": "string", "minLength": 1},
                        "data": {
                            "type": "string",
                            "format": "date-time"
                        }
                    }
                },
                "minItems": 1
            },
            "metadata": {
                "type": "object",
                "required": ["impacto", "prioridade", "tags"],
                "properties": {
                    "impacto": {
                        "type": "string",
                        "enum": ["baixo", "médio", "alto"]
                    },
                    "prioridade": {
                        "type": "string",
                        "enum": ["baixa", "média", "alta"]
                    },
                    "tags": {
                        "type": "array",
                        "items": {"type": "string"},
                        "minItems": 1
                    }
                }
            }
        }
    }
    
    # Schemas específicos por tipo
    FEATURE_SCHEMA = {
        "type": "object",
        "required": ["contexto"],
        "properties": {
            "contexto": {"type": "string", "minLength": 1}
        }
    }
    
    BUG_SCHEMA = {
        "type": "object",
        "required": ["descricao", "severidade"],
        "properties": {
            "descricao": {"type": "string", "minLength": 1},
            "severidade": {
                "type": "string",
                "enum": ["baixa", "média", "alta"]
            }
        }
    }
    
    PROCESSO_SCHEMA = {
        "type": "object",
        "required": ["contexto", "area"],
        "properties": {
            "contexto": {"type": "string", "minLength": 1},
            "area": {"type": "string", "minLength": 1}
        }
    }
    
    TECH_DEBT_SCHEMA = {
        "type": "object",
        "required": ["descricao", "componente"],
        "properties": {
            "descricao": {"type": "string", "minLength": 1},
            "componente": {"type": "string", "minLength": 1}
        }
    }
    
    @staticmethod
    def validate_date_format(date_str: str) -> bool:
        """Valida se uma string está no formato ISO8601"""
        try:
            datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            return True
        except ValueError:
            return False
    
    @staticmethod
    def validate_embate(embate: Dict) -> List[str]:
        """
        Valida um embate completo
        
        Args:
            embate: Dicionário com dados do embate
            
        Returns:
            Lista de erros encontrados (vazia se não houver erros)
        """
        errors = []
        
        try:
            # Valida schema base
            validate(instance=embate, schema=SchemaValidator.BASE_SCHEMA)
            
            # Valida schema específico do tipo
            tipo = embate.get('tipo')
            if tipo == 'feature':
                validate(instance=embate, schema=SchemaValidator.FEATURE_SCHEMA)
            elif tipo == 'bug':
                validate(instance=embate, schema=SchemaValidator.BUG_SCHEMA)
            elif tipo == 'processo':
                validate(instance=embate, schema=SchemaValidator.PROCESSO_SCHEMA)
            elif tipo == 'tech_debt':
                validate(instance=embate, schema=SchemaValidator.TECH_DEBT_SCHEMA)
            
            # Valida datas
            if not SchemaValidator.validate_date_format(embate['data_inicio']):
                errors.append(f"Data de início inválida: {embate['data_inicio']}")
            
            for arg in embate['argumentos']:
                if not SchemaValidator.validate_date_format(arg['data']):
                    errors.append(f"Data de argumento inválida: {arg['data']}")
            
        except ValidationError as e:
            errors.append(str(e))
        
        return errors
    
    @staticmethod
    def validate_json_file(file_path: str) -> List[str]:
        """
        Valida um arquivo JSON
        
        Args:
            file_path: Caminho do arquivo
            
        Returns:
            Lista de erros encontrados (vazia se não houver erros)
        """
        errors = []
        
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
                errors.extend(SchemaValidator.validate_embate(data))
        except json.JSONDecodeError as e:
            errors.append(f"Erro ao decodificar JSON: {str(e)}")
        except Exception as e:
            errors.append(f"Erro ao ler arquivo: {str(e)}")
        
        return errors
    
    @staticmethod
    def format_date(date: datetime) -> str:
        """
        Formata uma data no padrão ISO8601
        
        Args:
            date: Objeto datetime
            
        Returns:
            String formatada
        """
        return date.isoformat()
    
    @staticmethod
    def sanitize_embate(embate: Dict) -> Dict:
        """
        Sanitiza um embate, corrigindo formatos quando possível
        
        Args:
            embate: Dicionário com dados do embate
            
        Returns:
            Embate sanitizado
        """
        # Copia para não modificar o original
        sanitized = embate.copy()
        
        # Corrige datas
        try:
            data_inicio = datetime.fromisoformat(
                sanitized['data_inicio'].replace('Z', '+00:00')
            )
            sanitized['data_inicio'] = SchemaValidator.format_date(data_inicio)
        except (ValueError, KeyError):
            sanitized['data_inicio'] = SchemaValidator.format_date(datetime.now())
        
        # Corrige argumentos
        if 'argumentos' in sanitized:
            for arg in sanitized['argumentos']:
                try:
                    data = datetime.fromisoformat(
                        arg['data'].replace('Z', '+00:00')
                    )
                    arg['data'] = SchemaValidator.format_date(data)
                except (ValueError, KeyError):
                    arg['data'] = SchemaValidator.format_date(datetime.now())
        
        # Garante metadata mínima
        if 'metadata' not in sanitized:
            sanitized['metadata'] = {
                'impacto': 'médio',
                'prioridade': 'média',
                'tags': ['não_categorizado']
            }
        
        return sanitized 