from flask import Flask, jsonify, request, redirect
from flask_swagger_ui import get_swaggerui_blueprint
from flask_cors import CORS
import os
from dotenv import load_dotenv
import json
from config.settings import settings
import google.generativeai as genai

# Carrega variáveis de ambiente
load_dotenv()

# Configuração do Gemini
genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))
model = genai.GenerativeModel('gemini-1.5-flash')

app = Flask(__name__)

# Configuração do CORS - Permite apenas frontend na porta 3000
CORS(app, resources={
    r"/gemini/*": {
        "origins": ["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:2000", "http://127.0.0.1:2000"],
        "methods": ["POST", "OPTIONS"],
        "allow_headers": ["Content-Type"]
    },
    r"/health": {
        "origins": "*",  # Health check pode ser acessado de qualquer lugar
        "methods": ["GET"]
    }
})

# Configurações do Gemini
MAX_MESSAGE_LENGTH = 300

# Configuração do Swagger
SWAGGER_URL = '/docs'
API_URL = '/swagger'

swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': "Gemini API"
    }
)
app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

@app.route('/swagger')
def swagger_json():
    with open('porta8000.json', 'r') as f:
        return jsonify(json.load(f))

@app.route('/')
def redirect_to_docs():
    return redirect('/docs')

@app.route('/health', methods=['GET'])
def health_check():
    """Endpoint para verificar se a API está funcionando."""
    return jsonify({
        "status": "healthy",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "message": "Server is running"
    })

@app.route('/gemini/chat', methods=['POST'])
def chat():
    """Endpoint para chat com o Gemini."""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "Dados inválidos"}), 400
        
        message = data.get('message', '')
        
        # Valida apenas o tamanho da mensagem
        if len(message) > MAX_MESSAGE_LENGTH:
            return jsonify({"error": f"Mensagem muito longa. Máximo: {MAX_MESSAGE_LENGTH} caracteres"}), 400
        
        # Adiciona instrução para responder em português
        prompt = f"Responda em português do Brasil. {message}"
        
        # Chamada real ao Gemini
        response = model.generate_content(prompt)
        
        return jsonify({
            "response": response.text
        })
    except Exception as e:
        return jsonify({
            "error": f"Erro ao processar mensagem: {str(e)}"
        }), 500

if __name__ == '__main__':
    app.run(host=settings.HOST, port=settings.PORT, debug=settings.DEBUG) 