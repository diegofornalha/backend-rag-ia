# Integração com Serviços Externos

## 1. Supabase

### 1.1 Configuração

- Verificar URLs e chaves de acesso
- Validar permissões e roles
- Testar conexão antes do deploy

### 1.2 Variáveis de Ambiente

```env
SUPABASE_URL="https://seu-projeto.supabase.co"
SUPABASE_KEY="sua-chave-de-acesso"
SUPABASE_JWT_SECRET="seu-jwt-secret"
```

### 1.3 Boas Práticas

- Manter credenciais seguras
- Usar variáveis de ambiente
- Implementar retry em falhas de conexão

## 2. LangChain

### 2.1 Configuração

- Configurar endpoints corretos
- Validar chaves de API
- Definir diretório de cache

### 2.2 Variáveis de Ambiente

```env
LANGCHAIN_API_KEY="sua-chave-api"
LANGCHAIN_ENDPOINT="https://api.langchain.com"
LANGCHAIN_PROJECT="seu-projeto"
LANGCHAIN_CACHE_DIR="/app/cache/langchain"
```

## 3. Validações e Testes

### 3.1 Checklist de Integração

- [ ] Testar conexões
- [ ] Validar credenciais
- [ ] Verificar permissões
- [ ] Testar endpoints principais

### 3.2 Monitoramento

- Implementar logs de erro
- Monitorar tempo de resposta
- Alertar em falhas de conexão

## 4. Troubleshooting

### 4.1 Problemas Comuns

- Credenciais inválidas
- Timeouts de conexão
- Permissões insuficientes

### 4.2 Soluções

- Verificar variáveis de ambiente
- Testar conexão direta
- Validar configurações de rede
