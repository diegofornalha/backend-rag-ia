# Problemas Conhecidos na Busca Semântica

## 1. Incompatibilidades

### Python 3.12

- **Problema**: Segmentation fault ao usar sentence-transformers/torch
- **Solução**: Usar Python 3.11 ou inferior
- **Prevenção**: Especificar versão no `pyproject.toml` e `Dockerfile`

### NumPy 2.x

- **Problema**: Erro de compatibilidade com módulos compilados
- **Solução**: Usar NumPy 1.24.3
- **Prevenção**: Fixar versão no requirements.txt

## 2. Ambiente

### Docker e .env

- **Problema**: Falha ao ler variáveis de ambiente
- **Solução**: Implementar fallback ou usar ENV
- **Exemplo**:
  ```python
  SUPABASE_URL = os.getenv("SUPABASE_URL") or "valor_padrao"
  ```

## 3. Supabase

### match_documents

- **Problema**: Parâmetros específicos requeridos
- **Solução**: Seguir formato:
  ```sql
  match_documents(
    query_embedding: vector,
    match_count: int,
    match_threshold: float
  )
  ```

### Busca Textual

- **Problema**: `textSearch` não disponível
- **Solução**: Usar `ilike` ou full-text search
- **Exemplo**:
  ```python
  docs = supabase.table("documents").ilike("content", f"%{query}%")
  ```
