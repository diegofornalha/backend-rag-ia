"""
Sistema de upload de documentos integrado ao multiagente.
"""

import json
import re
from datetime import datetime
from typing import Any, Dict, Optional, Tuple

from ..llm_services.tracker import LlmTracker
from .base_agent import GeminiAgent


class DocumentUploadAgent(GeminiAgent):
    """Agente especializado em processamento de uploads de documentos."""

    def __init__(self, name: str, api_key: str):
        """Inicializa o agente."""
        super().__init__(name, api_key)
        self.tracker = LlmTracker()

    async def process(self, context: dict[str, Any]) -> dict[str, Any]:
        """
        Processa uma tarefa de upload.

        Args:
            context: Contexto da tarefa contendo content e cliente

        Returns:
            dict: Resultado do processamento
        """
        try:
            content = context.get("content")
            cliente = context.get("cliente")
            
            if not content or not cliente:
                self.track_upload_event("error", {
                    "error": "Conteúdo ou cliente não fornecidos",
                    "cliente": cliente
                })
                return {"error": "Conteúdo ou cliente não fornecidos"}
                
            # Primeiro valida e formata
            success, suggested_name, data = self.process_upload(content, cliente)
            
            if not success:
                self.track_upload_event("validation_failed", {
                    "error": data,
                    "cliente": cliente
                })
                return {"error": data}

            # Se for uma pergunta sobre o conteúdo
            if context.get("is_question"):
                response = await self.analyze_and_respond(content, context.get("question"))
                return {
                    "status": "success",
                    "response": response
                }

            # Se for um upload normal, tenta enriquecer o conteúdo
            enriched_data = await self.enrich_content(data['content'])
            
            self.track_upload_event("success", {
                "cliente": cliente,
                "filename": suggested_name
            })
            
            return {
                "status": "success",
                "data": enriched_data,
                "suggested_name": suggested_name
            }
            
        except Exception as e:
            self.track_upload_event("error", {
                "error": str(e),
                "cliente": context.get("cliente")
            })
            return {"error": f"Erro no processamento: {str(e)}"}

    async def enrich_content(self, content: Dict) -> Dict:
        """Enriquece o conteúdo do documento usando o modelo Gemini."""
        try:
            # Prepara o prompt para o modelo
            prompt = f"""Analise este documento e sugira melhorias:

Título: {content.get('titulo')}
Conteúdo: {content.get('conteudo')}

Por favor:
1. Identifique os principais tópicos
2. Sugira informações adicionais relevantes
3. Proponha uma estrutura mais clara se necessário
4. Indique possíveis referências ou documentos relacionados"""

            # Obtém sugestões do modelo
            response = await self.run(prompt)
            suggestions = response.get("result", "")

            # Adiciona as sugestões ao conteúdo
            enriched = {
                **content,
                "sugestoes_melhoria": suggestions,
                "enriquecido_em": datetime.now().isoformat()
            }

            return enriched

        except Exception as e:
            print(f"Erro ao enriquecer conteúdo: {e}")
            return content  # Retorna conteúdo original se houver erro

    async def analyze_and_respond(self, content: str, question: str) -> str:
        """Analisa o conteúdo e responde perguntas sobre ele."""
        try:
            prompt = f"""Com base neste conteúdo:

{content}

Por favor, responda esta pergunta: {question}

Forneça uma resposta detalhada e útil, incluindo:
1. Explicação direta
2. Exemplos relevantes
3. Possíveis implicações
4. Referências a partes específicas do documento"""

            response = await self.run(prompt)
            return response.get("result", "Desculpe, não foi possível analisar o conteúdo.")

        except Exception as e:
            return f"Erro ao analisar o conteúdo: {str(e)}"

    def track_upload_event(self, event_type: str, data: dict[str, Any]) -> None:
        """Registra eventos de upload no tracker."""
        self.tracker.track_event(f"document_upload_{event_type}", {
            "timestamp": datetime.now().isoformat(),
            "agent": self.name,
            **data
        })

    def extract_json_from_text(self, text: str) -> Optional[str]:
        """Tenta extrair um JSON válido do texto"""
        # Procura por padrões que parecem ser JSON
        json_pattern = r'\{[^{}]*\}'
        matches = re.findall(json_pattern, text)
        
        if not matches:
            return None
            
        # Tenta o maior match primeiro (provavelmente o JSON completo)
        matches.sort(key=len, reverse=True)
        return matches[0]

    def attempt_json_repair(self, content: str) -> Tuple[bool, Optional[Dict], str]:
        """Tenta reparar e extrair informações de um JSON malformado"""
        try:
            # Primeiro, tenta extrair um JSON válido do texto
            json_str = self.extract_json_from_text(content)
            if not json_str:
                return False, None, "Não foi possível encontrar um JSON válido no texto"

            # Tenta fazer o parse do JSON extraído
            data = json.loads(json_str)
            
            # Se chegou aqui, temos um dict, mas pode faltar campos
            result = {}
            
            # Procura por campos que podem ser o título
            title_fields = ['titulo', 'title', 'nome', 'name', 'assunto', 'subject']
            content_fields = ['conteudo', 'content', 'texto', 'text', 'body', 'mensagem', 'message']
            
            # Procura o título
            for field in title_fields:
                if field in data:
                    result['titulo'] = str(data[field]).strip()
                    break
            
            # Procura o conteúdo
            for field in content_fields:
                if field in data:
                    result['conteudo'] = str(data[field]).strip()
                    break
            
            # Se não encontrou título mas tem mensagem estruturada
            if 'titulo' not in result and 'mensagem' in data and isinstance(data['mensagem'], dict):
                msg = data['mensagem']
                # Tenta extrair um título da mensagem
                possible_titles = [
                    msg.get('saudacao', ''),
                    msg.get('introducao', ''),
                    msg.get('titulo', '')
                ]
                # Usa o primeiro não vazio
                for title in possible_titles:
                    if title:
                        result['titulo'] = title[:100]  # Limita tamanho
                        break

            # Se ainda não tem título, cria um baseado no timestamp
            if 'titulo' not in result:
                timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
                result['titulo'] = f"Documento {timestamp}"
            
            # Se não encontrou conteúdo, usa todo o JSON original como conteúdo
            if 'conteudo' not in result:
                result['conteudo'] = json.dumps(data, ensure_ascii=False, indent=2)
            
            return True, result, "JSON reparado com sucesso"
            
        except Exception as e:
            return False, None, f"Erro ao tentar reparar JSON: {str(e)}"

    def validate_json(self, content: str) -> Tuple[bool, Optional[Dict], str]:
        """Valida e formata o JSON do documento"""
        try:
            # Primeiro tenta fazer o parse normal
            parsed = json.loads(content)
            
            # Validação de campos obrigatórios
            if not parsed.get('titulo') or not parsed.get('conteudo'):
                # Se falhou, tenta reparar
                success, repaired, message = self.attempt_json_repair(content)
                if success:
                    return True, repaired, "JSON corrigido e formatado automaticamente"
                return False, None, message
            
            # Limpeza e formatação
            formatted = {
                'titulo': parsed['titulo'].strip(),
                'conteudo': parsed['conteudo'].strip()
            }
            
            return True, formatted, "JSON válido"
            
        except json.JSONDecodeError:
            # Se não conseguiu fazer o parse, tenta reparar
            success, repaired, message = self.attempt_json_repair(content)
            if success:
                return True, repaired, "JSON corrigido e formatado automaticamente"
            return False, None, message
        except Exception as e:
            return False, None, f"Erro na validação: {str(e)}"

    def suggest_filename(self, content: Dict) -> str:
        """Gera sugestão inteligente de nome de arquivo"""
        titulo = content['titulo']
        
        # Limpeza e formatação do título
        clean_name = (
            titulo.lower()
            .replace(' ', '-')
            .replace('_', '-')
            .replace('.', '-')
        )
        
        # Remove caracteres especiais
        clean_name = re.sub(r'[^a-z0-9-]', '', clean_name)
        
        # Remove hífens duplicados e no início/fim
        clean_name = re.sub(r'-+', '-', clean_name).strip('-')
        
        # Adiciona timestamp para garantir unicidade
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        
        return f"{clean_name}-{timestamp}.json"
    
    def process_upload(self, content: str, cliente: str) -> Tuple[bool, str, Optional[Dict]]:
        """Processa o upload completo do documento"""
        # Validação do JSON
        is_valid, formatted, message = self.validate_json(content)
        if not is_valid:
            return False, message, None
            
        # Gera sugestão de nome
        suggested_name = self.suggest_filename(formatted)
        
        # Prepara metadados
        metadata = {
            'cliente': cliente,
            'tipo': 'json',
            'processado_por': 'document_upload_agent',
            'data_processamento': datetime.now().isoformat()
        }
        
        return True, suggested_name, {
            'content': formatted,
            'metadata': metadata,
            'suggested_name': suggested_name
        }

    def format_error_message(self, error: str) -> str:
        """Formata mensagem de erro com exemplo"""
        return f"""❌ Erro: {error}

O formato correto deve ser:
```json
{{
  "titulo": "Nome do Documento",
  "conteudo": "Texto do documento aqui"
}}
```

Por favor, corrija o formato e tente novamente.""" 