# Chat Application

Uma aplicação de chat completa com frontend React e backend FastAPI.

## 🏗️ Estrutura do Projeto

```
.
├── frontend/     # Frontend React + TypeScript + Vite
└── backend/      # Backend FastAPI + Python
```

## 🚀 Frontend

### Funcionalidades

- Interface de chat com campo de mensagem e resposta
- Seletor de ambiente (Local/Render)
- Indicador de status da conexão
- Interface responsiva com Material-UI

### Requisitos

- Node.js (versão 14 ou superior)
- npm (gerenciador de pacotes do Node.js)

### Scripts

```bash
# Desenvolvimento
npm run dev

# Build de produção
npm run build

# Preview da build
npm run preview

# Testes
npm test

# Build dos testes
npm run test:build

# Execução dos testes
npm run test:run
```

### Ambientes

1. **Local**

   - URL: `http://localhost:8000`
   - Desenvolvimento e testes

2. **Render**
   - URL: `https://seu-backend-no-render.com`
   - Ambiente de produção

## 🛠️ Backend

### Funcionalidades

- API RESTful com FastAPI
- Integração com modelos de IA
- Suporte a WebSockets para chat em tempo real
- Containerização com Docker

### Requisitos

- Python 3.8+
- Docker
- Poetry (gerenciamento de dependências)

### Comandos

```bash
# Instalar dependências
poetry install

# Executar localmente
poetry run uvicorn main:app --reload

# Build do container
docker build -t chat-api .

# Executar container
docker run -p 8000:8000 chat-api
```

## 🚀 Deploy

### Frontend (Render)

1. Conecte seu repositório
2. Crie um Web Service
3. Configure:
   - Build Command: `npm install && npm run build`
   - Start Command: `npm run preview`

### Backend (Render)

1. Conecte seu repositório
2. Crie um Web Service
3. Configure:
   - Build Command: `docker build -t chat-api .`
   - Start Command: `docker run -p 8000:8000 chat-api`
   - Environment Variables: Configure conforme necessário

## 📝 Desenvolvimento

1. Clone o repositório
2. Configure o ambiente de desenvolvimento
3. Execute frontend e backend localmente
4. Faça suas alterações
5. Execute os testes
6. Envie um Pull Request

## 🤝 Contribuição

1. Fork o projeto
2. Crie sua Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a Branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.
