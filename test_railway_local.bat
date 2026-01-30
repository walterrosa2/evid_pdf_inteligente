@echo off
REM Script para testar o start_services.py localmente antes do deploy

echo ========================================
echo  Teste Local - Leitor Inteligente
echo ========================================
echo.

REM Verificar se o ambiente virtual está ativo
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERRO] Python nao encontrado!
    echo Por favor, ative o ambiente virtual primeiro.
    pause
    exit /b 1
)

echo [OK] Python encontrado
echo.

REM Definir porta local para teste (simula Railway)
set PORT=8000

echo Configuracao de teste:
echo - Backend: http://localhost:%PORT%
echo - Frontend: http://localhost:8001
echo - Docs API: http://localhost:%PORT%/docs
echo.

echo Iniciando servicos...
echo.

REM Executar o script de inicialização
python start_services.py

pause
