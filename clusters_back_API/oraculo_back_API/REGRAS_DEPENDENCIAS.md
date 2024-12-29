# Regras para Verificação de Compatibilidade de Dependências

## Informações do Projeto

### Servidor de Produção Atual

- **Plataforma**: Render.com
- **SSH**: `srv-ctmtqra3esus739sknb0@ssh.oregon.render.com`
- **Região**: Oregon (US West)
- **Tipo**: Web Service

### Recomendação de Região

Para melhor performance no Brasil, é recomendado usar:

- **Região**: São Paulo (sa1)
- **Provedor**: AWS South America (São Paulo)
- **Benefícios**:
  - Menor latência para usuários brasileiros
  - Melhor tempo de resposta
  - Conformidade com LGPD (Lei Geral de Proteção de Dados)

> **Nota**: Considerar migração do servidor de Oregon para São Paulo para otimizar a performance para usuários brasileiros.

## 1. Análise Inicial

1. Primeiro, liste todas as dependências em grupos funcionais:

   - Framework principal (ex: FastAPI, Uvicorn)
   - Bibliotecas de ML/IA
   - Banco de dados
   - Utilitários
   - Cache/Performance
   - Testes

2. Identifique as dependências críticas que são base para outras:
   - FastAPI → Starlette, Pydantic
   - Langchain → Hugging Face, transformers
   - Supabase → httpx

## 2. Verificação de Versões

1. Use o comando `pip index versions` para cada dependência crítica:

   ```bash
   pip index versions fastapi | grep -A 1 "Available versions:"
   ```

2. Para dependências relacionadas, verifique a compatibilidade em cascata:
   - Se atualizar FastAPI, verifique Pydantic
   - Se atualizar Langchain, verifique sentence-transformers

## 3. Teste de Compatibilidade

1. Use `pip install --dry-run` para testar a instalação sem efetivamente instalar:

   ```bash
   pip install -r requirements.txt --dry-run
   ```

2. Se houver conflitos, o comando mostrará mensagens como:
   ```
   ERROR: Cannot install package1==1.0.0 and package2==2.0.0 because these package versions have conflicting dependencies.
   ```

## 4. Resolução de Conflitos

1. Para conflitos diretos (ex: httpx e supabase):

   - Identifique a versão comum que satisfaz ambas as dependências
   - Use ranges de versão quando possível: `package>=1.0.0,<2.0.0`

2. Para conflitos em cascata:
   - Comece pela dependência mais fundamental
   - Trabalhe subindo na hierarquia de dependências

## 5. Boas Práticas

1. Sempre especifique versões exatas para:

   - Framework principal
   - Bibliotecas de ML/IA
   - Banco de dados

2. Use ranges de versão apenas quando necessário para:

   - Utilitários
   - Bibliotecas de suporte

3. Mantenha um registro de mudanças:
   ```
   # Exemplo de atualização:
   # FastAPI: 0.104.1 → 0.115.6 (compatibilidade com Pydantic 2.x)
   # Supabase: 1.0.3 → 2.3.4 (requer httpx>=0.24.0,<0.26.0)
   ```

## 6. Processo de Atualização

1. Faça um backup do requirements.txt atual

2. Atualize as dependências em ordem:

   - Framework principal
   - Bibliotecas críticas
   - Dependências secundárias

3. Teste a instalação com `--dry-run` antes de commitar

4. Documente todas as mudanças significativas

## 7. Monitoramento

1. Configure alertas de segurança no GitHub:

   - Dependabot
   - Renovate

2. Revise atualizações de segurança regularmente

3. Mantenha um ambiente de testes para validar atualizações

## 8. Troubleshooting

Se encontrar conflitos:

1. Verifique o log de erro completo
2. Identifique as dependências em conflito
3. Consulte a documentação oficial
4. Use `pip debug` para mais informações
5. Considere usar ambientes virtuais para testes

## 9. Ferramentas Úteis

- `pip-tools`: Para gerenciar dependências
- `pipdeptree`: Para visualizar árvore de dependências
- `safety`: Para verificar vulnerabilidades conhecidas

## 10. Checklist Final

- [ ] Todas as versões são compatíveis
- [ ] Não há conflitos de dependências
- [ ] Vulnerabilidades foram verificadas
- [ ] Mudanças foram documentadas
- [ ] Testes foram executados
- [ ] Backup foi realizado
