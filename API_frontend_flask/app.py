from flask import Flask, redirect, url_for
from flask_cors import CORS
import logging
import os
from termcolor import colored

from API_frontend_flask.config.settings import settings
from API_frontend_flask.config.jinja import setup_jinja
from API_frontend_flask.api.routes import main as main_blueprint

# Configuração de logging personalizada
class ColoredFormatter(logging.Formatter):
    """Formatador personalizado para logs coloridos."""
    
    def format(self, record):
        # Cores para diferentes níveis de log
        colors = {
            'INFO': 'green',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'DEBUG': 'blue'
        }
        
        # Ícones para diferentes tipos de mensagem
        icons = {
            'Iniciando': '🚀',
            'iniciada': '✅',
            'Documentação': '📚',
            'Debugger': '🔧',
            'Running': '⚡️',
            'WARNING': '⚠️ ',
            'ERROR': '❌'
        }
        
        # Adiciona cor e ícone à mensagem
        for key, icon in icons.items():
            if key in record.msg:
                record.msg = f"{icon} {record.msg}"
        
        # Formata a mensagem
        if record.levelname in colors:
            record.msg = colored(record.msg, colors[record.levelname])
            record.levelname = colored(record.levelname, colors[record.levelname])
        
        return super().format(record)

# Configuração do logger
logger = logging.getLogger('frontend')
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.setFormatter(ColoredFormatter('%(message)s'))
logger.addHandler(handler)

def create_app():
    """Cria e configura a aplicação Flask."""
    
    logger.info("Iniciando Frontend Flask...")
    
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
    
    # Registra os blueprints
    app.register_blueprint(main_blueprint)
    
    # Handler para erro 404 - Página não encontrada
    @app.errorhandler(404)
    def page_not_found(error):
        logger.warning(f"Tentativa de acesso a rota inexistente. Redirecionando para home...")
        return redirect(url_for('main.home'))
    
    # Log de inicialização
    logger.info(f"Frontend Flask iniciado - Versão {settings.VERSION}")
    
    # Log dos endpoints do Frontend
    logger.info("\n📍 Frontend Endpoints (Interface):")
    logger.info(f"🏠 Home: http://{settings.HOST}:{settings.PORT}/")
    logger.info(f"📱 Instâncias: http://{settings.HOST}:{settings.PORT}/instances")
    logger.info(f"💬 Mensagens: http://{settings.HOST}:{settings.PORT}/messages")
    logger.info(f"🏥 Health Check: http://{settings.HOST}:{settings.PORT}/health")
    
    # Aviso sobre o backend
    logger.warning("\n⚠️  Backend (API Principal):")
    logger.warning(f"🔌 API URL: {settings.RAG_API_URL}")
    logger.warning(f"📚 Documentação API: {settings.RAG_API_URL}/docs")
    logger.warning("📌 Certifique-se que o backend está rodando antes de usar a interface")
    
    return app

# Cria a aplicação
app = create_app()

if __name__ == '__main__':
    app.run(
        host=settings.HOST,
        port=settings.PORT,
        debug=settings.DEBUG
    ) 