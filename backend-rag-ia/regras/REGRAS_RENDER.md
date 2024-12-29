# Deploy no Render

````

## ⚠️ Importante

- O deploy **DEVE** ser feito usando Docker
- A porta configurada no Render deve ser 10000
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

## Estrutura de Arquivos para Deploy

### Arquivos Essenciais

- `requirements.txt`:
  - **Para deploy**: Deve estar na raiz do projeto para ser detectado pelo Render
  - **Para ambiente local**: Pode estar em qualquer diretório, desde que você especifique o caminho correto ao rodar `pip install -r path/to/requirements.txt`
- `Dockerfile` (se estiver usando containers)
- `.env` para variáveis de ambiente (não commitar)

### Ambiente Local vs Deploy

#### Ambiente Local

```bash
# Estando na pasta do projeto
cd backend-rag-ia
pip install -r requirements.txt  # ou especifique o caminho completo
python main.py
````

#### Deploy no Render

- O Render procura automaticamente pelo requirements.txt na raiz
- Se estiver usando Docker, o Dockerfile deve copiar o requirements.txt para o local correto

### Configuração do Serviço

- Nome do serviço: coflow
- Região: Oregon (us-west)
- Tipo: Web Service
- Branch: main

### Variáveis de Ambiente

Configurar no dashboard do Render:

- `SUPABASE_URL`
- `SUPABASE_KEY`
- Outras variáveis sensíveis

### Comandos de Build

```bash
pip install -r requirements.txt
```

### Comandos de Start

```bash
gunicorn main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT
```

### Monitoramento

- Verificar logs no dashboard
- Configurar alertas de erro
- Monitorar uso de recursos

### Troubleshooting

- Verificar logs de build
- Verificar logs de runtime
- Testar localmente antes do deploy

### SSH Access

- Endereço: srv-ctmtqra3esus739sknb0@ssh.oregon.render.com
- Usar para debugging e manutenção
