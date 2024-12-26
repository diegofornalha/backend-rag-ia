# Frontend do Chat

Este é o frontend da aplicação de chat, construído com React + TypeScript + Vite.

## Funcionalidades

- Interface de chat com campo de mensagem e resposta
- Seletor de ambiente (Local/Render)
- Indicador de status da conexão
- Interface responsiva com Material-UI

## Requisitos

- Node.js (versão 14 ou superior)
- npm (gerenciador de pacotes do Node.js)

## Como executar localmente

1. Certifique-se que o backend está rodando em `http://localhost:8000`

2. Instale as dependências:

```bash
npm install
```

3. Execute o projeto em modo de desenvolvimento:

```bash
npm run dev
```

O frontend estará disponível em `http://localhost:3000`

## Ambientes Disponíveis

O aplicativo possui dois ambientes configurados:

1. **Ambiente Local**

   - URL: `http://localhost:8000`
   - Usado para desenvolvimento e testes locais

2. **Ambiente Render**
   - URL: `https://seu-backend-no-render.onrender.com`
   - Usado para produção no Render

Você pode alternar entre os ambientes usando o seletor na interface do aplicativo.

## Scripts Disponíveis

- `npm run dev`: Inicia o servidor de desenvolvimento
- `npm run build`: Gera a build de produção
- `npm run preview`: Visualiza a build de produção localmente

## Deploy no Render

1. Conecte seu repositório ao Render
2. Crie um novo Web Service
3. Configure as seguintes opções:
   - Build Command: `npm install && npm run build`
   - Start Command: `npm run preview`
   - Environment Variables: Não são necessárias, pois as URLs estão configuradas no código
