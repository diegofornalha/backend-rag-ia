"""Constantes utilizadas no projeto."""

# Mensagens de erro
ERROR_SUPABASE_CONFIG = "Configuração do Supabase incompleta"
ERROR_SUPABASE_CONNECT = "Erro ao conectar ao Supabase"
ERROR_INVALID_DATA = "Dados inválidos"
ERROR_FILE_NOT_FOUND = "Arquivo não encontrado"
ERROR_FILE_READ = "Erro ao ler arquivo"
ERROR_FILE_WRITE = "Erro ao escrever arquivo"

# Configurações
DEFAULT_EMBEDDING_MODEL = "text-embedding-ada-002"
DEFAULT_SIMILARITY_THRESHOLD = 0.5
DEFAULT_MATCH_COUNT = 4
DEFAULT_CHUNK_SIZE = 1000
DEFAULT_CHUNK_OVERLAP = 200
DEFAULT_CONTENT_PREVIEW_LENGTH = 200
DEFAULT_SEARCH_LIMIT = 10

# Tabelas
TABLE_DOCUMENTS = "documents"
TABLE_EMBEDDINGS = "embeddings"
TABLE_CHUNKS = "chunks"

# Campos
FIELD_ID = "id"
FIELD_CONTENT = "content"
FIELD_EMBEDDING = "embedding"
FIELD_METADATA = "metadata"
FIELD_CREATED_AT = "created_at"
FIELD_UPDATED_AT = "updated_at"

# Tipos de documento
DOC_TYPE_TEXT = "text"
DOC_TYPE_CODE = "code"
DOC_TYPE_MARKDOWN = "markdown"

# Status
STATUS_PENDING = "pending"
STATUS_PROCESSING = "processing"
STATUS_COMPLETED = "completed"
STATUS_ERROR = "error"

# Limites
MAX_TEXT_LENGTH = 100000
MAX_CHUNK_SIZE = 2000
MAX_RESULTS = 10
MAX_RETRIES = 3
TIMEOUT = 30  # segundos

# HTTP Status
HTTP_OK = 200
HTTP_CREATED = 201
HTTP_BAD_REQUEST = 400
HTTP_UNAUTHORIZED = 401
HTTP_NOT_FOUND = 404
HTTP_SERVER_ERROR = 500

# Tamanhos de preview
PREVIEW_LENGTH_SMALL = 57
PREVIEW_LENGTH_MEDIUM = 100
PREVIEW_LENGTH_LARGE = 200
