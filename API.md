# Documentação da API do Oráculo 🤖

## Visão Geral

O Oráculo é uma API de chat que utiliza o modelo Gemini 1.0 Pro da Google para gerar respostas inteligentes em português do Brasil.

## Ambientes Disponíveis

- **Desenvolvimento (Local)**

  ```
  http://localhost:8000
  ```

- **Produção (Render)**
  ```
  https://oraculo-api-latest.onrender.com
  ```

## Endpoints

### 1. Chat (POST /api/chat)

Processa mensagens do usuário e retorna respostas do modelo Gemini.

#### Request

```http
POST /api/chat
Content-Type: application/json

{
  "message": "Qual é a diferença entre IA e Machine Learning?"
}
```

#### Response Success (200 OK)

```json
{
  "response": "A Inteligência Artificial (IA) é um campo mais amplo que engloba..."
}
```

#### Response Error (422 Unprocessable Entity)

```json
{
  "detail": [
    {
      "loc": ["body", "message"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

### 2. Health Check (GET /health)

Verifica o status da API e do modelo.

#### Request

```http
GET /health
```

#### Response Success (200 OK)

```json
{
  "status": "healthy",
  "model": "gemini-1.0-pro"
}
```

## Exemplos de Uso

### cURL

```bash
# Chat
curl -X POST "http://localhost:8000/api/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "O que é machine learning?"}'

# Health Check
curl http://localhost:8000/health
```

### Python

```python
import requests

def chat_with_oracle(message: str, base_url: str = "http://localhost:8000"):
    response = requests.post(
        f"{base_url}/api/chat",
        json={"message": message}
    )
    return response.json()

# Exemplo de uso
response = chat_with_oracle("O que é machine learning?")
print(response["response"])
```

### TypeScript/React

```typescript
import axios from "axios";

interface ChatResponse {
  response: string;
}

async function chatWithOracle(
  message: string,
  baseUrl: string = "http://localhost:8000"
): Promise<string> {
  try {
    const response = await axios.post<ChatResponse>(`${baseUrl}/api/chat`, {
      message,
    });
    return response.data.response;
  } catch (error) {
    console.error("Erro:", error);
    throw new Error("Falha ao processar mensagem");
  }
}
```

## Considerações Técnicas

### Limites e Restrições

- Tempo máximo de resposta: 60 segundos
- Tamanho máximo da mensagem: 4096 caracteres
- Rate limit: 60 requisições por minuto
- Cold start no Render: ~50 segundos (plano gratuito)

### CORS

Origens permitidas:

- `http://localhost:3000` (Frontend Dev)
- `http://localhost:5173` (Frontend Dev Vite)
- `https://oraculo-asimov.vercel.app` (Frontend Prod)

### Boas Práticas

1. **Tratamento de Erros**

   - Sempre implemente tratamento de erros
   - Verifique o status da API antes de enviar mensagens
   - Implemente retry com backoff para falhas temporárias

2. **Performance**

   - Cache respostas frequentes
   - Implemente timeout adequado (recomendado: 30s)
   - Considere o cold start no plano gratuito do Render

3. **UX**
   - Mostre feedback de loading durante requisições
   - Mantenha o usuário informado sobre o status da conexão
   - Permita retry em caso de falhas

## Documentação Interativa

- **Swagger UI**: `/docs`
- **ReDoc**: `/redoc`
- **OpenAPI JSON**: `/openapi.json`

## Suporte

Para reportar problemas ou sugerir melhorias:

1. Abra uma issue no GitHub
2. Envie um email para suporte@asimov.academy
3. Acesse nossa comunidade no Discord
