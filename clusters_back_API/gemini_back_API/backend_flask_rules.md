# Regras do Backend Flask

## 1. Execução do Servidor

- ⚠️ **NÃO execute** `python3 run_back_gemeni.py` se o servidor já estiver rodando
- O servidor tem hot-reload ativado e atualizará automaticamente quando houver mudanças
- Para verificar se o servidor está rodando, acesse:
  - http://localhost:8000/health
  - Ou verifique a saída no terminal com a mensagem "🚀 Iniciando servidor backend..."

## 2. Desenvolvimento

- Todas as respostas do Gemini devem ser em português do Brasil
- Máximo de 300 caracteres por mensagem
- CORS configurado para portas 2000 e 3000
- Sempre use tratamento de erros nos endpoints

## 3. Boas Práticas

- Mantenha o código organizado em clusters
- Separe responsabilidades entre server-side e client-side
- Documente novos endpoints no Swagger
- Mantenha as variáveis de ambiente atualizadas no `.env`

## 4. Ambiente de Desenvolvimento

- Use ambiente virtual Python (`.venv`)
- Mantenha `requirements_backend.txt` atualizado
- Debug mode está ativado por padrão
- Servidor roda na porta 8000

## ⚠️ 1. Isolamento Total do Frontend

❗❗❗ **OBRIGATÓRIO**: Backend 100% isolado:

- **NUNCA** misturar código frontend
- **NUNCA** adicionar templates/arquivos estáticos
- **NUNCA** criar dependências
- **NUNCA** compartilhar recursos

✅ **Comunicação Permitida**:

- API REST com endpoints documentados
- CORS configurado
- Apenas JSON

⚠️ **Riscos de Quebrar Isolamento**:

- Perda de independência
- Problemas de manutenção/escalabilidade
- Vulnerabilidades

## 2. Arquitetura

### API REST

- Apenas JSON, sem templates
- Documentação Swagger UI
- Porta 8000 dedicada
- CORS habilitado

### Estrutura Isolada

- Pasta `gemini_back_API/`
- Configs próprias (.env, settings.py)
- requirements_backend.txt separado
- Sem dependências externas

## 3. Responsabilidades

### Backend

- Lógica de negócio
- Queries de banco
- Processamento de dados/requisições

## 4. Monitoramento

Endpoint `/health`:

- Verifica status online
- Debug de conexão
- Integração com serviços

## 5. Configurações

❗ Pasta `config` (CRÍTICA):

- settings.py centralizado
- Variáveis de ambiente
- Valores padrão seguros

## 6. Preservação de Recursos

Antes de remover funcionalidades:

1. Avaliar utilidade prática
2. Consultar desenvolvedor
3. Justificar remoção
4. Aguardar aprovação
