# Regras de Deploy

## 1. Deploys Vazios

- ❌ **Deploys vazios são proibidos**
- Cada deploy deve conter mudanças reais nos arquivos
- Commits vazios (`--allow-empty`) não são permitidos
- O deploy só deve ser feito quando houver alterações significativas no código

## 2. Boas Práticas

### Antes do Deploy

1. Verificar se há alterações reais nos arquivos
2. Testar localmente as mudanças
3. Garantir que os testes passam
4. Verificar a qualidade do código (linting)

### Durante o Deploy

1. Usar mensagens de commit descritivas
2. Incluir o tipo de mudança no commit (feat, fix, docs, etc)
3. Referenciar issues ou tickets relacionados

### Após o Deploy

1. Verificar os logs do servidor
2. Confirmar que a API está saudável
3. Validar as mudanças no ambiente de produção

## 3. Tipos de Deploy Permitidos

- ✅ Novas funcionalidades (feat)
- ✅ Correções de bugs (fix)
- ✅ Melhorias de documentação (docs)
- ✅ Refatorações (refactor)
- ✅ Melhorias de performance (perf)
- ✅ Melhorias de estilo (style)
- ✅ Testes (test)

## 4. Monitoramento

- Usar o endpoint `/health` para verificar o status da API
- Monitorar os logs para identificar problemas
- Verificar métricas de performance
- Acompanhar o uso de recursos

## 5. Rollback

Em caso de problemas após o deploy:

1. Identificar o commit problemático
2. Reverter para a versão anterior estável
3. Investigar a causa do problema
4. Corrigir e fazer um novo deploy com a solução

---

**Observação**: Estas regras devem ser seguidas por todos os desenvolvedores para manter a qualidade e estabilidade do sistema.
