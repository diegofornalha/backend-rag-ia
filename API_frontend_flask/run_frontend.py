import subprocess
import sys
import os
from time import sleep

def run_frontend():
    # Ativa o ambiente virtual e carrega as variáveis de ambiente
    activate_cmd = "source .venv/bin/activate && source .env"
    
    # Comando para iniciar apenas o frontend
    frontend_cmd = f"{activate_cmd} && python3 -m flask run --debug --port 2000"
    
    try:
        # Inicia o processo
        print("\n🚀 Iniciando servidor frontend...\n")
        
        frontend = subprocess.Popen(frontend_cmd, shell=True, stdout=subprocess.PIPE, 
                                 stderr=subprocess.PIPE, text=True)
        print("📱 Frontend iniciado na porta 2000")
        
        print("\n✨ Servidor rodando! Pressione Ctrl+C para parar.\n")
        
        # Mantém o script rodando
        while True:
            sleep(1)
            
    except KeyboardInterrupt:
        print("\n\n🛑 Encerrando servidor...")
        # Encerra o processo
        frontend.terminate()
        print("✅ Servidor encerrado com sucesso!")
        sys.exit(0)

if __name__ == "__main__":
    run_frontend() 