#!/bin/bash

# Porta onde o FastAPI está rodando
PORT=10000

# Inicia o backend com Docker Compose
echo "🔧 Iniciando backend com Docker Compose..."
docker compose up --build -d

# Aguarda alguns segundos para garantir que o serviço subiu
sleep 5

# Inicia o túnel Ngrok
echo "🌐 Criando túnel com Ngrok na porta $PORT..."
ngrok http $PORT
