-- Criar schema auth se não existir
CREATE SCHEMA IF NOT EXISTS auth;

-- Função para obter o ID do usuário atual
CREATE OR REPLACE FUNCTION auth.uid() 
RETURNS uuid 
LANGUAGE sql 
STABLE
SECURITY DEFINER
SET search_path = auth, rag, rules, public
AS $$
  SELECT 
    COALESCE(
      current_setting('request.jwt.claims', true)::json->>'sub',
      current_setting('request.jwt.claims', true)::json->>'user_id'
    )::uuid
$$;

-- Função para verificar se o usuário é autenticado
CREATE OR REPLACE FUNCTION auth.is_authenticated() 
RETURNS boolean 
LANGUAGE sql 
STABLE
SECURITY DEFINER
SET search_path = auth, rag, rules, public
AS $$
  SELECT auth.uid() IS NOT NULL
$$;

-- Função para verificar se o usuário tem role específica
CREATE OR REPLACE FUNCTION auth.has_role(role text) 
RETURNS boolean 
LANGUAGE sql 
STABLE
SECURITY DEFINER
SET search_path = auth, rag, rules, public
AS $$
  SELECT 
    COALESCE(
      current_setting('request.jwt.claims', true)::json->>'role' = role,
      false
    )
$$;

-- Função para verificar se o usuário é dono do registro
CREATE OR REPLACE FUNCTION auth.is_owner(record_owner_id uuid) 
RETURNS boolean 
LANGUAGE sql 
STABLE
SECURITY DEFINER
SET search_path = auth, rag, rules, public
AS $$
  SELECT auth.uid() = record_owner_id
$$;
