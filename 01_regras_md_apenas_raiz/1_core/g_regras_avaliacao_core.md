# Regras para Avaliação de Core vs. Não-Core

## Definição de Core

### O que é Core?

1. Componentes Essenciais:

   - Módulos que implementam a funcionalidade RAG principal
   - Serviços de busca semântica
   - Integração com LLM
   - Gerenciamento de embeddings
   - Processamento de documentos

2. Infraestrutura Crítica:

   - Configurações de ambiente
   - Gerenciamento de conexões
   - Tratamento de erros essenciais
   - Logging de operações críticas

3. Interfaces Principais:
   - API endpoints essenciais
   - Modelos de dados core
   - Schemas principais
   - Tipos e constantes fundamentais

### O que NÃO é Core?

1. Ferramentas de Suporte:

   - Scripts de CLI
   - Utilitários de desenvolvimento
   - Ferramentas de teste
   - Scripts de manutenção

2. Funcionalidades Auxiliares:

   - Interfaces de administração
   - Ferramentas de debug
   - Scripts de deploy
   - Monitoramento e métricas

3. Documentação e Recursos:
   - Arquivos markdown
   - Exemplos e tutoriais
   - Assets e recursos estáticos
   - Configurações de desenvolvimento

## Regras de Avaliação

### Critérios para Core

1. Impacto Operacional:

   - É essencial para o funcionamento básico do sistema?
   - Uma falha aqui compromete toda a aplicação?
   - Outros componentes dependem diretamente deste?

2. Responsabilidade Funcional:

   - Implementa lógica de negócio essencial?
   - Gerencia recursos críticos?
   - É parte da pipeline principal de processamento?

3. Acoplamento:
   - Quantos outros componentes dependem deste?
   - Qual o impacto de mudanças aqui?
   - É fundamental para a arquitetura?

### Estrutura do Core

```
backend_rag_ia/
├── api/          # Endpoints essenciais
├── config/       # Configurações core
├── models/       # Modelos de dados
├── services/     # Serviços principais
└── utils/        # Utilitários essenciais
```

### Exemplos Práticos

#### É Core:

- `backend_rag_ia/services/semantic_search.py`
- `backend_rag_ia/models/document.py`
- `backend_rag_ia/config/env_config.py`
- `backend_rag_ia/api/search_endpoints.py`

#### Não é Core:

- `tools/cli/busca_semantica.py`
- `scripts_apenas_raiz/deploy.py`
- `testes_apenas_raiz/test_search.py`
- `monitoring_apenas_raiz/check_api.py`

## Processo de Avaliação

1. Análise Inicial:

   - Verificar localização do arquivo/componente
   - Identificar dependências diretas
   - Avaliar função principal

2. Aplicar Critérios:

   - Checar impacto operacional
   - Verificar responsabilidade funcional
   - Analisar acoplamento

3. Decisão:
   - Classificar como core ou não-core
   - Documentar razão da classificação
   - Validar com equipe se necessário

## Manutenção

1. Revisão Regular:

   - Reavaliar classificações periodicamente
   - Atualizar documentação quando necessário
   - Ajustar critérios conforme evolução

2. Refatoração:
   - Mover componentes não-core para fora do core
   - Consolidar funcionalidades core
   - Manter separação clara
