# Documentação do Projeto

Este diretório contém toda a documentação do projeto organizada por categorias.

## Estrutura de Diretórios

1. **1_core/**

   - Documentação principal e regras fundamentais
   - Arquivos:
     - `a_readme.md`: Visão geral do projeto
     - `b_project_rules.md`: Regras do projeto
     - `c_regras.md`: Regras gerais
     - `d_regras_documentacao.md`: Regras de documentação
     - `e_estrutura_projeto.md`: Estrutura do projeto
     - `f_regras_verificacao_dupla.md`: Regras de verificação
     - `g_regras_avaliacao_core.md`: Avaliação de core
     - `h_diretrizes_hierarquia.md`: Diretrizes de hierarquia
     - `i_resolucao_conflitos.md`: Resolução de conflitos
     - `j_registro_decisoes.md`: Registro de decisões
     - `k_hierarquia_nomenclatura.md`: Sistema de Hierarquia de Nomenclaturas
     - `l_transicao_pastas_raiz.md`: Regras de Transição das Pastas Raiz

2. **2_database/**

   - Documentação relacionada ao banco de dados
   - Arquivos:
     - `a_render_settings.md`: Configurações do Render
     - `b_models.md`: Modelos de dados
     - `c_problemas_conhecidos.md`: Problemas conhecidos
     - `d_queries.md`: Queries SQL
     - `e_regras_supabase.md`: Regras do Supabase

3. **3_deployment/**

   - Documentação de deploy
   - Arquivos:
     - `a_render.md`: Deploy no Render
     - `b_pipeline.md`: Pipeline de deploy
     - `c_env.md`: Variáveis de ambiente

4. **4_development/**

   - Guias de desenvolvimento
   - Arquivos:
     - `a_standards.md`: Padrões de código
     - `b_workflow.md`: Fluxo de trabalho
     - `c_testing.md`: Testes
     - `d_consulta_primeiro.md`: Princípio "Consultar Primeiro, Criar Depois"

5. **5_monitoring/**

   - Documentação de monitoramento
   - Arquivos:
     - `a_index_monitoring.md`: Índice de monitoramento
     - `b_regras_logs.md`: Regras de logs
     - `c_regras_logs_detalhados.md`: Logs detalhados
     - `d_regras_monitoramento.md`: Regras de monitoramento
     - `e_regras_monitor.md`: Regras do monitor

6. **6_melhorias/**
   - Documentação de melhorias
   - Arquivos:
     - `a_llm_improvements.md`: Melhorias de LLM
     - `b_rag_improvements.md`: Melhorias do RAG
     - `c_autonomy_assessment.md`: Avaliação de autonomia
     - `d_cache_inteligente.md`: Cache inteligente
     - `e_feedback_loop.md`: Feedback loop
     - `f_otimizacao_de_embeddings.md`: Otimização de embeddings

## Convenções de Nomenclatura

1. Arquivos Markdown:

   - Começar com letra minúscula (a*, b*, c\*, etc.)
   - Usar underscores para espaços
   - Exemplo: a_config.md, b_setup.md, c_guide.md

2. Diretórios:

   - Começar com número (1*, 2*, 3\*, etc.)
   - Usar underscores para espaços
   - Exemplo: 1_core, 2_database

## Regras de Atualização

1. Novos Arquivos:

   - Seguir a sequência alfabética existente
   - Manter a organização por diretórios
   - Atualizar este índice

2. Novos Diretórios:

   - Seguir a sequência numérica
   - Criar README.md interno
   - Atualizar este índice

3. Manutenção:
   - Manter o índice atualizado
   - Documentar mudanças significativas
   - Seguir o padrão de versionamento

# Regras e Diretrizes do Projeto

## 🚫 Funcionalidades que NÃO devem ser implementadas

### 1. Proteção DDoS

**Motivo**: O Render já fornece proteção DDoS nativa e gratuita

- ✅ Usa infraestrutura Cloudflare
- ✅ Ativação automática
- ✅ Mais robusta que implementações manuais
- ❌ Não implementar sistemas próprios de rate limiting
- ❌ Não criar blacklists de IPs manualmente

### 2. Health Check

**Motivo**: Sistema nativo do Render mais eficiente

- ✅ Auto-healing automático
- ✅ Reinicia apps não responsivos
- ✅ Monitoramento integrado
- ❌ Não criar verificações redundantes
- ❌ Não implementar sistema próprio de health check

### 3. Monitoramento de Sistema

**Motivo**: Render oferece monitoramento nativo

- ✅ Métricas em tempo real
- ✅ Notificações via Slack
- ✅ Dashboard integrado
- ❌ Não duplicar coleta de métricas básicas
- ❌ Não criar sistemas paralelos de alertas

## ✅ O que DEVE ser mantido

### 1. Sistema de Embates

Mantenha apenas funcionalidades específicas do negócio:

- Controle de uso de ferramentas
- Sistema de contenção
- Métricas de hidratação
- Relatórios personalizados

### 2. Logs e Relatórios

Mantenha apenas logs específicos:

- Estado dos embates
- Métricas de negócio
- Relatórios customizados

## 📋 Checklist para Novas Implementações

Antes de implementar novas funcionalidades, verifique:

1. O Render já oferece essa funcionalidade nativamente?
2. A implementação adiciona valor específico ao negócio?
3. Não há duplicação com serviços existentes?

## 🔄 Processo de Revisão

Ao revisar código, verifique:

- [ ] Não há implementações redundantes com o Render
- [ ] Funcionalidades são específicas do negócio
- [ ] Código segue as diretrizes de otimização

## 📚 Referências

- [Documentação do Render sobre DDoS](https://render.com/docs/ddos-protection)
- [Monitoramento no Render](https://render.com/docs/monitoring)
- [Health Checks](https://render.com/docs/health-checks)

## ⚠️ Observações Importantes

1. **Custo-Benefício**:

   - Implementações próprias = maior custo de manutenção
   - Soluções nativas = melhor performance

2. **Segurança**:

   - Proteções nativas são mais robustas
   - Atualizações automáticas de segurança

3. **Manutenção**:
   - Menos código = menos bugs
   - Foco em lógica de negócio
