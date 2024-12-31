# Configuração da Busca Semântica

## 1. Dependências

### Versões Específicas

```
sentence-transformers==2.2.2
torch==2.0.1
transformers==4.30.2
huggingface-hub==0.16.4
supabase==1.0.3
rich==13.4.2
python-dotenv==1.0.0
numpy==1.24.3
```

### Ambiente Python

- Versão: 3.11
- Virtual env recomendado
- Pip atualizado

## 2. Supabase

### Configuração

- Habilitar pgvector
- Criar índices necessários
- Configurar chave de serviço

### Modelo

- Nome: `all-MiniLM-L6-v2`
- Dimensão: 384
- Cache: Habilitado

## 3. Docker

### Dockerfile

```dockerfile
FROM python:3.11-slim
# ... demais configurações em REGRAS_DOCKER.md
```

### Variáveis

- Usar ENV para produção
- Fallback para desenvolvimento
- Documentar valores padrão
