# Deploy Railway - Leitor Inteligente

## 📋 Resumo da Configuração

Este projeto está configurado para rodar **Backend (FastAPI)** e **Frontend (Streamlit)** em um único serviço no Railway.

## 🚀 Como Funciona

### Arquivos de Configuração

1. **`Procfile`**: Define o comando de inicialização
   ```
   web: python start_services.py
   ```

2. **`start_services.py`**: Script Python que:
   - Inicia o backend FastAPI na porta `$PORT`
   - Inicia o frontend Streamlit na porta `$PORT + 1`
   - Monitora ambos os processos
   - Gerencia encerramento gracioso

3. **`railway.toml`**: Configurações de build do Railway

## 🔧 Variáveis de Ambiente Necessárias

Configure no painel do Railway:

| Variável | Descrição | Obrigatório |
|----------|-----------|-------------|
| `GOOGLE_API_KEY` | Chave da API do Google Gemini | ✅ Sim |
| `GEMINI_MODEL` | Modelo do Gemini (padrão: `gemini-2.0-flash`) | ❌ Não |
| `SECRET_KEY` | Chave secreta para JWT | ❌ Não (gerada automaticamente) |

## 📦 Deploy Passo a Passo

### 1. Criar Projeto no Railway
- Acesse [railway.app](https://railway.app)
- Clique em "New Project"
- Selecione "Deploy from GitHub repo"
- Escolha este repositório

### 2. Configurar Variáveis de Ambiente
- No painel do projeto, vá em "Variables"
- Adicione `GOOGLE_API_KEY` com sua chave do Gemini
- (Opcional) Adicione outras variáveis conforme necessário

### 3. Deploy Automático
- O Railway detectará o `Procfile` automaticamente
- O build será iniciado usando as configurações do `railway.toml`
- Aguarde a conclusão do deploy

### 4. Verificar Serviços

Após o deploy, você terá acesso a:

- **API Backend**: `https://[seu-app].up.railway.app/`
  - Retorna: `{"message":"Leitor Inteligente API está online!","docs":"/docs","status":"active"}`
  
- **Documentação Swagger**: `https://[seu-app].up.railway.app/docs`
  - Interface interativa da API
  
- **Frontend Streamlit**: `https://[seu-app].up.railway.app:[PORT+1]`
  - Interface visual do aplicativo

## 📊 Monitoramento

### Logs
Acesse os logs no painel do Railway para ver:
- ✅ Inicialização do backend
- ✅ Inicialização do frontend
- ✅ PIDs dos processos
- ✅ Portas utilizadas

### Exemplo de Log Esperado:
```
16:00:00 | INFO     | 🚀 Iniciando Leitor Inteligente...
16:00:00 | INFO     | 📡 Backend será executado na porta: 8000
16:00:00 | INFO     | 🎨 Frontend será executado na porta: 8001
16:00:00 | INFO     | 📡 Iniciando Backend (FastAPI)...
16:00:03 | SUCCESS  | ✅ Backend rodando no PID: 123
16:00:03 | INFO     | 🎨 Iniciando Frontend (Streamlit)...
16:00:05 | SUCCESS  | ✅ Frontend rodando no PID: 456
16:00:05 | SUCCESS  | 🎉 Todos os serviços iniciados com sucesso!
```

## 🔍 Troubleshooting

### Problema: "Command not found"
**Solução**: Verifique se `requirements.txt` inclui todas as dependências:
```
fastapi
uvicorn
streamlit
loguru
```

### Problema: Backend ou Frontend não inicia
**Solução**: 
1. Verifique os logs do Railway
2. Confirme que `GOOGLE_API_KEY` está configurada
3. Verifique se há erros de importação

### Problema: Não consigo acessar o frontend
**Solução**: 
- O Railway pode não expor múltiplas portas automaticamente
- Considere criar dois serviços separados (Opção 1) se necessário
- Ou configure um proxy reverso

## 🔄 Alternativa: Dois Serviços Separados

Se preferir rodar backend e frontend em serviços separados:

1. **Serviço 1 - Backend**:
   - Procfile: `web: uvicorn backend.main:app --host 0.0.0.0 --port $PORT`
   
2. **Serviço 2 - Frontend**:
   - Procfile: `web: streamlit run frontend/app.py --server.port $PORT --server.address 0.0.0.0`
   - Variável adicional: `BACKEND_URL` apontando para o serviço 1

## 📝 Notas Importantes

- ⚠️ O Railway pode ter limitações com múltiplas portas em um único serviço
- ✅ O backend sempre estará acessível na porta principal
- ⚠️ O frontend pode precisar de configuração adicional de rede
- 💾 Adicione um volume em `/app/data` para persistência do banco SQLite

## 🆘 Suporte

Se encontrar problemas:
1. Verifique os logs do Railway
2. Confirme todas as variáveis de ambiente
3. Teste localmente com `python start_services.py`
4. Consulte a documentação do Railway sobre múltiplas portas
