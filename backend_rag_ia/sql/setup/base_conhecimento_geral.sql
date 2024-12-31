-- Habilitar extensão necessária
CREATE EXTENSION IF NOT EXISTS vector;

-- Criar tabela principal de base de conhecimento
CREATE TABLE IF NOT EXISTS "01_base_conhecimento_regras_geral" (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    titulo TEXT NOT NULL,
    conteudo TEXT NOT NULL,
    metadata JSONB DEFAULT '{}'::jsonb,
    owner_id UUID,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Criar tabela de embeddings
CREATE TABLE IF NOT EXISTS "02_embeddings_regras_geral" (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    documento_id UUID NOT NULL REFERENCES "01_base_conhecimento_regras_geral"(id) ON DELETE CASCADE,
    embedding vector(384),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Criar índice para busca por similaridade
CREATE INDEX IF NOT EXISTS embeddings_embedding_idx ON "02_embeddings_regras_geral" 
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);

-- Configurar RLS para a tabela principal
ALTER TABLE IF EXISTS "01_base_conhecimento_regras_geral" ENABLE ROW LEVEL SECURITY;

-- Configurar RLS para a tabela de embeddings
ALTER TABLE IF EXISTS "02_embeddings_regras_geral" ENABLE ROW LEVEL SECURITY;

-- Remover políticas existentes para evitar conflitos
DROP POLICY IF EXISTS select_documentos ON "01_base_conhecimento_regras_geral";
DROP POLICY IF EXISTS insert_documentos ON "01_base_conhecimento_regras_geral";
DROP POLICY IF EXISTS update_documentos ON "01_base_conhecimento_regras_geral";
DROP POLICY IF EXISTS delete_documentos ON "01_base_conhecimento_regras_geral";

DROP POLICY IF EXISTS select_embeddings ON "02_embeddings_regras_geral";
DROP POLICY IF EXISTS insert_embeddings ON "02_embeddings_regras_geral";
DROP POLICY IF EXISTS update_embeddings ON "02_embeddings_regras_geral";
DROP POLICY IF EXISTS delete_embeddings ON "02_embeddings_regras_geral";

-- Criar políticas para a tabela principal
CREATE POLICY select_documentos ON "01_base_conhecimento_regras_geral"
    FOR SELECT
    USING (
        (metadata->>'public')::boolean = true
        OR
        auth.uid() = owner_id
    );

CREATE POLICY insert_documentos ON "01_base_conhecimento_regras_geral"
    FOR INSERT
    WITH CHECK (
        auth.uid() = owner_id
    );

CREATE POLICY update_documentos ON "01_base_conhecimento_regras_geral"
    FOR UPDATE
    USING (
        auth.uid() = owner_id
    );

CREATE POLICY delete_documentos ON "01_base_conhecimento_regras_geral"
    FOR DELETE
    USING (
        auth.uid() = owner_id
    );

-- Criar políticas para a tabela de embeddings
CREATE POLICY select_embeddings ON "02_embeddings_regras_geral"
    FOR SELECT
    USING (
        EXISTS (
            SELECT 1
            FROM "01_base_conhecimento_regras_geral" d
            WHERE d.id = documento_id
            AND (
                (d.metadata->>'public')::boolean = true
                OR
                auth.uid() = d.owner_id
            )
        )
    );

CREATE POLICY insert_embeddings ON "02_embeddings_regras_geral"
    FOR INSERT
    WITH CHECK (
        EXISTS (
            SELECT 1
            FROM "01_base_conhecimento_regras_geral" d
            WHERE d.id = documento_id
            AND auth.uid() = d.owner_id
        )
    );

CREATE POLICY update_embeddings ON "02_embeddings_regras_geral"
    FOR UPDATE
    USING (
        EXISTS (
            SELECT 1
            FROM "01_base_conhecimento_regras_geral" d
            WHERE d.id = documento_id
            AND auth.uid() = d.owner_id
        )
    );

CREATE POLICY delete_embeddings ON "02_embeddings_regras_geral"
    FOR DELETE
    USING (
        EXISTS (
            SELECT 1
            FROM "01_base_conhecimento_regras_geral" d
            WHERE d.id = documento_id
            AND auth.uid() = d.owner_id
        )
    );

-- Função para busca semântica
CREATE OR REPLACE FUNCTION match_documents(
    query_embedding vector,
    match_threshold float DEFAULT 0.8,
    match_count int DEFAULT 5
)
RETURNS TABLE (
    id UUID,
    titulo TEXT,
    conteudo TEXT,
    similarity float
)
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
BEGIN
    RETURN QUERY
    SELECT
        d.id,
        d.titulo,
        d.conteudo,
        1 - (e.embedding <=> query_embedding) as similarity
    FROM "01_base_conhecimento_regras_geral" d
    JOIN "02_embeddings_regras_geral" e ON e.documento_id = d.id
    WHERE 1 - (e.embedding <=> query_embedding) > match_threshold
    ORDER BY e.embedding <=> query_embedding
    LIMIT match_count;
END;
$$; 

-- Inserir novo conhecimento sobre hierarquia de decisões
INSERT INTO "01_base_conhecimento_regras_geral" (titulo, conteudo) 
VALUES (
    'Hierarquia de Decisões: Boas Práticas vs. Preferências',
    'Na tomada de decisões do projeto, as boas práticas de desenvolvimento têm prioridade sobre preferências pessoais. 
    
    Exemplos práticos:
    1. Isolamento de Testes: Mesmo que haja preferência por manter testes junto ao código, a boa prática de isolá-los 
       prevalece pelos benefícios de otimização, segurança e manutenção.
    
    2. Organização de Scripts: A estruturação em categorias específicas segue boas práticas de organização, 
       mesmo que possa haver preferência por uma estrutura mais simples.
    
    3. Limpeza de Código: A remoção de código obsoleto ou duplicado é uma boa prática que se sobrepõe à 
       preferência de manter código "por precaução".
    
    Quando houver conflito entre preferência pessoal e boa prática:
    - Seguir a boa prática estabelecida
    - Documentar a decisão e sua justificativa
    - Explicar os benefícios da abordagem escolhida
    - Manter registro das considerações feitas
    
    As preferências pessoais podem ser aplicadas quando:
    - Não conflitam com boas práticas
    - Não comprometem qualidade ou manutenibilidade
    - Agregam valor ao projeto
    - São bem documentadas'
);

-- Inserir conhecimento sobre organização de código
INSERT INTO "01_base_conhecimento_regras_geral" (titulo, conteudo)
VALUES (
    'Organização e Isolamento de Recursos',
    'A organização do código segue princípios de isolamento e categorização:

    1. Scripts (scripts_apenas_raiz/):
       - Isolados do código principal
       - Organizados por categoria (busca, ambiente, monitoramento)
       - Scripts de organização em pasta separada
       - Facilita manutenção e evita poluição

    2. Testes (testes_apenas_raiz/):
       - Isolados para otimizar imagem de produção
       - Benefícios: build mais rápido, menor consumo de recursos
       - Estrutura organizada em unit, integration, monitoring
       - Inclui fixtures e utils para suporte

    3. SQL (sql/):
       - Organizado por função (setup, maintenance, security, migrations)
       - Remoção de duplicados e obsoletos
       - Documentação mantida atualizada

    Princípios Gerais:
    - Separação clara de responsabilidades
    - Limpeza contínua de recursos
    - Documentação organizada
    - Otimização para produção

    Esta organização visa:
    - Facilitar manutenção
    - Melhorar segurança
    - Otimizar recursos
    - Manter código limpo'
); 