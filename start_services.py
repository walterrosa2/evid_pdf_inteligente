#!/usr/bin/env python3
"""
Script de inicialização para Railway
Roda o backend (FastAPI) e frontend (Streamlit) simultaneamente
"""

import os
import sys
import subprocess
import signal
import time
from loguru import logger

# Configurar loguru
logger.remove()
logger.add(sys.stdout, format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>")

# Processos globais
backend_process = None
frontend_process = None

def cleanup(signum=None, frame=None):
    """Encerra os processos ao receber sinal de término"""
    logger.warning("🛑 Encerrando serviços...")
    
    if backend_process:
        backend_process.terminate()
        logger.info("Backend encerrado")
    
    if frontend_process:
        frontend_process.terminate()
        logger.info("Frontend encerrado")
    
    sys.exit(0)

# Registrar handlers de sinal
signal.signal(signal.SIGTERM, cleanup)
signal.signal(signal.SIGINT, cleanup)

def main():
    global backend_process, frontend_process
    
    # Obter porta do ambiente (Railway define $PORT)
    port = int(os.getenv("PORT", 8000))
    frontend_port = port + 1
    
    logger.info("🚀 Iniciando Leitor Inteligente...")
    logger.info(f"📡 Backend será executado na porta: {port}")
    logger.info(f"🎨 Frontend será executado na porta: {frontend_port}")
    
    try:
        # Iniciar backend FastAPI
        logger.info("📡 Iniciando Backend (FastAPI)...")
        backend_process = subprocess.Popen([
            sys.executable, "-m", "uvicorn",
            "backend.main:app",
            "--host", "0.0.0.0",
            "--port", str(port)
        ])
        
        # Aguardar backend inicializar
        time.sleep(3)
        logger.success(f"✅ Backend rodando no PID: {backend_process.pid}")
        
        # Iniciar frontend Streamlit
        logger.info("🎨 Iniciando Frontend (Streamlit)...")
        frontend_process = subprocess.Popen([
            sys.executable, "-m", "streamlit", "run",
            "frontend/app.py",
            "--server.port", str(frontend_port),
            "--server.address", "0.0.0.0",
            "--server.headless", "true"
        ])
        
        logger.success(f"✅ Frontend rodando no PID: {frontend_process.pid}")
        logger.info(f"📚 Documentação da API: http://0.0.0.0:{port}/docs")
        logger.info(f"🌐 Interface Streamlit: http://0.0.0.0:{frontend_port}")
        logger.success("🎉 Todos os serviços iniciados com sucesso!")
        
        # Monitorar processos
        while True:
            # Verificar se algum processo morreu
            backend_status = backend_process.poll()
            frontend_status = frontend_process.poll()
            
            if backend_status is not None:
                logger.error(f"❌ Backend encerrou com código: {backend_status}")
                cleanup()
            
            if frontend_status is not None:
                logger.error(f"❌ Frontend encerrou com código: {frontend_status}")
                cleanup()
            
            time.sleep(1)
            
    except Exception as e:
        logger.error(f"❌ Erro ao iniciar serviços: {e}")
        cleanup()
        sys.exit(1)

if __name__ == "__main__":
    main()
