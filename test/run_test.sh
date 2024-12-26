#!/bin/bash

echo "🔨 Construindo a imagem de teste..."
docker build -t render-api-test .

echo "\n🚀 Executando o teste..."
docker run --rm render-api-test 