@echo off
TITLE Debug Backend Leitor Inteligente
echo ---------------------------------------------------
echo INICIANDO BACKEND EM MODO DEBUG MANUAL
echo ---------------------------------------------------

REM 1. Configurar PYTHONPATH para a raiz do projeto
set "PYTHONPATH=%~dp0"
echo ==> PYTHONPATH definido para: %PYTHONPATH%

REM 2. Ativar Ambiente Virtual
if exist "%~dp0.venv\Scripts\activate.bat" (
    echo ==> Ativando ambiente virtual...
    call "%~dp0.venv\Scripts\activate.bat"
) else (
    echo ERRO: .venv nao encontrado! Execute o start.ps1 primeiro para criar.
    pause
    exit /b
)

REM 3. Iniciar Uvicorn (Backend)
echo.
echo ==> Iniciando Uvicorn na porta 8000...
echo     (Pressione Ctrl+C para parar)
echo.

python -m uvicorn backend.main:app --host localhost --port 8000 --reload

echo.
echo O Backend parou de rodar.
pause
