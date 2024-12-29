from flask import Blueprint, jsonify

# Cria o Blueprint principal
main = Blueprint('main', __name__)

@main.route('/health')
def health():
    """Endpoint de saúde da API."""
    return jsonify({
        "status": "healthy",
        "service": "backend_api",
        "version": "1.0.0"
    }) 