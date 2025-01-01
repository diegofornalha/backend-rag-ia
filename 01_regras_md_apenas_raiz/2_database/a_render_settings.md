# Configurações do PostgreSQL para Render

Este documento contém as configurações necessárias para o PostgreSQL no ambiente Render.

⚠️ **IMPORTANTE**: Estes comandos devem ser executados:

- Um por vez
- Via linha de comando (psql)
- Com privilégios de superusuário
- Fora de blocos de transação

## Configurações de Timeout

```sql
ALTER SYSTEM SET statement_timeout = '30s';                    -- ⚠️ NUNCA aumentar além de 30s
ALTER SYSTEM SET idle_in_transaction_session_timeout = '15s';  -- ⚠️ CRÍTICO para evitar conexões zumbis
ALTER SYSTEM SET client_min_messages = 'warning';              -- Reduz ruído nos logs
ALTER SYSTEM SET timezone = 'UTC';                            -- ⚠️ SEMPRE manter em UTC
```

## Pool de Conexões

```sql
ALTER SYSTEM SET max_connections = '100';                      -- ⚠️ Limite máximo do Render
ALTER SYSTEM SET superuser_reserved_connections = '3';         -- Reserva para manutenção
```

## Configurações de Memória

```sql
ALTER SYSTEM SET shared_buffers = '128MB';                    -- ⚠️ Limite máximo do Render
ALTER SYSTEM SET work_mem = '4MB';                            -- ⚠️ NUNCA aumentar sem análise
ALTER SYSTEM SET maintenance_work_mem = '64MB';               -- Para operações de manutenção
```

## Write-Ahead Logging (WAL)

```sql
ALTER SYSTEM SET wal_level = 'replica';                       -- ⚠️ Necessário para backup
ALTER SYSTEM SET max_wal_size = '1GB';                        -- ⚠️ Ajustar conforme uso
ALTER SYSTEM SET min_wal_size = '80MB';                       -- Mínimo recomendado
```

## Checkpoints

```sql
ALTER SYSTEM SET checkpoint_timeout = '5min';                 -- ⚠️ Balancear com WAL
ALTER SYSTEM SET checkpoint_completion_target = '0.9';        -- Distribuir I/O
```

## Autovacuum

```sql
ALTER SYSTEM SET autovacuum = on;                            -- ⚠️ NUNCA desabilitar
ALTER SYSTEM SET autovacuum_max_workers = '3';               -- Limite para recursos
ALTER SYSTEM SET autovacuum_naptime = '1min';                -- Frequência de verificação
```

## Monitoramento

```sql
ALTER SYSTEM SET track_activities = on;                      -- ⚠️ Necessário para diagnóstico
ALTER SYSTEM SET track_counts = on;                          -- Estatísticas de vacuum
ALTER SYSTEM SET track_io_timing = on;                       -- Performance I/O
ALTER SYSTEM SET track_functions = 'all';                    -- Monitoramento de funções
```

## Extensões Necessárias

```sql
CREATE EXTENSION IF NOT EXISTS pg_stat_statements;            -- Monitoramento de queries
CREATE EXTENSION IF NOT EXISTS pgcrypto;                     -- Segurança
CREATE EXTENSION IF NOT EXISTS vector;                       -- Embeddings
```

## Função de Monitoramento de Saúde

```sql
CREATE OR REPLACE FUNCTION check_render_health()
RETURNS TABLE (
    component text,
    status text,
    details jsonb
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        'database'::text as component,
        CASE
            WHEN pg_is_in_recovery() THEN 'standby'
            ELSE 'primary'
        END as status,
        jsonb_build_object(
            'connections', (SELECT count(*) FROM pg_stat_activity),
            'size', pg_size_pretty(pg_database_size(current_database())),
            'uptime', (SELECT date_trunc('second', current_timestamp - pg_postmaster_start_time()))::text,
            'last_vacuum', (
                SELECT max(last_vacuum)::text
                FROM pg_stat_user_tables
            ),
            'active_queries', (
                SELECT count(*)
                FROM pg_stat_activity
                WHERE state = 'active'
            )
        ) as details;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;
```

## Problemas Conhecidos e Soluções

1. **Erro**: "ALTER SYSTEM cannot run inside a transaction block"
   **Solução**:

   - Executar comandos ALTER SYSTEM separadamente
   - Nunca incluir ALTER SYSTEM dentro de BEGIN/COMMIT
   - Executar ALTER SYSTEM como primeira operação

2. **Erro**: Conflitos de Extensões
   **Solução**:
   - Executar CREATE EXTENSION IF NOT EXISTS no início
   - Executar cada extensão separadamente
   - Ordem recomendada:
     1. vector
     2. pgcrypto
     3. pg_stat_statements

## Limitações do Render

- Máximo de 100 conexões simultâneas
- Timeout máximo de 30 segundos por query
- Memória compartilhada limitada a 128MB
- Necessidade de configuração específica para WAL
