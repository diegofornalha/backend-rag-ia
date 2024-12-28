from flask import Blueprint, render_template, jsonify
from API_frontend_flask.config.settings import settings

# Cria o Blueprint principal
main = Blueprint('main', __name__)

@main.route('/')
def home():
    """Página inicial do sistema RAG."""
    config = settings.get_config()
    return render_template('base/home.html',
                         title=config['TITLE'],
                         description=config['DESCRIPTION'])

@main.route('/health')
def health():
    """Endpoint de saúde da API Frontend."""
    config = settings.get_config()
    return jsonify({
        "status": "healthy",
        "service": "frontend_flask",
        "version": config['VERSION']
    })

@main.route('/instances')
def instances_page():
    """Página de gerenciamento de instâncias."""
    config = settings.get_config()
    return render_template('instances/index.html',
                         title="Gerenciamento de Instâncias",
                         description="Gerencie suas instâncias do WhatsApp")

@main.route('/messages')
def messages_page():
    """Página de gerenciamento de mensagens."""
    config = settings.get_config()
    return render_template('messages/index.html',
                         title="Gerenciamento de Mensagens",
                         description="Envie e gerencie suas mensagens") 