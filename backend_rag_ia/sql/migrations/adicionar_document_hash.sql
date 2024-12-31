-- Adicionar coluna document_hash
ALTER TABLE rag.knowledge_base 
ADD COLUMN IF NOT EXISTS document_hash TEXT;

-- Criar índice para busca rápida
CREATE INDEX IF NOT EXISTS idx_document_hash 
ON rag.knowledge_base(document_hash);

-- Adicionar constraint de unicidade
ALTER TABLE rag.knowledge_base 
ADD CONSTRAINT unique_document_hash UNIQUE (document_hash);

-- Atualizar hashes existentes
UPDATE rag.knowledge_base 
SET document_hash = encode(sha256(content::bytea), 'hex')
WHERE document_hash IS NULL; 