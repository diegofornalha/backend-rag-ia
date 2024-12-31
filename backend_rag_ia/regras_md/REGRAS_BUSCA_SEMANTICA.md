# Regras de Busca Semântica

> ⚠️ Este documento é um índice das regras relacionadas à busca semântica.
> Para detalhes específicos, consulte os arquivos referenciados.

## 1. Visão Geral

- **Objetivo**: Implementar busca semântica eficiente e resiliente
- **Modelo**: `all-MiniLM-L6-v2`
- **Stack**: Python 3.11 + Supabase + pgvector

## 2. Documentos Relacionados

1. [Problemas Conhecidos](./busca/PROBLEMAS_CONHECIDOS.md)

   - Incompatibilidades
   - Soluções e prevenções
   - Troubleshooting comum

2. [Configuração](./busca/CONFIGURACAO.md)

   - Versões das dependências
   - Setup do ambiente
   - Configuração do Supabase

3. [Processo de Busca](./busca/PROCESSO.md)

   - Fluxo principal
   - Sistema de fallback
   - Boas práticas

4. [Manutenção](./busca/MANUTENCAO.md)
   - Monitoramento
   - Índices
   - Performance

## 3. Regras Essenciais

1. **Versões Fixas**:

   - Python 3.11
   - NumPy 1.24.3
   - Demais versões em [Configuração](./busca/CONFIGURACAO.md)

2. **Fallbacks Obrigatórios**:

   - Busca textual como backup
   - Tratamento de erros
   - Logs detalhados

3. **Manutenção**:
   - Documentar novos problemas
   - Atualizar soluções
   - Manter exemplos práticos
