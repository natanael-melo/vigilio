#!/bin/bash

# ============================================
# Script de Publicação do Vigilo no Docker Hub
# ============================================

# Configurações
DOCKER_USER="seu_usuario"  # ← ALTERE AQUI para seu username do Docker Hub
IMAGE_NAME="vigilo"
VERSION="1.1.0"

echo "🐳 Publicando Vigilo no Docker Hub"
echo "=========================================="
echo ""

# Verifica se está logado
echo "🔐 Verificando login no Docker Hub..."
if ! docker info | grep -q "Username"; then
    echo "⚠️  Você não está logado. Fazendo login..."
    docker login
    if [ $? -ne 0 ]; then
        echo "❌ Falha no login. Abortando."
        exit 1
    fi
fi

echo "✅ Login OK"
echo ""

# Build da imagem
echo "🔨 Fazendo build da imagem..."
docker build -t ${DOCKER_USER}/${IMAGE_NAME}:${VERSION} .
docker build -t ${DOCKER_USER}/${IMAGE_NAME}:latest .

if [ $? -ne 0 ]; then
    echo "❌ Falha no build. Abortando."
    exit 1
fi

echo "✅ Build concluído"
echo ""

# Push para Docker Hub
echo "📤 Enviando para Docker Hub..."
echo "   - ${DOCKER_USER}/${IMAGE_NAME}:${VERSION}"
docker push ${DOCKER_USER}/${IMAGE_NAME}:${VERSION}

echo "   - ${DOCKER_USER}/${IMAGE_NAME}:latest"
docker push ${DOCKER_USER}/${IMAGE_NAME}:latest

if [ $? -ne 0 ]; then
    echo "❌ Falha no push. Verifique sua conexão."
    exit 1
fi

echo ""
echo "=========================================="
echo "✅ Publicação concluída com sucesso!"
echo ""
echo "📦 Imagem disponível em:"
echo "   https://hub.docker.com/r/${DOCKER_USER}/${IMAGE_NAME}"
echo ""
echo "🚀 Para usar em outras VPS:"
echo "   docker pull ${DOCKER_USER}/${IMAGE_NAME}:latest"
echo "=========================================="

