# ✅ Configuração Concluída - Deploy Railway (Opção 2)

## 📦 Arquivos Criados/Modificados

### ✨ Novos Arquivos

1. **`start_services.py`** 🚀
   - Script Python que inicia backend e frontend simultaneamente
   - Monitora processos e gerencia encerramento
   - Usa `loguru` para logs detalhados
   - Backend: porta `$PORT`
   - Frontend: porta `$PORT + 1`

2. **`start.sh`** 🐚
   - Versão bash do script de inicialização (alternativa)

3. **`RAILWAY_DEPLOY.md`** 📖
   - Documentação completa sobre deploy no Railway
   - Troubleshooting e dicas
   - Passo a passo detalhado

4. **`test_railway_local.bat`** 🧪
   - Script para testar localmente antes do deploy
   - Simula ambiente do Railway

### 🔄 Arquivos Modificados

1. **`Procfile`**
   - **Antes**: 
     ```
     web: python -m uvicorn backend.main:app --host 0.0.0.0 --port $PORT
     frontend: streamlit run frontend/app.py --server.port $PORT --server.address 0.0.0.0
     ```
   - **Depois**:
     ```
     web: python start_services.py
     ```

2. **`COMO_RODAR.md`**
   - Atualizada seção de deploy do Railway
   - Adicionadas informações sobre o script unificado
   - Instruções de verificação pós-deploy

## 🎯 Como Funciona

```
Railway Deploy
     ↓
Procfile detectado
     ↓
Executa: python start_services.py
     ↓
┌─────────────────────────────────┐
│   start_services.py             │
│                                 │
│  1. Lê variável $PORT           │
│  2. Inicia Backend (FastAPI)    │
│     → Porta: $PORT              │
│  3. Aguarda 3 segundos          │
│  4. Inicia Frontend (Streamlit) │
│     → Porta: $PORT + 1          │
│  5. Monitora ambos processos    │
└─────────────────────────────────┘
```

## 🧪 Testar Localmente

Antes de fazer o deploy, teste localmente:

```powershell
# Execute o script de teste
.\test_railway_local.bat
```

Ou manualmente:

```powershell
# Definir porta
$env:PORT = "8000"

# Executar
python start_services.py
```

Você verá logs como:

```
16:00:00 | INFO     | 🚀 Iniciando Leitor Inteligente...
16:00:00 | INFO     | 📡 Backend será executado na porta: 8000
16:00:00 | INFO     | 🎨 Frontend será executado na porta: 8001
16:00:03 | SUCCESS  | ✅ Backend rodando no PID: 12345
16:00:05 | SUCCESS  | ✅ Frontend rodando no PID: 67890
16:00:05 | SUCCESS  | 🎉 Todos os serviços iniciados com sucesso!
```

## 🚀 Próximos Passos para Deploy

### 1. Commit e Push
```bash
git add .
git commit -m "feat: configurar deploy unificado no Railway"
git push origin main
```

### 2. No Railway
1. Acesse seu projeto no Railway
2. Vá em "Variables" e configure:
   - `GOOGLE_API_KEY`: sua chave do Gemini
3. O Railway detectará as mudanças e fará redeploy automaticamente

### 3. Verificar Deploy
Após o deploy, acesse:
- **API**: `https://[seu-app].up.railway.app/`
  - Deve retornar: `{"message":"Leitor Inteligente API está online!","docs":"/docs","status":"active"}`
- **Docs**: `https://[seu-app].up.railway.app/docs`
  - Interface Swagger da API

## ⚠️ Observação Importante

O Railway pode ter limitações ao expor múltiplas portas em um único serviço. Se você encontrar problemas para acessar o frontend na porta `$PORT + 1`, considere:

**Alternativa A**: Criar dois serviços separados no Railway
- Serviço 1: Backend (FastAPI)
- Serviço 2: Frontend (Streamlit)

**Alternativa B**: Usar apenas o backend
- Acessar a API via `/docs`
- Integrar frontend em outro serviço/domínio

## 📊 Status Atual

✅ Script de inicialização criado  
✅ Procfile atualizado  
✅ Documentação atualizada  
✅ Script de teste local criado  
✅ Pronto para deploy!

## 🆘 Precisa de Ajuda?

Consulte:
- `RAILWAY_DEPLOY.md` - Documentação completa
- `COMO_RODAR.md` - Guia geral de execução
- Logs do Railway - Para troubleshooting

---

**Próximo passo**: Faça commit das mudanças e push para o GitHub. O Railway fará o redeploy automaticamente! 🚀
