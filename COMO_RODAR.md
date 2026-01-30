# Guia de Execução - Leitor Inteligente

Este documento contém os comandos necessários para instalar as dependências e iniciar os servidores do projeto.

---

## 1. Instalação de Dependências
Antes de iniciar, certifique-se de que o ambiente virtual está ativo e instale as bibliotecas necessárias:

```powershell
# Instalar todas as dependências do projeto
pip install -r requirements.txt
```

---

## 2. Configuração do Ambiente (.env)
Certifique-se de que existe um arquivo `.env` na raiz do projeto com as seguintes chaves:

```env
GOOGLE_API_KEY=Sua_Chave_Aqui
GEMINI_MODEL=gemini-2.0-flash
```

---

## 3. Como Iniciar os Servidores

Você precisará de **dois terminais abertos** na pasta raiz do projeto:

### Terminal 1: Servidor App (Backend - FastAPI)
Este servidor gerencia o banco de dados, arquivos e as chamadas à IA.
```powershell
uvicorn backend.main:app --reload
```
*O servidor estará disponível em: `http://localhost:8000`*

### Terminal 2: Interface (Frontend - Streamlit)
Este comando abre a interface visual no seu navegador.
```powershell
streamlit run frontend/app.py
```
*A interface abrirá em: `http://localhost:8501` (ou na porta configurada)*

---

## 4. Deploy no Railway

Este projeto está configurado para deploy automático no **Railway**.

### Passos para Deploy:
1. **Conectar Repositório**: Crie um novo projeto no Railway e conecte este repositório do GitHub.
2. **Serviços**: O Railway detectará o arquivo `railway.toml` e criará os serviços de **Backend** e **Frontend**.
3. **Variáveis de Ambiente**:
   - `GOOGLE_API_KEY`: Sua chave do Gemini.
   - `DATA_PATH`: `/app/data` (Para persistência).
   - `BACKEND_URL`: A URL pública gerada para o serviço de Backend (Configurar no serviço do Frontend).
4. **Volumes (Importante)**:
   - Adicione um volume montado em `/app/data` em ambos os serviços se desejar compartilhar o banco de dados e uploads, ou apenas no Backend para persistência.

---

## Observações Importantes:
- **Banco de Dados:** O sistema utiliza SQLite (`leitor_inteligente_v2.db`). No ambiente produtivo, garanta que o arquivo esteja em um volume persistente.
- **Chatbot:** Para o chatbot funcionar, é indispensável que o arquivo Texto do processo seja enviado no momento do cadastro e que o marcador de página esteja correto.
- **Logs:** Os logs de execução e auditoria de prompts podem ser consultados em `backend/logs/`.
