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
            
            # Cria embate sobre análise de dependências
            embate_deps = Embate(
                titulo="Análise de Dependências entre Embates",
                tipo="tecnico",
                contexto="""
                Proposta de implementação de um sistema de análise de dependências entre embates.
                
                Motivação:
                1. Relações Complexas:
                   - Embates interdependentes
                   - Ordem de implementação
                   - Impactos em cascata
                
                2. Benefícios Técnicos:
                   - Melhor planejamento
                   - Redução de retrabalho
                   - Otimização de recursos
                
                3. Manutenibilidade:
                   - Visualização clara
                   - Decisões informadas
                   - Histórico de relações
                """,
                status="aberto",
                data_inicio=now,
                metadata={"is_trigger_embate": True},
                argumentos=[]
            )
            
            # Adiciona argumentos técnicos
            embate_deps.argumentos.append({
                "autor": "Sistema",
                "tipo": "tecnico",
                "conteudo": """
                Análise Técnica:
                
                1. Tipos de Dependência:
                   - Técnica (código/arquitetura)
                   - Funcional (features)
                   - Temporal (ordem)
                   - Recursos (equipe/infra)
                
                2. Implementação:
                   - Grafo de dependências
                   - Análise de impacto
                   - Visualização interativa
                   - API de consulta
                
                3. Integração:
                   - Sistema de priorização
                   - CI/CD pipeline
                   - Gemini para análise
                   - Storage para histórico
                """,
                "data": now
            })
            
            embate_deps.argumentos.append({
                "autor": "Sistema",
                "tipo": "tecnico",
                "conteudo": """
                Impacto e Riscos:
                
                1. Impacto no Código:
                   - Novo módulo de dependências
                   - Integração com storage
                   - Interface de visualização
                   - APIs de análise
                
                2. Riscos:
                   - Complexidade do grafo
                   - Performance da análise
                   - Manutenção do histórico
                   - Precisão das relações
                
                3. Mitigação:
                   - Algoritmos eficientes
                   - Cache de análises
                   - Validação manual
                   - Documentação clara
                """,
                "data": now
            })
            
            embates.append(embate_deps)
            
            # E agora vou criar um embate sobre dashboard de métricas
            embate_dashboard = Embate(
                titulo="Dashboard de Métricas de Embates",
                tipo="tecnico",
                contexto="""
                Proposta de implementação de um dashboard para visualização e análise de métricas de embates.
                
                Motivação:
                1. Visibilidade:
                   - Status dos embates
                   - Métricas de progresso
                   - Tendências e padrões
                
                2. Benefícios Técnicos:
                   - Monitoramento em tempo real
                   - Análise de performance
                   - Tomada de decisão
                
                3. Manutenibilidade:
                   - Centralização de dados
                   - Histórico de métricas
                   - Relatórios automáticos
                """,
                status="aberto",
                data_inicio=now,
                metadata={"is_trigger_embate": True},
                argumentos=[]
            )
            
            # Adiciona argumentos técnicos
            embate_dashboard.argumentos.append({
                "autor": "Sistema",
                "tipo": "tecnico",
                "conteudo": """
                Análise Técnica:
                
                1. Métricas Principais:
                   - Taxa de resolução
                   - Tempo médio
                   - Distribuição por tipo
                   - Tendências temporais
                
                2. Implementação:
                   - Frontend React
                   - Gráficos D3.js
                   - API de métricas
                   - Cache Redis
                
                3. Integrações:
                   - Sistema de embates
                   - Análise de dependências
                   - CI/CD pipeline
                   - Alertas e notificações
                """,
                "data": now
            })
            
            embate_dashboard.argumentos.append({
                "autor": "Sistema",
                "tipo": "tecnico",
                "conteudo": """
                Impacto e Riscos:
                
                1. Impacto no Código:
                   - Novo frontend
                   - APIs de métricas
                   - Coleta de dados
                   - Cache layer
                
                2. Riscos:
                   - Performance do frontend
                   - Volume de dados
                   - Manutenção de gráficos
                   - Complexidade de queries
                
                3. Mitigação:
                   - Otimização de queries
                   - Agregação de dados
                   - Componentização
                   - Testes E2E
                """,
                "data": now
            })
            
            embates.append(embate_dashboard)
            
            # Cria embate sobre integração com sistemas externos
            embate_external = Embate(
                titulo="Integração com Sistemas Externos",
                tipo="tecnico",
                contexto="""
                Proposta de padronização e gerenciamento de integrações com sistemas externos.
                
                Motivação:
                1. Dependências Externas:
                   - Gemini para análise
                   - GitHub para CI/CD
                   - Redis para cache
                   - Supabase para storage
                
                2. Benefícios Técnicos:
                   - Resiliência do sistema
                   - Gerenciamento de falhas
                   - Performance otimizada
                
                3. Manutenibilidade:
                   - Padrões consistentes
                   - Monitoramento unificado
                   - Documentação centralizada
                """,
                status="aberto",
                data_inicio=now,
                metadata={"is_trigger_embate": True},
                argumentos=[]
            )
            
            # Adiciona argumentos técnicos
            embate_external.argumentos.append({
                "autor": "Sistema",
                "tipo": "tecnico",
                "conteudo": """
                Análise Técnica:
                
                1. Pontos de Integração:
                   - APIs externas
                   - Sistemas de cache
                   - Bancos de dados
                   - Serviços de IA
                
                2. Implementação:
                   - Camada de abstração
                   - Retry policies
                   - Circuit breakers
                   - Rate limiting
                
                3. Monitoramento:
                   - Health checks
                   - Métricas de latência
                   - Logs estruturados
                   - Alertas automáticos
                """,
                "data": now
            })
            
            embate_external.argumentos.append({
                "autor": "Sistema",
                "tipo": "tecnico",
                "conteudo": """
                Impacto e Riscos:
                
                1. Impacto no Código:
                   - Novos adaptadores
                   - Configuração de retry
                   - Implementação de fallbacks
                   - Testes de integração
                
                2. Riscos:
                   - Indisponibilidade externa
                   - Custos de API
                   - Complexidade adicional
                   - Manutenção contínua
                
                3. Mitigação:
                   - Fallbacks locais
                   - Cache estratégico
                   - Monitoramento proativo
                   - Documentação detalhada
                """,
                "data": now
            })
            
            embates.append(embate_external)
            
            # Cria embate sobre segurança e autenticação
            embate_security = Embate(
                titulo="Segurança e Autenticação do Sistema",
                tipo="tecnico",
                contexto="""
                Proposta de implementação de um sistema robusto de segurança e autenticação.
                
                Motivação:
                1. Requisitos de Segurança:
                   - Proteção de endpoints
                   - Autenticação de usuários
                   - Autorização de ações
                   - Auditoria de acessos
                
                2. Benefícios Técnicos:
                   - Controle de acesso
                   - Rastreabilidade
                   - Conformidade
                   - Prevenção de ataques
                
                3. Manutenibilidade:
                   - Padrões de segurança
                   - Logs de auditoria
                   - Documentação segura
                """,
                status="aberto",
                data_inicio=now,
                metadata={"is_trigger_embate": True},
                argumentos=[]
            )
            
            # Adiciona argumentos técnicos
            embate_security.argumentos.append({
                "autor": "Sistema",
                "tipo": "tecnico",
                "conteudo": """
                Análise Técnica:
                
                1. Componentes de Segurança:
                   - JWT Authentication
                   - Role-based Access Control
                   - API Key Management
                   - Rate Limiting
                
                2. Implementação:
                   - Middleware de autenticação
                   - Sistema de roles
                   - Gestão de tokens
                   - Logs de segurança
                
                3. Monitoramento:
                   - Tentativas de acesso
                   - Padrões suspeitos
                   - Uso de recursos
                   - Alertas de segurança
                """,
                "data": now
            })
            
            embate_security.argumentos.append({
                "autor": "Sistema",
                "tipo": "tecnico",
                "conteudo": """
                Impacto e Riscos:
                
                1. Impacto no Código:
                   - Middleware de auth
                   - Decorators de proteção
                   - Sistema de roles
                   - Logs de auditoria
                
                2. Riscos:
                   - Complexidade adicional
                   - Overhead de autenticação
                   - Gestão de tokens
                   - Manutenção de roles
                
                3. Mitigação:
                   - Testes de segurança
                   - Documentação clara
                   - Monitoramento constante
                   - Atualizações regulares
                """,
                "data": now
            })
            
            embates.append(embate_security)
            
            # Cria embate sobre documentação e API Docs
            embate_docs = Embate(
                titulo="Documentação e API Docs do Sistema",
                tipo="tecnico",
                contexto="""
                Proposta de implementação de um sistema completo de documentação e API Docs.
                
                Motivação:
                1. Necessidades de Documentação:
                   - API Reference
                   - Guias de integração
                   - Exemplos de uso
                   - Troubleshooting
                
                2. Benefícios Técnicos:
                   - Facilita integrações
                   - Reduz suporte
                   - Melhora adoção
                   - Garante qualidade
                
                3. Manutenibilidade:
                   - Documentação viva
                   - Testes de docs
                   - Versionamento
                   - Feedback loop
                """,
                status="aberto",
                data_inicio=now,
                metadata={"is_trigger_embate": True},
                argumentos=[]
            )
            
            # Adiciona argumentos técnicos
            embate_docs.argumentos.append({
                "autor": "Sistema",
                "tipo": "tecnico",
                "conteudo": """
                Análise Técnica:
                
                1. Componentes:
                   - OpenAPI/Swagger
                   - Markdown docs
                   - Code examples
                   - Integration guides
                
                2. Implementação:
                   - FastAPI docs
                   - MkDocs setup
                   - Doc tests
                   - CI/CD integration
                
                3. Monitoramento:
                   - Doc coverage
                   - Usage analytics
                   - Feedback forms
                   - Error tracking
                """,
                "data": now
            })
            
            embate_docs.argumentos.append({
                "autor": "Sistema",
                "tipo": "tecnico",
                "conteudo": """
                Impacto e Riscos:
                
                1. Impacto no Código:
                   - OpenAPI schemas
                   - Doc strings
                   - Example code
                   - Test cases
                
                2. Riscos:
                   - Docs desatualizados
                   - Exemplos quebrados
                   - Complexidade
                   - Manutenção contínua
                
                3. Mitigação:
                   - Doc tests
                   - CI/CD checks
                   - Review process
                   - Feedback loop
                """,
                "data": now
            })
            
            embates.append(embate_docs)
            
            # Cria embate sobre testes automatizados
            embate_tests = Embate(
                titulo="Testes Automatizados e Cobertura de Código",
                tipo="tecnico",
                contexto="""
                Proposta de implementação de um sistema completo de testes automatizados e cobertura de código.
                
                Motivação:
                1. Necessidades de Testes:
                   - Testes unitários
                   - Testes de integração
                   - Testes end-to-end
                   - Testes de performance
                
                2. Benefícios Técnicos:
                   - Qualidade do código
                   - Detecção de bugs
                   - Refatoração segura
                   - Documentação viva
                
                3. Manutenibilidade:
                   - Cobertura de código
                   - Testes automatizados
                   - CI/CD integration
                   - Feedback rápido
                """,
                status="aberto",
                data_inicio=now,
                metadata={"is_trigger_embate": True},
                argumentos=[]
            )
            
            # Adiciona argumentos técnicos
            embate_tests.argumentos.append({
                "autor": "Sistema",
                "tipo": "tecnico",
                "conteudo": """
                Análise Técnica:
                
                1. Componentes:
                   - PyTest framework
                   - Coverage.py
                   - Mocking tools
                   - Test fixtures
                
                2. Implementação:
                   - Test structure
                   - Coverage reports
                   - CI/CD pipeline
                   - Test automation
                
                3. Monitoramento:
                   - Coverage metrics
                   - Test results
                   - Performance stats
                   - Quality gates
                """,
                "data": now
            })
            
            embate_tests.argumentos.append({
                "autor": "Sistema",
                "tipo": "tecnico",
                "conteudo": """
                Impacto e Riscos:
                
                1. Impacto no Código:
                   - Test files
                   - Coverage config
                   - CI/CD changes
                   - Documentation
                
                2. Riscos:
                   - Test maintenance
                   - False positives
                   - Performance impact
                   - Coverage gaps
                
                3. Mitigação:
                   - Test reviews
                   - Quality metrics
                   - Regular updates
                   - Team training
                """,
                "data": now
            })
            
            embates.append(embate_tests)
            
            # Cria embate sobre gerenciamento de versões
            embate_versions = Embate(
                titulo="Gerenciamento de Versões e Releases",
                tipo="tecnico",
                contexto="""
                Proposta de implementação de um sistema completo de gerenciamento de versões e releases.
                
                Motivação:
                1. Necessidades de Versionamento:
                   - Controle de versões
                   - Release automation
                   - Change tracking
                   - Version tagging
                
                2. Benefícios Técnicos:
                   - Release control
                   - Version history
                   - Rollback support
                   - Dependency management
                
                3. Manutenibilidade:
                   - Release notes
                   - Version docs
                   - Migration guides
                   - Breaking changes
                """,
                status="aberto",
                data_inicio=now,
                metadata={"is_trigger_embate": True},
                argumentos=[]
            )
            
            # Adiciona argumentos técnicos
            embate_versions.argumentos.append({
                "autor": "Sistema",
                "tipo": "tecnico",
                "conteudo": """
                Análise Técnica:
                
                1. Componentes:
                   - Semantic versioning
                   - Release scripts
                   - Version control
                   - Change tracking
                
                2. Implementação:
                   - Version system
                   - Release process
                   - CI/CD pipeline
                   - Documentation
                
                3. Monitoramento:
                   - Release metrics
                   - Version stats
                   - Usage tracking
                   - Feedback loop
                """,
                "data": now
            })
            
            embate_versions.argumentos.append({
                "autor": "Sistema",
                "tipo": "tecnico",
                "conteudo": """
                Impacto e Riscos:
                
                1. Impacto no Código:
                   - Version tags
                   - Release notes
                   - Migration code
                   - Documentation
                
                2. Riscos:
                   - Breaking changes
                   - Migration issues
                   - Version conflicts
                   - Dependency hell
                
                3. Mitigação:
                   - Version tests
                   - Migration tests
                   - Release checks
                   - Rollback plan
                """,
                "data": now
            })
            
            embates.append(embate_versions)
            
            # Cria embate sobre otimização de performance
            embate_perf = Embate(
                titulo="Otimização de Performance e Escalabilidade",
                tipo="tecnico",
                contexto="""
                Proposta de implementação de um sistema completo de otimização de performance e escalabilidade.
                
                Motivação:
                1. Necessidades de Performance:
                   - Response time
                   - Throughput
                   - Resource usage
                   - Scalability
                
                2. Benefícios Técnicos:
                   - Better UX
                   - Cost savings
                   - Reliability
                   - Maintainability
                
                3. Escalabilidade:
                   - Load balancing
                   - Auto scaling
                   - Caching
                   - Optimization
                """,
                status="aberto",
                data_inicio=now,
                metadata={"is_trigger_embate": True},
                argumentos=[]
            )
            
            # Adiciona argumentos técnicos
            embate_perf.argumentos.append({
                "autor": "Sistema",
                "tipo": "tecnico",
                "conteudo": """
                Análise Técnica:
                
                1. Componentes:
                   - Load testing
                   - Profiling tools
                   - Monitoring
                   - Analytics
                
                2. Implementação:
                   - Code optimization
                   - Cache strategy
                   - DB tuning
                   - Infrastructure
                
                3. Monitoramento:
                   - Performance KPIs
                   - Resource usage
                   - Error rates
                   - Response times
                """,
                "data": now
            })
            
            embate_perf.argumentos.append({
                "autor": "Sistema",
                "tipo": "tecnico",
                "conteudo": """
                Impacto e Riscos:
                
                1. Impacto no Código:
                   - Optimization
                   - Refactoring
                   - Architecture
                   - Infrastructure
                
                2. Riscos:
                   - Complexity
                   - Side effects
                   - Tech debt
                   - Resource costs
                
                3. Mitigação:
                   - Testing
                   - Monitoring
                   - Documentation
                   - Rollback plan
                """,
                "data": now
            })
            
            embates.append(embate_perf)
            
            # Cria embate sobre arquitetura
            embate_arch = Embate(
                titulo="Arquitetura e Design Patterns",
                tipo="tecnico",
                contexto="""
                Proposta de implementação de uma arquitetura robusta e padrões de design.
                
                Motivação:
                1. Necessidades de Arquitetura:
                   - Clean architecture
                   - Design patterns
                   - SOLID principles
                   - Best practices
                
                2. Benefícios Técnicos:
                   - Maintainability
                   - Scalability
                   - Testability
                   - Flexibility
                
                3. Padrões:
                   - Repository pattern
                   - Factory pattern
                   - Strategy pattern
                   - Observer pattern
                """,
                status="aberto",
                data_inicio=now,
                metadata={"is_trigger_embate": True},
                argumentos=[]
            )
            
            # Adiciona argumentos técnicos
            embate_arch.argumentos.append({
                "autor": "Sistema",
                "tipo": "tecnico",
                "conteudo": """
                Análise Técnica:
                
                1. Componentes:
                   - Domain models
                   - Use cases
                   - Interfaces
                   - Infrastructure
                
                2. Implementação:
                   - Clean arch layers
                   - Design patterns
                   - Dependency injection
                   - Interface segregation
                
                3. Monitoramento:
                   - Code quality
                   - Architecture rules
                   - Pattern usage
                   - Dependencies
                """,
                "data": now
            })
            
            embate_arch.argumentos.append({
                "autor": "Sistema",
                "tipo": "tecnico",
                "conteudo": """
                Impacto e Riscos:
                
                1. Impacto no Código:
                   - Refactoring
                   - New patterns
                   - Architecture
                   - Dependencies
                
                2. Riscos:
                   - Complexity
                   - Learning curve
                   - Over-engineering
                   - Tech debt
                
                3. Mitigação:
                   - Documentation
                   - Training
                   - Code reviews
                   - Gradual changes
                """,
                "data": now
            })
            
            embates.append(embate_arch)
            
            # Cria embate sobre internacionalização
            embate_i18n = Embate(
                titulo="Internacionalização e Localização",
                tipo="tecnico",
                contexto="""
                Proposta de implementação de um sistema completo de internacionalização e localização.
                
                Motivação:
                1. Necessidades de I18n/L10n:
                   - Múltiplos idiomas
                   - Formatos regionais
                   - Conteúdo localizado
                   - Acessibilidade
                
                2. Benefícios Técnicos:
                   - Expansão global
                   - Melhor UX
                   - Conformidade
                   - Flexibilidade
                
                3. Manutenibilidade:
                   - Strings externalizadas
                   - Traduções gerenciadas
                   - Formatos padronizados
                   - Updates simplificados
                """,
                status="aberto",
                data_inicio=now,
                metadata={"is_trigger_embate": True},
                argumentos=[]
            )
            
            # Adiciona argumentos técnicos
            embate_i18n.argumentos.append({
                "autor": "Sistema",
                "tipo": "tecnico",
                "conteudo": """
                Análise Técnica:
                
                1. Componentes:
                   - Sistema de traduções
                   - Formatação regional
                   - RTL support
                   - Unicode handling
                
                2. Implementação:
                   - Gettext setup
                   - Translation files
                   - Format handlers
                   - Language detection
                
                3. Monitoramento:
                   - Coverage de traduções
                   - Qualidade de traduções
                   - Usage analytics
                   - User feedback
                """,
                "data": now
            })
            
            embate_i18n.argumentos.append({
                "autor": "Sistema",
                "tipo": "tecnico",
                "conteudo": """
                Impacto e Riscos:
                
                1. Impacto no Código:
                   - String extraction
                   - Format handling
                   - UI adjustments
                   - Testing setup
                
                2. Riscos:
                   - Missing translations
                   - Format errors
                   - Context issues
                   - Performance impact
                
                3. Mitigação:
                   - Translation review
                   - Automated tests
                   - Context docs
                   - Performance monitoring
                """,
                "data": now
            })
            
            embates.append(embate_i18n)
            
            # Cria embate sobre backup
            embate_backup = Embate(
                titulo="Backup e Recuperação de Dados",
                tipo="tecnico",
                contexto="""
                Proposta de implementação de um sistema completo de backup e recuperação de dados.
                
                Motivação:
                1. Necessidades de Backup:
                   - Dados críticos
                   - Recuperação de desastres
                   - Conformidade legal
                   - Continuidade
                
                2. Benefícios Técnicos:
                   - Segurança de dados
                   - Recuperação rápida
                   - Auditoria
                   - Compliance
                
                3. Manutenibilidade:
                   - Backups automáticos
                   - Verificação periódica
                   - Rotação de backups
                   - Documentação
                """,
                status="aberto",
                data_inicio=now,
                metadata={"is_trigger_embate": True},
                argumentos=[]
            )
            
            # Adiciona argumentos técnicos
            embate_backup.argumentos.append({
                "autor": "Sistema",
                "tipo": "tecnico",
                "conteudo": """
                Análise Técnica:
                
                1. Componentes:
                   - Backup system
                   - Recovery tools
                   - Monitoring
                   - Verification
                
                2. Implementação:
                   - Backup strategy
                   - Recovery process
                   - Testing plan
                   - Documentation
                
                3. Monitoramento:
                   - Backup status
                   - Recovery tests
                   - Storage usage
                   - Performance impact
                """,
                "data": now
            })
            
            embate_backup.argumentos.append({
                "autor": "Sistema",
                "tipo": "tecnico",
                "conteudo": """
                Impacto e Riscos:
                
                1. Impacto no Sistema:
                   - Storage usage
                   - Network traffic
                   - Processing load
                   - Recovery time
                
                2. Riscos:
                   - Backup failures
                   - Recovery issues
                   - Data corruption
                   - Performance impact
                
                3. Mitigação:
                   - Monitoring
                   - Regular tests
                   - Documentation
                   - Training
                """,
                "data": now
            })
            
            embates.append(embate_backup)
            
            # Cria embate sobre configurações
            embate_config = Embate(
                titulo="Gestão de Configurações",
                tipo="tecnico",
                contexto="""
                Proposta de implementação de um sistema completo de gestão de configurações.
                
                Motivação:
                1. Necessidades de Configuração:
                   - Múltiplos ambientes
                   - Segurança de dados
                   - Flexibilidade
                   - Manutenibilidade
                
                2. Benefícios Técnicos:
                   - Configuração centralizada
                   - Versionamento
                   - Auditoria
                   - Segurança
                
                3. Manutenibilidade:
                   - Gestão simplificada
                   - Documentação automática
                   - Validação
                   - Histórico
                """,
                status="aberto",
                data_inicio=now,
                metadata={"is_trigger_embate": True},
                argumentos=[]
            )
            
            # Adiciona argumentos técnicos
            embate_config.argumentos.append({
                "autor": "Sistema",
                "tipo": "tecnico",
                "conteudo": """
                Análise Técnica:
                
                1. Componentes:
                   - Config manager
                   - Secret storage
                   - Environment handling
                   - Validation system
                
                2. Implementação:
                   - Config structure
                   - Secret management
                   - Environment setup
                   - Documentation
                
                3. Monitoramento:
                   - Config changes
                   - Access logs
                   - Validation status
                   - Usage patterns
                """,
                "data": now
            })
            
            embate_config.argumentos.append({
                "autor": "Sistema",
                "tipo": "tecnico",
                "conteudo": """
                Impacto e Riscos:
                
                1. Impacto no Sistema:
                   - Code changes
                   - Security setup
                   - Environment config
                   - Documentation
                
                2. Riscos:
                   - Security exposure
                   - Config conflicts
                   - Migration issues
                   - Performance impact
                
                3. Mitigação:
                   - Security review
                   - Testing strategy
                   - Documentation
                   - Monitoring
                """,
                "data": now
            })
            
            embates.append(embate_config)
            
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
