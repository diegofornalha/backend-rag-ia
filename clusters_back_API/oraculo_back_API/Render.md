# Deploy no Render

## Pré-requisitos

- Conta no Render (https://render.com)
- Repositório Git com o código do Oráculo API
- Dockerfile configurado (já incluído no projeto)

## Configuração no Render

1. Acesse o Dashboard do Render
2. Clique em "New +" e selecione "Web Service"
3. Conecte seu repositório Git
4. Configure o serviço:
   - Nome: `oraculo-back-api`
   - Environment: `Docker`
   - Branch: `main` (ou sua branch de produção)
   - Root Directory: `clusters_back_API/oraculo_back_API`
   - Docker Command: deixe vazio (usará o CMD do Dockerfile)

## Variáveis de Ambiente

Configure as seguintes variáveis no Render:

```env
ENVIRONMENT=production
DEBUG=false
PORT=10000
HOST=0.0.0.0
WORKERS=4
SUPABASE_URL=seu_supabase_url
SUPABASE_KEY=sua_supabase_key
LOG_LEVEL=INFO
```

## ⚠️ Importante

- O deploy **DEVE** ser feito usando Docker
- A porta configurada no Render deve ser 10000
- Certifique-se de que todas as variáveis de ambiente estão configuradas
- O serviço usa a URL fornecida pelo Render automaticamente

## Verificando o Deploy

1. Após o deploy, acesse a URL fornecida pelo Render
2. Teste o endpoint de saúde: `GET /health`
3. Verifique os logs no dashboard do Render

## Troubleshooting

Se encontrar problemas:

1. Verifique os logs do container no Render
2. Confirme se todas as variáveis de ambiente estão configuradas
3. Verifique se o Dockerfile está sendo construído corretamente
4. Certifique-se de que a porta 10000 está exposta e configurada
