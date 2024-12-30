#!/bin/bash

# Configurações
RENDER_SSH_HOST="ssh.oregon.render.com"
RENDER_SSH_USER="srv-ctmtqra3esus739sknb0"
RENDER_SSH_KEY="$HOME/.ssh/id_ed25519"

# Função para executar comandos SSH
ssh_execute() {
    ssh -i "$RENDER_SSH_KEY" -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null "$RENDER_SSH_USER@$RENDER_SSH_HOST" "$1"
}

# Menu de opções
echo "🚀 Gerenciamento SSH do Render"
echo "1. Explorar diretórios"
echo "2. Verificar ambiente Docker"
echo "3. Reiniciar aplicação"
echo "4. Ver logs"
echo "5. Verificar processos"
echo "6. Limpar cache"
echo "7. Sair"

read -p "Escolha uma opção (1-7): " opcao

case $opcao in
    1)
        echo "📂 Menu de Exploração"
        echo "a) Listar diretório atual"
        echo "b) Listar /opt"
        echo "c) Listar /opt/render"
        echo "d) Verificar espaço em disco"
        read -p "Escolha uma opção (a-d): " subopcao
        case $subopcao in
            a) ssh_execute "ls -la" ;;
            b) ssh_execute "ls -la /opt" ;;
            c) ssh_execute "ls -la /opt/render" ;;
            d) ssh_execute "df -h" ;;
            *) echo "❌ Opção inválida" ;;
        esac
        ;;
    2)
        echo "🐳 Menu Docker"
        echo "a) Listar containers"
        echo "b) Verificar imagens"
        echo "c) Verificar redes"
        echo "d) Status do sistema"
        read -p "Escolha uma opção (a-d): " subopcao
        case $subopcao in
            a) ssh_execute "docker ps -a" ;;
            b) ssh_execute "docker images" ;;
            c) ssh_execute "docker network ls" ;;
            d) ssh_execute "docker system df" ;;
            *) echo "❌ Opção inválida" ;;
        esac
        ;;
    3)
        echo "🔄 Reiniciando aplicação..."
        ssh_execute "cd /opt/render/project/src && \
                    docker pull fornalha/backend:latest && \
                    docker stop \$(docker ps -q) 2>/dev/null || true && \
                    docker run -d -p 10000:10000 \
                    -e PYTHONPATH=/app/backend-rag-ia \
                    fornalha/backend:latest"
        ;;
    4)
        echo "📝 Menu de Logs"
        echo "a) Logs do container atual"
        echo "b) Últimas 100 linhas"
        echo "c) Seguir logs em tempo real"
        read -p "Escolha uma opção (a-c): " subopcao
        case $subopcao in
            a) ssh_execute "docker logs \$(docker ps -q)" ;;
            b) ssh_execute "docker logs --tail 100 \$(docker ps -q)" ;;
            c) ssh_execute "docker logs -f \$(docker ps -q)" ;;
            *) echo "❌ Opção inválida" ;;
        esac
        ;;
    5)
        echo "👀 Verificando processos..."
        ssh_execute "ps aux | grep python || true"
        ;;
    6)
        echo "🧹 Limpando cache..."
        ssh_execute "docker system prune -f"
        ;;
    7)
        echo "👋 Saindo..."
        exit 0
        ;;
    *)
        echo "❌ Opção inválida"
        exit 1
        ;;
esac 