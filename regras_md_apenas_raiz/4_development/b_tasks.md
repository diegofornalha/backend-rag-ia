# Tarefas de Reorganização das Ferramentas

## 0. Padrão de Nomenclatura

### Diretórios Raiz

1. Diretórios com sufixo `_apenas_raiz` indicam que devem ficar na raiz do projeto
2. Subpastas dentro de diretórios `_apenas_raiz` devem seguir o padrão numérico:
   - Formato: `N_nome_da_pasta` onde N é um número sequencial
   - Exemplo: `1_core`, `2_database`, `3_deployment`, etc.
   - Todas as subpastas devem seguir este padrão sem exceção

### Regras de Arquivos

1. Arquivos dentro das pastas devem seguir o padrão alfabético:
   - Formato: `letra_nome_do_arquivo.extensão`
   - Exemplo: `a_index.md`, `b_tasks.md`, `c_setup.md`, etc.
   - Usar letras minúsculas e underscores
   - Evitar caracteres especiais ou acentos
   - Isso se aplica a TODOS os arquivos, incluindo documentação e configuração

### Regras de Documentação

1. Todos os arquivos markdown (`.md`) devem ficar no diretório `regras_md_apenas_raiz`
2. A documentação é organizada em categorias numeradas:
   - `1_core/` - Documentação do núcleo
   - `2_database/` - Documentação do banco de dados
   - `3_deployment/` - Documentação de implantação
   - `4_development/` - Documentação de desenvolvimento
     - `a_index.md`
     - `b_tasks.md` (anteriormente TASKS.md)
   - `5_monitoring/` - Documentação de monitoramento
   - `6_melhorias/` - Propostas de melhorias
     - `a_llm_improvements.md`
     - `b_rag_improvements.md`
     - `c_autonomy_assessment.md`
     - `d_cache_inteligente.md`
     - `e_feedback_loop.md`
     - `f_otimizacao_de_embeddings.md`

### Consolidação de Diretórios ✅

Alguns diretórios têm funções similares e foram consolidados:

1. `ferramentas_rag_apenas_raiz` + `tools_apenas_raiz` → `/tools` ✅
   - Todas as ferramentas CLI foram movidas para `/tools`
   - Arquivos duplicados foram removidos
   - Mantém organização mais clara e evita duplicação

### Estrutura Final

```
/
├── logs/           # Logs da aplicação
├── monitoring/     # Scripts de monitoramento
├── regras_md/     # Documentação em markdown
├── scripts/       # Scripts utilitários
├── sql/          # Scripts SQL e migrações
├── testes/       # Testes automatizados
└── tools/        # Ferramentas CLI (consolida ferramentas_rag)
    ├── cli/      # Ferramentas de linha de comando
    ├── database/ # Ferramentas de banco de dados
    └── utils/    # Utilitários compartilhados
```

## 1. Ferramentas de Busca Semântica

- [x] Mover e adaptar `e_busca_semantica_terminal_autonoma.py`

  - [x] Criar estrutura de diretórios em `/tools`
  - [x] Remover dependências do core
  - [x] Implementar funções auxiliares locais
  - [x] Testar funcionamento independente

- [x] Mover e adaptar `c_busca_semantica_simples.py`

  - [x] Remover dependências do core
  - [x] Adaptar para uso independente
  - [x] Testar funcionamento

- [x] Mover e adaptar `d_busca_semantica_com_ia.py`
  - [x] Remover dependências do core
  - [x] Adaptar para uso independente
  - [x] Testar funcionamento

## 2. Ferramentas de Banco de Dados

- [x] Mover e adaptar `b_subir_para_supabase.py`

  - [x] Remover dependências do core
  - [x] Adaptar para uso independente
  - [x] Testar funcionamento

- [x] Mover e adaptar `a_limpar_banco.py`
  - [x] Remover dependências do core
  - [x] Adaptar para uso independente
  - [x] Testar funcionamento

## 3. Organização e Documentação

- [x] Criar estrutura de diretórios em `/tools`

  - [x] `/cli` - Ferramentas de linha de comando
  - [x] `/database` - Ferramentas de banco de dados
  - [x] `/utils` - Utilitários compartilhados

- [x] Criar documentação
  - [x] README.md para cada ferramenta
  - [x] Instruções de uso
  - [x] Requisitos e dependências

## 4. Testes e Validação

- [x] Testar cada ferramenta isoladamente
- [x] Verificar se todas as dependências estão documentadas
- [x] Garantir que não há referências ao core
- [x] Validar funcionamento em ambiente limpo

## 5. Limpeza ✅

- [x] Remover arquivos antigos do core
- [x] Atualizar imports nos arquivos que permaneceram
- [x] Remover diretórios vazios
- [x] Atualizar documentação principal

## 6. Próximos Passos

- [ ] Mover todos os arquivos `.md` para `regras_md_apenas_raiz`
- [ ] Organizar documentação por categorias
- [ ] Atualizar referências nos arquivos
