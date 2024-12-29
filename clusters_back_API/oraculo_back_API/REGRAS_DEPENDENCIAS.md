# Regras para Verificar Versões de Dependências

## 1. Análise Inicial

- Verificar todas as dependências listadas no `requirements.txt`
- Identificar versões atuais e últimas versões disponíveis
- Documentar dependências críticas para o sistema

## 2. Verificação de Versões

- Usar `pip index versions [pacote]` para verificar versões disponíveis
- Verificar changelogs para mudanças significativas
- Identificar breaking changes entre versões

## 3. Testes de Compatibilidade

- Realizar testes de instalação com `--dry-run`
- Verificar conflitos entre dependências
- Testar em ambiente isolado antes de produção

## 4. Resolução de Conflitos

- Documentar conflitos encontrados
- Ajustar versões para resolver incompatibilidades
- Manter registro de decisões tomadas

## 5. Boas Práticas

- Sempre especificar versões exatas (exceto quando necessário range)
- Manter arquivo de requirements organizado por categorias
- Incluir comentários para decisões importantes

## 6. Processo de Atualização

- Criar branch específica para atualizações
- Testar mudanças em ambiente de desenvolvimento
- Documentar processo de rollback se necessário

## 7. Monitoramento de Segurança

- Usar `safety check` para verificar vulnerabilidades
- Manter registro de vulnerabilidades conhecidas
- Planejar atualizações de segurança

### Vulnerabilidades Conhecidas

1. gunicorn==21.2.0
   - CVE-2024-1135: Validação inadequada de headers Transfer-Encoding
   - Impacto: Possível HTTP Request Smuggling (HRS)
   - Observação: Mantida versão 21.2.0 por ser mais estável. Versão 22.0.0 também apresenta vulnerabilidades similares.
   - Mitigação: Usar em conjunto com proxy reverso que valida headers adequadamente

## 8. Ferramentas Úteis

- pip-tools para gerenciamento de dependências
- safety para verificação de segurança
- pip-audit para auditoria de dependências

## 9. Informações do Servidor de Produção

- Plataforma: Render
- SSH: ssh srv-ctmtqra3esus739sknb0@ssh.oregon.render.com
- Região: Oregon (US West)
- Tipo: Web Service
