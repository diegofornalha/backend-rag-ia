from flask import Flask, redirect
from flask_cors import CORS
from flask_swagger_ui import get_swaggerui_blueprint
import logging
import os
from termcolor import colored

# Configuração de logging personalizada
class ColoredFormatter(logging.Formatter):
    def format(self, record):
        colors = {
            'INFO': 'green',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'DEBUG': 'blue'
        }
        
        icons = {
            'Iniciando': '🚀',
            'iniciada': '✅',
            'Documentação': '📚',
            'Debugger': '🔧',
            'Running': '⚡️',
            'WARNING': '⚠️ ',
            'ERROR': '❌'
        }
        
        for key, icon in icons.items():
            if key in record.msg:
                record.msg = f"{icon} {record.msg}"
        
        if record.levelname in colors:
            record.msg = colored(record.msg, colors[record.levelname])
            record.levelname = colored(record.levelname, colors[record.levelname])
        
        return super().format(record)

# Configuração do logger
logger = logging.getLogger('backend')
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.setFormatter(ColoredFormatter('%(message)s'))
logger.addHandler(handler)

def create_backend_app():
    """Cria e configura a aplicação Flask para o backend."""
    
    logger.info("Iniciando Backend API...")
    
    # Inicializa o Flask
    app = Flask(__name__)
    
    # Configuração do CORS
    CORS(app, resources={
        r"/*": {
            "origins": "*",
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"]
        }
    })
    
    # Configuração do Swagger UI
    SWAGGER_URL = '/docs'
    API_URL = '/static/swagger.json'
    swaggerui_blueprint = get_swaggerui_blueprint(
        SWAGGER_URL,
        API_URL,
        config={
            'app_name': "Backend API"
        }
    )
    app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)
    
    # Redireciona a rota raiz para a documentação
    @app.route('/')
    def index():
        return redirect('/docs')
    
    # Handler para erro 404 - Rota não encontrada
    @app.errorhandler(404)
    def not_found_error(error):
        logger.warning(f"Tentativa de acesso a rota inexistente. Redirecionando para documentação...")
        return redirect('/docs')
    
    # Rota de saúde
    @app.route('/health')
    def health():
        return {
            "status": "healthy",
            "service": "backend_api",
            "version": "1.0.0"
        }
    
    # Log de inicialização
    logger.info("Backend API iniciada - Versão 1.0.0")
    logger.info("\n📍 Backend Endpoints:")
    logger.info(f"🏠 Raiz (redireciona para docs): http://localhost:3000/")
    logger.info(f"📚 Documentação API: http://localhost:3000/docs")
    logger.info(f"🏥 Health Check: http://localhost:3000/health")
    logger.info("\n⚠️  Todas as rotas não encontradas serão redirecionadas para /docs")
    
    return app

# Cria a aplicação
app = create_backend_app()

if __name__ == '__main__':
    app.run(
        host="0.0.0.0",
        port=3000,
        debug=True
    ) 