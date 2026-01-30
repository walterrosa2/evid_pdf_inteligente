@echo off
TITLE Inicializador Leitor Inteligente
REM Atalho para rodar o script PowerShell sem restrições de política
echo Iniciando aplicacao...
powershell -ExecutionPolicy Bypass -File "%~dp0start.ps1"
pause
