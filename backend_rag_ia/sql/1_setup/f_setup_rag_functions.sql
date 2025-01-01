-- Define o schema padrão
SET search_path TO public;

-- Habilita a extensão vector
CREATE EXTENSION IF NOT EXISTS vector;

-- Remove funções existentes
DROP FUNCTION IF EXISTS generate_embedding(text);
DROP FUNCTION IF EXISTS match_documents(vector, float, int);

-- Cria tabela base de conhecimento se não existir
CREATE TABLE IF NOT EXISTS base_conhecimento (
    id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
    titulo text NOT NULL,
    conteudo jsonb NOT NULL,
    created_at timestamptz DEFAULT now(),
    updated_at timestamptz DEFAULT now()
);

-- Cria tabela de embeddings se não existir
CREATE TABLE IF NOT EXISTS embeddings (
    id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
    documento_id uuid REFERENCES base_conhecimento(id) ON DELETE CASCADE,
    embedding vector(384) NOT NULL,
    created_at timestamptz DEFAULT now()
);

-- Função para gerar embeddings
CREATE OR REPLACE FUNCTION generate_embedding(input_text text)
RETURNS jsonb
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
    embedding_array float[];
BEGIN
    -- Por enquanto retorna um array de 384 zeros
    -- Isso será substituído pela chamada real ao modelo
    embedding_array := array_fill(0::float, ARRAY[384]);
    RETURN jsonb_build_object('embedding', embedding_array);
END;
$$;

-- Função para buscar documentos similares
CREATE OR REPLACE FUNCTION match_documents(
    query_embedding vector,
    match_threshold float DEFAULT 0.3,
    match_count int DEFAULT 5
)
RETURNS TABLE (
    id uuid,
    documento_id uuid,
    content jsonb,
    similarity float
)
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
BEGIN
    RETURN QUERY
    SELECT
        e.id,
        e.documento_id,
        d.conteudo as content,
        1 - (e.embedding <=> query_embedding) as similarity
    FROM embeddings e
    JOIN base_conhecimento d ON e.documento_id = d.id
    WHERE 1 - (e.embedding <=> query_embedding) > match_threshold
    ORDER BY similarity DESC
    LIMIT match_count;
END;
$$;

-- Cria índice para busca por similaridade
CREATE INDEX IF NOT EXISTS idx_embeddings_embedding ON embeddings USING ivfflat (embedding vector_cosine_ops);

-- Insere dados de exemplo
INSERT INTO base_conhecimento (titulo, conteudo) VALUES
('Regras do Sistema RAG', '{"text": "O sistema RAG (Retrieval Augmented Generation) é composto por três componentes principais: 1) Retrieval: busca semântica e embeddings, 2) Augmentation: enriquecimento e contexto, 3) Generation: processamento LLM e respostas contextualizadas."}'),
('Configuração do Sistema', '{"text": "Para configurar o sistema RAG, é necessário: 1) Configurar Supabase com pgvector, 2) Configurar API do Gemini, 3) Configurar cache de embeddings, 4) Configurar endpoints da API."}'),
('Boas Práticas RAG', '{"text": "Boas práticas para o sistema RAG incluem: 1) Centralizar lógica nos serviços, 2) Usar cache em múltiplas camadas, 3) Implementar fallbacks, 4) Manter consistência entre CLI e API."}');

-- Gera embeddings para os documentos
INSERT INTO embeddings (documento_id, embedding)
SELECT id, (generate_embedding(conteudo->>'text')->>'embedding')::vector
FROM base_conhecimento
WHERE id NOT IN (SELECT documento_id FROM embeddings); 