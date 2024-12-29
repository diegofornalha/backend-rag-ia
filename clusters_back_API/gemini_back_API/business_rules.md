# Regras de Negócio - API Gemini Backend

## 1. Configurações do Servidor

- Porta padrão: 8000
- Debug mode ativado por padrão
- Hot-reload ativado
- Host: '0.0.0.0'

## 2. Segurança e CORS

### Origens Permitidas:

- http://localhost:2000
- http://127.0.0.1:2000
- Endpoint `/health` permite qualquer origem

### Métodos HTTP:

- POST e OPTIONS para endpoints Gemini

## 3. Regras do Gemini

- Limite máximo: 300 caracteres por mensagem
- Idioma: Português do Brasil (obrigatório)
- Requer API key do Google no .env
- Modelo: 'gemini-1.5-flash'

## 4. Estrutura e Isolamento

### Isolamento Total do Frontend

- Backend 100% isolado
- Proibido misturar código frontend
- Proibido adicionar templates/arquivos estáticos
- Proibido criar dependências frontend
- Proibido compartilhar recursos

### Comunicação Permitida

- Apenas via API REST
- Endpoints documentados
- CORS configurado
- Respostas exclusivamente em JSON

## 5. Documentação

- Swagger UI em `/docs`
- Especificação OpenAPI em `/swagger`
- Documentação obrigatória para novos endpoints

## 6. Tratamento de Erros

- Tratamento obrigatório em todos endpoints
- Respostas de erro padronizadas em JSON
- Códigos HTTP apropriados por situação

## 7. Ambiente de Desenvolvimento

- Uso obrigatório de ambiente virtual Python (.venv)
- Manutenção do requirements_backend.txt
- Configuração via .env
- Estrutura em clusters

## 8. Endpoints Principais

- `/health`: Monitoramento
- `/gemini/chat`: Integração Gemini
- `/`: Redirecionamento para docs
- `/docs`: Interface Swagger
- `/swagger`: Spec OpenAPI

## 9. Validações

- Verificação de JSON válido
- Validação de tamanho (máx 300 chars)
- Tratamento de exceções Gemini

## 10. Configurações Environment

### Classe Settings

```python
class Settings:
    # Flask
    DEBUG: bool = os.getenv("FLASK_DEBUG", "1") == "1"
    PORT: int = int(os.getenv("PORT", "8000"))
    HOST: str = os.getenv("HOST", "0.0.0.0")

    # API
    APP_NAME: str = os.getenv("APP_NAME", "Gemini API")
    APP_VERSION: str = os.getenv("APP_VERSION", "1.0.0")

    # Gemini
    GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY")

    # Swagger
    SWAGGER_URL: str = os.getenv("SWAGGER_URL", "/docs")
    API_URL: str = os.getenv("API_URL", "/swagger")
```

## 11. Boas Práticas

- Configurações principais via .env
- Valores padrão para configs essenciais
- Configurações centralizadas na classe Settings
- Estrutura organizada e modular
- Manutenção da independência dos serviços

## 12. Riscos e Proibições

### Riscos de Quebrar Isolamento:

- Perda de independência
- Problemas de manutenção
- Problemas de escalabilidade
- Vulnerabilidades de segurança

### Proibições Expressas:

- Uso de Vue.js
- Conteúdo misto (server-side/client-side)
- Dependências frontend no backend
