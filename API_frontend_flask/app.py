from flask import Flask
from flask_cors import CORS
from flask_swagger_ui import get_swaggerui_blueprint
import logging
import os

from API_frontend_flask.config.settings import settings
from API_frontend_flask.config.jinja import setup_jinja
from API_frontend_flask.api.routes import main as main_blueprint

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_app():
    """Cria e configura a aplicação Flask."""
    
    logger.info("🚀 Iniciando API Frontend Flask...")
    
    # Inicializa o Flask com as configurações
    app = Flask(__name__,
        template_folder=settings.TEMPLATE_FOLDER,
        static_folder=settings.STATIC_FOLDER,
        static_url_path=settings.STATIC_URL_PATH
    )
    
    # Configuração do CORS
    CORS(app, resources={
        r"/*": {
            "origins": "*",
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"]
        }
    })
    
    # Carrega configurações
    app.config.update(settings.get_config())
    
    # Configura Jinja2
    setup_jinja(app)
    
    # Configuração do Swagger UI
    SWAGGER_URL = '/docs'
    API_URL = '/static/swagger.json'
    swaggerui_blueprint = get_swaggerui_blueprint(
        SWAGGER_URL,
        API_URL,
        config={
            'app_name': "Frontend Flask API"
        }
    )
    app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)
    
    # Registra os blueprints
    app.register_blueprint(main_blueprint)
    
    # Log de inicialização
    logger.info(f"✅ API Frontend Flask iniciada - Versão {settings.VERSION}")
    logger.info(f"📝 Documentação: http://{settings.HOST}:{settings.PORT}/docs")
    
    return app

# Cria a aplicação
app = create_app()

if __name__ == '__main__':
    app.run(
        host=settings.HOST,
        port=settings.PORT,
        debug=settings.DEBUG
    ) 