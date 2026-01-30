# Script de Inicializacao da Aplicacao - Leitor Inteligente (Backend + Frontend)
# Este script automatiza:
# 1. Verificação do Python
# 2. Criação/Ativação do venv
# 3. Instalação de dependências
# 4. Inicialização do Backend (FastAPI/Uvicorn) em nova janela
# 5. Inicialização do Frontend (Streamlit) na janela atual

$ErrorActionPreference = "Stop"

# Garante que o script rode no diretorio onde ele esta localizado
Set-Location $PSScriptRoot

Write-Host "------------------------------------------" -ForegroundColor Cyan
Write-Host "   Iniciando Leitor Inteligente           " -ForegroundColor Cyan
Write-Host "------------------------------------------" -ForegroundColor Cyan

# 1. Verifica se o Python esta instalado
try {
    python --version | Out-Null
}
catch {
    Write-Error "Python nao encontrado! Instale o Python para continuar."
    exit
}

# 2. Gerencia o Ambiente Virtual (.venv)
if (Test-Path ".venv") {
    Write-Host "==> [.venv] detectado." -ForegroundColor Green
}
else {
    Write-Host "==> [.venv] nao encontrado. Criando ambiente virtual..." -ForegroundColor Yellow
    python -m venv .venv
    Write-Host "==> Ambiente virtual criado com sucesso." -ForegroundColor Green
}

# 3. Define variaveis de caminho e PYTHONPATH
$venvScript = Join-Path $PSScriptRoot ".venv\Scripts\Activate.ps1"
$pythonExe = Join-Path $PSScriptRoot ".venv\Scripts\python.exe"

# Adiciona o diretorio atual ao PYTHONPATH para que o modulo 'backend' seja encontrado
$env:PYTHONPATH = $PSScriptRoot
Write-Host "==> PYTHONPATH configurado para: $PSScriptRoot" -ForegroundColor Gray

# 4. Ativa o Ambiente Virtual (na sessao atual)
if (Test-Path $venvScript) {
    Write-Host "==> Ativando ambiente virtual..." -ForegroundColor Blue
    & $venvScript
}
else {
    Write-Error "ERRO: Script de ativacao nao encontrado em $venvScript"
    exit
}

# 5. Verifica e instala dependencias
if (Test-Path "requirements.txt") {
    Write-Host "==> Verificando dependencias..." -ForegroundColor Blue
    python -m pip install -r requirements.txt --quiet
    Write-Host "==> Dependencias verificadas." -ForegroundColor Green
}

# 6. Inicializa o Backend (FastAPI) em uma NOVA JANELA
Write-Host ""
Write-Host "------------------------------------------" -ForegroundColor Magenta
Write-Host "   Iniciando Backend (Uvicorn)...         " -ForegroundColor Magenta
Write-Host "------------------------------------------" -ForegroundColor Magenta

# Monta o comando para abrir o uvicorn em outra janela, garantindo que use o venv e o pythonpath
$backendCmd = "-NoExit -Command & '$venvScript'; $env:PYTHONPATH='$PSScriptRoot'; python -m uvicorn backend.main:app --reload --port 8000"
Start-Process powershell -ArgumentList $backendCmd

Write-Host "==> Backend iniciado (janela separada)." -ForegroundColor Green

Write-Host "==> Aguardando Backend iniciar na porta 8000..." -ForegroundColor Cyan

$maxRetries = 30
$retryCount = 0
$backendReady = $false

while ($retryCount -lt $maxRetries) {
    $conn = Test-NetConnection -ComputerName localhost -Port 8000 -InformationLevel Quiet
    if ($conn) {
        $backendReady = $true
        break
    }
    Write-Host "   ... aguardando backend ($retryCount/$maxRetries)" -ForegroundColor Gray
    Start-Sleep -Seconds 2
    $retryCount++
}

if (-not $backendReady) {
    Write-Warning "AVISO: O Backend nao respondeu na porta 8000 apos 60 segundos."
    Write-Warning "O Frontend pode falhar ao conectar."
    # Nao aborta, tenta abrir o frontend mesmo assim, mas avisa o usuario
}
else {
    Write-Host "==> Backend detectado e pronto!" -ForegroundColor Green
}


# 7. Inicializa o Frontend (Streamlit) na janela ATUAL
Write-Host ""
Write-Host "------------------------------------------" -ForegroundColor Cyan
Write-Host "   Iniciando Frontend (Streamlit)...      " -ForegroundColor Cyan
Write-Host "------------------------------------------" -ForegroundColor Cyan
Write-Host "A aplicacao abrira no seu navegador em instantes." -ForegroundColor White

streamlit run frontend/app.py --server.port 8501 --server.address localhost
