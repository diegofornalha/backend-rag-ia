from jinja2 import Environment
from datetime import datetime

def format_datetime(value):
    """Formata datetime para exibição."""
    if isinstance(value, str):
        value = datetime.fromisoformat(value)
    return value.strftime("%d/%m/%Y %H:%M:%S")

def setup_jinja(app):
    """Configura o ambiente Jinja2."""
    
    # Adiciona filtros customizados
    app.jinja_env.filters['datetime'] = format_datetime
    
    # Configurações do Jinja2
    app.jinja_env.trim_blocks = True
    app.jinja_env.lstrip_blocks = True
    
    # Variáveis globais
    app.jinja_env.globals.update(
        APP_NAME=app.config['TITLE'],
        CURRENT_YEAR=datetime.now().year
    ) 