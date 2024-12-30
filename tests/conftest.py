import os
import pytest
from dotenv import load_dotenv

# Carrega variáveis de ambiente antes dos testes
@pytest.fixture(scope="session", autouse=True)
def load_env():
    load_dotenv()
    
# Fixture para verificar se as variáveis de ambiente necessárias estão definidas
@pytest.fixture(scope="session")
def check_env_vars():
    required_vars = ["SUPABASE_URL", "SUPABASE_KEY"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        pytest.skip(f"Variáveis de ambiente necessárias não definidas: {', '.join(missing_vars)}") 