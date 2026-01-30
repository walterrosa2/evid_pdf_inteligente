#!/bin/bash

# Script de inicialização para Railway
# Roda o backend (FastAPI) e frontend (Streamlit) simultaneamente

echo "🚀 Iniciando Leitor Inteligente..."

# Inicia o backend FastAPI em background
echo "📡 Iniciando Backend (FastAPI) na porta $PORT..."
python -m uvicorn backend.main:app --host 0.0.0.0 --port $PORT &
BACKEND_PID=$!

# Aguarda 3 segundos para o backend iniciar
sleep 3

# Calcula porta para o frontend (PORT + 1)
FRONTEND_PORT=$((PORT + 1))

# Inicia o frontend Streamlit
echo "🎨 Iniciando Frontend (Streamlit) na porta $FRONTEND_PORT..."
streamlit run frontend/app.py --server.port $FRONTEND_PORT --server.address 0.0.0.0 &
FRONTEND_PID=$!

echo "✅ Backend rodando no PID: $BACKEND_PID (porta $PORT)"
echo "✅ Frontend rodando no PID: $FRONTEND_PID (porta $FRONTEND_PORT)"
echo "📚 Documentação da API: http://0.0.0.0:$PORT/docs"
echo "🌐 Interface Streamlit: http://0.0.0.0:$FRONTEND_PORT"

# Função para encerrar processos ao receber sinal de término
cleanup() {
    echo "🛑 Encerrando serviços..."
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
    exit 0
}

trap cleanup SIGTERM SIGINT

# Mantém o script rodando e monitora os processos
wait
