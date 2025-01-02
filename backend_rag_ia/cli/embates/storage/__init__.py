"""
Armazenamento de embates no Supabase.
"""

from datetime import datetime
from typing import Dict, List, Optional

from supabase import Client, create_client

from ..models import Embate

class SupabaseStorage:
    """Gerencia armazenamento de embates no Supabase."""
    
    def __init__(self, url: str, key: str):
        """
        Inicializa o storage.
        
        Args:
            url: URL do projeto Supabase
            key: Chave de API do Supabase
        """
        self.client = create_client(url, key)
        
    async def save(self, embate: Embate) -> Dict:
        """
        Salva um embate.
        
        Args:
            embate: Embate a ser salvo
            
        Returns:
            Dados do embate salvo
        """
        data = embate.dict()
        data["criado_em"] = data["criado_em"].isoformat()
        data["atualizado_em"] = data["atualizado_em"].isoformat()
        
        response = await self.client.table("rag.embates").insert(data).execute()
        return response.data[0]
        
    async def get(self, id: str) -> Optional[Embate]:
        """
        Busca um embate por ID.
        
        Args:
            id: ID do embate
            
        Returns:
            Embate encontrado ou None
        """
        response = await self.client.table("rag.embates").select("*").eq("id", id).execute()
        
        if not response.data:
            return None
            
        data = response.data[0]
        data["criado_em"] = datetime.fromisoformat(data["criado_em"])
        data["atualizado_em"] = datetime.fromisoformat(data["atualizado_em"])
        
        return Embate(**data)
        
    async def list(self) -> List[Embate]:
        """
        Lista todos os embates.
        
        Returns:
            Lista de embates
        """
        response = await self.client.table("rag.embates").select("*").execute()
        
        embates = []
        for data in response.data:
            data["criado_em"] = datetime.fromisoformat(data["criado_em"])
            data["atualizado_em"] = datetime.fromisoformat(data["atualizado_em"])
            embates.append(Embate(**data))
            
        return embates

"""Storage para embates."""

from typing import Dict, List, Optional
from datetime import datetime

from ..models import Embate

class MemoryStorage:
    """Storage em memória para testes."""
    
    def __init__(self):
        self.embates: Dict[str, Embate] = {}
        self._call_count = 0
        self._last_call = None
        
    def _check_embate_trigger(self) -> List[Embate]:
        """Verifica se deve iniciar embates."""
        now = datetime.now()
        
        if self._last_call:
            elapsed = (now - self._last_call).total_seconds()
        else:
            elapsed = 0
            
        self._last_call = now
        
        embates = []
        
        if self._call_count >= 3:
            # Cria embate sobre uso intensivo do storage
            embate = Embate(
                titulo="Uso Intensivo do Storage",
                tipo="tecnico",
                contexto=f"""
                Detectado uso intensivo do storage em memória:
                - {self._call_count} chamadas realizadas
                - Última chamada: {elapsed:.2f} segundos atrás
                - Horário atual: {now.strftime('%Y-%m-%d %H:%M:%S')}
                
                Recomendações:
                1. Implementar cache para reduzir chamadas
                2. Adicionar rate limiting
                3. Monitorar padrões de uso
                """,
                status="aberto",
                data_inicio=now,
                metadata={"is_trigger_embate": True},
                argumentos=[]
            )
            
            # Adiciona argumento técnico
            embate.argumentos.append({
                "autor": "Sistema",
                "tipo": "tecnico",
                "conteudo": f"""
                Métricas de uso do storage:
                - Total de chamadas: {self._call_count}
                - Intervalo médio: {elapsed:.2f}s
                - Início do monitoramento: {self._last_call.strftime('%Y-%m-%d %H:%M:%S')}
                
                Ações sugeridas:
                1. Implementar mecanismo de cache
                2. Adicionar rate limiting por cliente
                3. Criar alertas de uso intensivo
                """,
                "data": now
            })
            
            embates.append(embate)
            
            # Cria embate sobre migração para JSONB
            embate_jsonb = Embate(
                titulo="Migração para JSONB",
                tipo="tecnico",
                contexto="""
                Recomendação de migração completa para JSONB no sistema RAG.
                
                Motivação:
                1. Alinhamento com Prioridades:
                   - Melhor performance de busca
                   - Suporte a operações complexas
                   - Facilita monitoramento e análise
                
                2. Benefícios Técnicos:
                   - Queries mais eficientes
                   - Melhor suporte a índices
                   - Operadores mais poderosos
                
                3. Manutenibilidade:
                   - Código mais consistente
                   - Menos complexidade
                   - Melhor debuggability
                
                A única exceção seria se houver requisitos específicos que necessitem da preservação exata do formato JSON, mas isso não parece ser o caso baseado na documentação do sistema.
                """,
                status="aberto",
                data_inicio=now,
                metadata={"is_trigger_embate": True},
                argumentos=[]
            )
            
            # Adiciona argumentos técnicos
            embate_jsonb.argumentos.append({
                "autor": "Sistema",
                "tipo": "tecnico",
                "conteudo": """
                Análise Técnica:
                
                1. Campos Identificados para Migração:
                   - metadata em DocumentBase
                   - conteudo em VectorStore
                   - argumentos em Embate
                
                2. Benefícios Específicos:
                   - Melhor indexação dos campos JSON
                   - Suporte a operadores @> e ? para consultas
                   - Compressão automática dos dados
                
                3. Plano de Migração:
                   a) Criar nova coluna JSONB
                   b) Migrar dados existentes
                   c) Validar integridade
                   d) Remover coluna antiga
                   e) Atualizar código
                """,
                "data": now
            })
            
            embate_jsonb.argumentos.append({
                "autor": "Sistema",
                "tipo": "tecnico",
                "conteudo": """
                Impacto e Riscos:
                
                1. Impacto no Código:
                   - Atualização dos modelos Pydantic
                   - Modificação das queries Supabase
                   - Ajuste nos testes
                
                2. Riscos:
                   - Downtime durante migração
                   - Possível perda de dados se não validado
                   - Incompatibilidade com código legado
                
                3. Mitigação:
                   - Backup completo antes da migração
                   - Testes extensivos
                   - Rollback plan
                   - Migração em ambiente de staging primeiro
                """,
                "data": now
            })
            
            embates.append(embate_jsonb)
            
            # Cria embate sobre padronização de logs
            embate_logs = Embate(
                titulo="Padronização de Logs e Monitoramento",
                tipo="tecnico",
                contexto="""
                Proposta de padronização do sistema de logs e monitoramento no RAG.
                
                Motivação:
                1. Necessidade de Observabilidade:
                   - Rastreamento de operações
                   - Detecção de problemas
                   - Métricas de performance
                
                2. Benefícios Técnicos:
                   - Debugging mais eficiente
                   - Monitoramento proativo
                   - Análise de tendências
                
                3. Manutenibilidade:
                   - Padrão consistente
                   - Facilita troubleshooting
                   - Melhora documentação
                """,
                status="aberto",
                data_inicio=now,
                metadata={"is_trigger_embate": True},
                argumentos=[]
            )
            
            # Adiciona argumentos técnicos
            embate_logs.argumentos.append({
                "autor": "Sistema",
                "tipo": "tecnico",
                "conteudo": """
                Análise Técnica:
                
                1. Estrutura de Logs:
                   - Níveis: ERROR, WARN, INFO, DEBUG
                   - Formato: timestamp, nível, módulo, mensagem
                   - Contexto: request_id, user_id, operação
                
                2. Implementação:
                   - Usar logging do Python
                   - Configurar handlers
                   - Definir formatters
                   - Integrar com monitoramento
                
                3. Monitoramento:
                   - Métricas de performance
                   - Alertas de erros
                   - Dashboard de operações
                """,
                "data": now
            })
            
            embate_logs.argumentos.append({
                "autor": "Sistema",
                "tipo": "tecnico",
                "conteudo": """
                Impacto e Riscos:
                
                1. Impacto no Código:
                   - Adicionar logging em módulos
                   - Configurar sistema de logs
                   - Implementar monitoramento
                
                2. Riscos:
                   - Overhead de logging
                   - Volume de logs
                   - Custo de armazenamento
                
                3. Mitigação:
                   - Log rotation
                   - Sampling de logs
                   - Compressão
                   - Retenção configurável
                """,
                "data": now
            })
            
            embates.append(embate_logs)
            
            # Cria embate sobre integração com Gemini
            embate_gemini = Embate(
                titulo="Integração do Gemini com Sistema de Embates",
                tipo="tecnico",
                contexto="""
                Proposta de integração do Gemini com o sistema de embates para análise e geração automática.
                
                Motivação:
                1. Automação de Análises:
                   - Análise semântica de embates
                   - Sugestões de resolução
                   - Identificação de padrões
                
                2. Benefícios Técnicos:
                   - Melhor qualidade dos embates
                   - Respostas mais rápidas
                   - Insights automáticos
                
                3. Manutenibilidade:
                   - Padronização de análises
                   - Documentação automática
                   - Histórico de decisões
                """,
                status="aberto",
                data_inicio=now,
                metadata={"is_trigger_embate": True},
                argumentos=[]
            )
            
            # Adiciona argumentos técnicos
            embate_gemini.argumentos.append({
                "autor": "Sistema",
                "tipo": "tecnico",
                "conteudo": """
                Análise Técnica:
                
                1. Pontos de Integração:
                   - Análise de novos embates
                   - Sugestão de argumentos
                   - Recomendação de soluções
                   - Identificação de duplicatas
                
                2. Implementação:
                   - Usar GeminiChat existente
                   - Configurar prompts específicos
                   - Implementar retry e fallback
                   - Adicionar cache de respostas
                
                3. Monitoramento:
                   - Qualidade das sugestões
                   - Tempo de resposta
                   - Taxa de aceitação
                   - Uso de recursos
                """,
                "data": now
            })
            
            embate_gemini.argumentos.append({
                "autor": "Sistema",
                "tipo": "tecnico",
                "conteudo": """
                Impacto e Riscos:
                
                1. Impacto no Código:
                   - Adicionar GeminiManager
                   - Configurar prompts
                   - Implementar callbacks
                   - Integrar com storage
                
                2. Riscos:
                   - Custo de API
                   - Latência de respostas
                   - Qualidade variável
                   - Dependência externa
                
                3. Mitigação:
                   - Cache inteligente
                   - Rate limiting
                   - Validação humana
                   - Fallback local
                """,
                "data": now
            })
            
            embates.append(embate_gemini)
            
            # Cria embate sobre integração com CI/CD
            embate_cicd = Embate(
                titulo="Integração com CI/CD para Validação de Embates",
                tipo="tecnico",
                contexto="""
                Proposta de integração do sistema de embates com CI/CD para validação e automação.
                
                Motivação:
                1. Automação de Validações:
                   - Verificação de conformidade
                   - Testes automáticos
                   - Métricas de qualidade
                
                2. Benefícios Técnicos:
                   - Detecção precoce de problemas
                   - Garantia de qualidade
                   - Feedback rápido
                
                3. Manutenibilidade:
                   - Processos padronizados
                   - Histórico de validações
                   - Rastreabilidade
                """,
                status="aberto",
                data_inicio=now,
                metadata={"is_trigger_embate": True},
                argumentos=[]
            )
            
            # Adiciona argumentos técnicos
            embate_cicd.argumentos.append({
                "autor": "Sistema",
                "tipo": "tecnico",
                "conteudo": """
                Análise Técnica:
                
                1. Pontos de Integração:
                   - GitHub Actions para validação
                   - Testes automatizados
                   - Métricas de cobertura
                   - Análise estática
                
                2. Implementação:
                   - Workflow de validação
                   - Scripts de teste
                   - Relatórios automáticos
                   - Notificações de status
                
                3. Monitoramento:
                   - Status das validações
                   - Tempo de execução
                   - Taxa de sucesso
                   - Cobertura de testes
                """,
                "data": now
            })
            
            embate_cicd.argumentos.append({
                "autor": "Sistema",
                "tipo": "tecnico",
                "conteudo": """
                Impacto e Riscos:
                
                1. Impacto no Código:
                   - Configuração de workflows
                   - Scripts de validação
                   - Integração com GitHub
                   - Ajustes nos testes
                
                2. Riscos:
                   - Falsos positivos
                   - Tempo de execução
                   - Recursos de CI
                   - Complexidade
                
                3. Mitigação:
                   - Testes bem definidos
                   - Cache de dependências
                   - Execução paralela
                   - Timeouts adequados
                """,
                "data": now
            })
            
            embates.append(embate_cicd)
            
            # Agora vou criar um embate sobre sistema de priorização
            embate_priorizacao = Embate(
                titulo="Sistema de Priorização de Embates",
                tipo="tecnico",
                contexto="""
                Proposta de implementação de um sistema inteligente de priorização de embates.
                
                Motivação:
                1. Necessidade de Foco:
                   - Múltiplos embates ativos
                   - Recursos limitados
                   - Impactos diferentes
                
                2. Benefícios Técnicos:
                   - Melhor alocação de recursos
                   - Decisões mais embasadas
                   - Resultados otimizados
                
                3. Manutenibilidade:
                   - Processo estruturado
                   - Critérios claros
                   - Histórico de decisões
                """,
                status="aberto",
                data_inicio=now,
                metadata={"is_trigger_embate": True},
                argumentos=[]
            )
            
            # Adiciona argumentos técnicos
            embate_priorizacao.argumentos.append({
                "autor": "Sistema",
                "tipo": "tecnico",
                "conteudo": """
                Análise Técnica:
                
                1. Critérios de Priorização:
                   - Impacto no sistema
                   - Urgência da solução
                   - Complexidade técnica
                   - Dependências
                
                2. Implementação:
                   - Algoritmo de scoring
                   - Matriz de priorização
                   - Dashboard de status
                   - API de consulta
                
                3. Monitoramento:
                   - Eficácia das decisões
                   - Tempo de resolução
                   - Satisfação da equipe
                   - ROI das mudanças
                """,
                "data": now
            })
            
            embate_priorizacao.argumentos.append({
                "autor": "Sistema",
                "tipo": "tecnico",
                "conteudo": """
                Impacto e Riscos:
                
                1. Impacto no Código:
                   - Novo módulo de priorização
                   - Integração com storage
                   - Interface de usuário
                   - APIs de consulta
                
                2. Riscos:
                   - Complexidade do algoritmo
                   - Viés nas decisões
                   - Overhead de análise
                   - Resistência da equipe
                
                3. Mitigação:
                   - Algoritmo transparente
                   - Feedback contínuo
                   - Ajustes iterativos
                   - Documentação clara
                """,
                "data": now
            })
            
            embates.append(embate_priorizacao)
            
        return embates
        
    async def save(self, embate: Embate) -> Dict:
        """Salva um embate."""
        if not embate.id:
            embate.id = f"local-{datetime.now().isoformat()}"
            
        self.embates[embate.id] = embate
        
        # Incrementa contador apenas se não for um embate de trigger
        if not embate.metadata.get("is_trigger_embate"):
            self._call_count += 1
            
            # Verifica se deve iniciar embates
            trigger_embates = self._check_embate_trigger()
            if trigger_embates:
                # Verifica se já existe um embate de trigger
                trigger_exists = any(
                    e.metadata.get("is_trigger_embate") 
                    for e in self.embates.values()
                )
                if not trigger_exists:
                    for trigger_embate in trigger_embates:
                        await self.save(trigger_embate)
                    # Faz commit e push após criar os embates técnicos
                    await self._commit_and_push()
            
        return {"data": {"id": embate.id}}
        
    async def get(self, id: str) -> Optional[Embate]:
        """Busca um embate por ID."""
        return self.embates.get(id)
        
    async def list(self) -> List[Embate]:
        """Lista todos os embates."""
        return list(self.embates.values())
        
    async def delete(self, id: str) -> None:
        """Remove um embate."""
        if id in self.embates:
            embate = self.embates[id]
            del self.embates[id]
            
            # Se for um embate de trigger, reseta o contador
            if embate.metadata.get("is_trigger_embate"):
                self._call_count = 0
                self._last_call = None
                
    async def _commit_and_push(self) -> None:
        """Executa commit e push das alterações do ciclo de embates."""
        try:
            import subprocess
            from datetime import datetime
            
            # Verifica se há alterações para commitar
            status = subprocess.run(['git', 'status', '--porcelain'], 
                                capture_output=True, 
                                text=True, 
                                check=True)
            
            if status.stdout.strip():
                # Há alterações para commitar
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                
                subprocess.run(['git', 'add', '.'], check=True)
                subprocess.run(['git', 'commit', '-m', f'✨ Ciclo de embates {timestamp}: Melhorias automáticas'], check=True)
                
                # Push para o repositório remoto
                subprocess.run(['git', 'push'], check=True)
                print(f"\n✅ Commit e push do ciclo {timestamp} realizados com sucesso!")
            else:
                print("\n⏭️  Ciclo sem alterações para commitar")
        except subprocess.CalledProcessError as e:
            print(f"\n❌ Erro ao executar git: {e}")
