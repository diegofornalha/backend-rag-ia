from flask import Flask
from app_gemini_back import app

if __name__ == "__main__":
    print("\n🚀 Iniciando servidor backend...\n")
    print("\033[34m🔗 Backend API disponível em: \033[4mhttp://localhost:8000\033[0m")
    print("\033[34m📚 Documentação disponível em: \033[4mhttp://localhost:8000/docs\033[0m")
    app.run(host='0.0.0.0', port=8000, debug=True) 