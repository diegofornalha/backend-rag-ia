#!/bin/bash

# Configurações
APP_NAME="backend-rag"
DOCKER_REGISTRY="registry.example.com"
DEPLOY_ENV=${1:-production}
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
IMAGE_TAG="${DEPLOY_ENV}_${TIMESTAMP}"
HEALTH_CHECK_RETRIES=30
HEALTH_CHECK_INTERVAL=10

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Função de log
log() {
    echo -e "${2:-$NC}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

# Função de erro
error() {
    log "$1" $RED
    exit 1
}

# Função de verificação de saúde
check_health() {
    local url=$1
    local retries=$2
    local interval=$3
    local count=0

    log "Verificando saúde do serviço em $url" $YELLOW

    while [ $count -lt $retries ]; do
        if curl -s -f "$url/api/v1/health" > /dev/null; then
            log "Serviço está saudável!" $GREEN
            return 0
        fi

        count=$((count + 1))
        log "Tentativa $count de $retries..." $YELLOW
        sleep $interval
    done

    return 1
}

# Verifica ambiente
if [ -z "$DEPLOY_ENV" ]; then
    error "Ambiente não especificado"
fi

# Verifica variáveis necessárias
if [ -z "$DOCKER_REGISTRY" ]; then
    error "DOCKER_REGISTRY não definido"
fi

# Build da imagem
log "Iniciando build da imagem..." $YELLOW
docker build -t "${DOCKER_REGISTRY}/${APP_NAME}:${IMAGE_TAG}" \
    -f backend_rag_ia/3_deployment/docker/Dockerfile . || \
    error "Falha no build da imagem"

# Push da imagem
log "Push da imagem para registry..." $YELLOW
docker push "${DOCKER_REGISTRY}/${APP_NAME}:${IMAGE_TAG}" || \
    error "Falha no push da imagem"

# Backup da versão atual
log "Criando backup da versão atual..." $YELLOW
CURRENT_VERSION=$(docker inspect "${APP_NAME}" --format '{{.Config.Image}}' 2>/dev/null || echo "")
if [ ! -z "$CURRENT_VERSION" ]; then
    docker tag "$CURRENT_VERSION" "${DOCKER_REGISTRY}/${APP_NAME}:backup_${TIMESTAMP}"
fi

# Deploy
log "Iniciando deploy..." $YELLOW

# Parar container atual
docker stop "${APP_NAME}" 2>/dev/null || true
docker rm "${APP_NAME}" 2>/dev/null || true

# Iniciar novo container
docker run -d \
    --name "${APP_NAME}" \
    --restart unless-stopped \
    -p 8000:8000 \
    -e "ENVIRONMENT=${DEPLOY_ENV}" \
    "${DOCKER_REGISTRY}/${APP_NAME}:${IMAGE_TAG}" || \
    error "Falha ao iniciar container"

# Verificar saúde
if ! check_health "http://localhost:8000" $HEALTH_CHECK_RETRIES $HEALTH_CHECK_INTERVAL; then
    log "Serviço não está saudável. Iniciando rollback..." $RED
    
    # Rollback
    docker stop "${APP_NAME}"
    docker rm "${APP_NAME}"
    
    if [ ! -z "$CURRENT_VERSION" ]; then
        log "Restaurando versão anterior..." $YELLOW
        docker run -d \
            --name "${APP_NAME}" \
            --restart unless-stopped \
            -p 8000:8000 \
            -e "ENVIRONMENT=${DEPLOY_ENV}" \
            "$CURRENT_VERSION"
            
        if check_health "http://localhost:8000" $HEALTH_CHECK_RETRIES $HEALTH_CHECK_INTERVAL; then
            log "Rollback concluído com sucesso" $GREEN
        else
            error "Falha no rollback"
        fi
    else
        error "Sem versão anterior para rollback"
    fi
    
    exit 1
fi

# Limpeza
log "Removendo imagens antigas..." $YELLOW
docker images "${DOCKER_REGISTRY}/${APP_NAME}" --format "{{.ID}}" | \
    grep -v "$(docker inspect --format='{{.Id}}' "${DOCKER_REGISTRY}/${APP_NAME}:${IMAGE_TAG}")" | \
    xargs -r docker rmi

log "Deploy concluído com sucesso!" $GREEN

# Métricas do deploy
DEPLOY_DURATION=$SECONDS
log "Métricas do Deploy:" $GREEN
log "- Duração: ${DEPLOY_DURATION}s" $GREEN
log "- Ambiente: ${DEPLOY_ENV}" $GREEN
log "- Tag: ${IMAGE_TAG}" $GREEN
log "- Health check: OK" $GREEN 