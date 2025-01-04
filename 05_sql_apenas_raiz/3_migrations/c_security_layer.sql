-- Adicionar coluna content_hash se não existir
ALTER TABLE rag."01_base_conhecimento_regras_geral" 
ADD COLUMN IF NOT EXISTS content_hash TEXT GENERATED ALWAYS AS (encode(sha256(conteudo::bytea), 'hex')) STORED;

-- Criar índice para busca rápida
CREATE INDEX IF NOT EXISTS idx_content_hash 
ON rag."01_base_conhecimento_regras_geral"(content_hash);

-- Adicionar constraint de unicidade
ALTER TABLE rag."01_base_conhecimento_regras_geral" 
ADD CONSTRAINT unique_content_hash UNIQUE (content_hash, owner_id);

-- Atualizar hashes existentes (não necessário pois é GENERATED ALWAYS)
-- Mantido como comentário para referência
-- UPDATE rag."01_base_conhecimento_regras_geral" 
-- SET content_hash = encode(sha256(conteudo::bytea), 'hex')
-- WHERE content_hash IS NULL; 