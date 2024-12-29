#!/bin/bash

# Cores para output
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

# Verificar se um comando foi fornecido
JOB_COMMAND="$1"
if [ -z "$JOB_COMMAND" ]; then
    echo -e "${RED}Erro: Comando não especificado${NC}"
    echo "Uso: ./job_runner.sh 'seu comando aqui'"
    exit 1
fi

# Verificar variáveis de ambiente
if [ -z "$RENDER_API_KEY" ] || [ -z "$RENDER_SERVICE_ID" ]; then
    echo -e "${RED}Erro: RENDER_API_KEY e RENDER_SERVICE_ID devem estar configurados${NC}"
    exit 1
fi

echo -e "${GREEN}🚀 Criando job para executar: $JOB_COMMAND${NC}"

# Criar job
RESPONSE=$(curl --silent --request POST \
     --url "https://api.render.com/v1/services/$RENDER_SERVICE_ID/jobs" \
     --header "Authorization: Bearer $RENDER_API_KEY" \
     --header 'Content-Type: application/json' \
     --data-raw "{
         \"startCommand\": \"$JOB_COMMAND\"
     }")

JOB_ID=$(echo $RESPONSE | jq -r '.id')

if [ -z "$JOB_ID" ] || [ "$JOB_ID" = "null" ]; then
    echo -e "${RED}Erro ao criar job: $RESPONSE${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Job criado com ID: $JOB_ID${NC}"

# Monitorar status
echo "Monitorando status do job..."
while true; do
    STATUS=$(curl --silent \
         --url "https://api.render.com/v1/services/$RENDER_SERVICE_ID/jobs/$JOB_ID" \
         --header "Authorization: Bearer $RENDER_API_KEY" \
         | jq -r '.status')
    
    if [ "$STATUS" = "succeeded" ]; then
        echo -e "${GREEN}✅ Job completado com sucesso!${NC}"
        break
    elif [ "$STATUS" = "failed" ]; then
        echo -e "${RED}❌ Job falhou!${NC}"
        exit 1
    elif [ "$STATUS" = "null" ]; then
        echo "⏳ Job pendente..."
    else
        echo "⚡ Job em execução... (status: $STATUS)"
    fi
    
    sleep 10
done 