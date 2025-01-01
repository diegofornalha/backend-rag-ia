"""Constantes do projeto."""

# Configurações gerais
DEFAULT_SEARCH_LIMIT = 5
DEFAULT_MATCH_THRESHOLD = 0.5

# Códigos HTTP
HTTP_OK = 200
HTTP_BAD_REQUEST = 400
HTTP_UNAUTHORIZED = 401
HTTP_NOT_FOUND = 404
HTTP_SERVER_ERROR = 500

# Mensagens de erro
ERROR_SUPABASE_CONFIG = "SUPABASE_URL e SUPABASE_KEY devem ser configurados"
ERROR_GOOGLE_API_KEY = "GOOGLE_API_KEY deve ser configurada"
ERROR_EMBEDDING_GENERATION = "Erro ao gerar embedding"
ERROR_DATABASE_QUERY = "Erro na consulta ao banco de dados"
ERROR_SEARCH_FAILED = "Erro ao realizar busca: {error}" 