# Regras Principais do Projeto

> ⚠️ Este documento é um índice das regras fundamentais do projeto.
> Para detalhes específicos, consulte os arquivos referenciados.

## 1. Ambiente de Desenvolvimento

- **Sistema**: macOS (ARM)
- **Stack**: Python + FastAPI
- **Padrão**: Server-side first

## 2. Regras Fundamentais

1. **Idioma**:

   - Documentação em português BR
   - Código em inglês
   - Commits em inglês

2. **Organização**:

   - Frontend em `API_frontend_flask`
   - APIs em `clusters_API`
   - Documentação em `regras_md`

3. **Proibições**:
   - ❌ Vue.js no frontend
   - ❌ Mistura server-side/client-side
   - ❌ Duplicação de código

## 3. Documentos Relacionados

1. [Docker](./docker/REGRAS_DOCKER_VERIFICACAO.md)

   - Regras de build
   - Verificação de imagens
   - Deploy

2. [Verificação](./REGRAS_VERIFICACAO_DUPLA.md)

   - Processo de verificação
   - Documentação necessária
   - Exemplos

3. [Desenvolvimento](./desenvolvimento/PERGUNTAS_FREQUENTES.md)

   - FAQ
   - Próximos passos
   - Troubleshooting

4. [Exemplos](./exemplos/DOCSTRING_EXEMPLO.md)
   - Padrões de código
   - Documentação
   - Boas práticas

## 4. Fluxo de Trabalho

1. **Antes de Criar**:

   - Verificar duplicidade
   - Consultar documentação
   - Seguir padrões

2. **Antes de Remover**:

   - Verificar utilidade
   - Consultar desenvolvedor
   - Documentar motivo

3. **Ao Modificar**:
   - Fazer verificação dupla
   - Atualizar documentação
   - Testar mudanças
