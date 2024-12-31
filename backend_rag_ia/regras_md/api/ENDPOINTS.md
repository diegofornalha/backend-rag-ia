# Endpoints da API

## 1. Estrutura de Rotas

### Base URL

- Desenvolvimento: `http://localhost:10000`
- Produção: `https://api.coflow.com.br`
- Prefixo: `/api/v1`

### Padrões

- Usar substantivos (não verbos)
- Nomes no plural
- Separar palavras com hífen
- Case sensitive

## 2. Endpoints Principais

### Documentos

```
POST   /documents     # Criar documento
GET    /documents     # Listar documentos
GET    /documents/:id # Obter documento
PUT    /documents/:id # Atualizar documento
DELETE /documents/:id # Remover documento
```

### Busca

```
POST /search         # Busca semântica
GET  /search/status  # Status da busca
```

### Sistema

```
GET /health         # Status do sistema
GET /config         # Configurações
```

## 3. Versionamento

### Regras

- Usar prefixo `/v1`, `/v2`, etc
- Manter versões antigas por 6 meses
- Documentar breaking changes

### Breaking Changes

- Mudança de formato de resposta
- Remoção de campos
- Alteração de tipos
