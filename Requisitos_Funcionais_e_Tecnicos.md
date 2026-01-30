# Documento de Requisitos Funcionais e Técnicos
**Projeto:** Leitor Inteligente - Melhorias e Chatbot
**Versão:** 1.0
**Status:** Aguardando Aprovação

## Visão Geral
Este documento detalha a estratégia técnica para implementação de três novas funcionalidades: Chatbot Especializado por Contexto, Funcionalidade de "Copiar Texto" da evidência e Upload de Arquivo Texto do Processo.

---

## 1. Chatbot Especializado no Processo
### Requisitos Funcionais
- **Gatilho:** O chatbot deve ser acessível lateralmente (sidebar ou painel expansível) após o usuário filtrar evidências.
- **Contexto:**
  - O chat deve receber como contexto:
    1. A lista de evidências filtradas (JSON/Texto resumido).
    2. O conteúdo textual das páginas referenciadas nessas evidências (extraído do novo arquivo texto).
- **Histórico:** Cada sessão de chat deve ser salva com um nome (ex: "Análise Tributária - 12/01/2026") para consulta futura.
- **Interatividade:** O usuário pergunta sobre os dados filtrados e o LLM responde usando *apenas* o contexto fornecido.
- **Adicional** Precisaremos criar um prompt que será enviado junto com o contexto para que o LLM responda. Então crie o prompt e salve em nova pasta \prompt com nome de prompt_chatbot.txt. 

### Estratégia Técnica
#### Backend (FastAPI + SQLAlchemy)
- **Novas Tabelas no Banco de Dados:**
  - `ChatSession`: `id`, `processo_id`, `name` (string), `created_at` (datetime), `context_summary` (text - opcional, para lembrar o que foi filtrado).
  - `ChatMessage`: `id`, `session_id`, `role` ("user" | "assistant"), `content` (text), `created_at`.
- **Novos Endpoints:**
  - `POST /processos/{id}/chat_sessions`: Cria nova sessão.
  - `GET /processos/{id}/chat_sessions`: Lista histórico.
  - `GET /chat_sessions/{session_id}/messages`: Recupera mensagens antigas.
  - `POST /chat_sessions/{session_id}/messages`: Envia pergunta
    - **Lógica de RAG (Retrieval):**
      1. Recebe a pergunta.
      2. Carrega as últimas N mensagens histórico.
      3. (Otimização) O contexto estático (Evidências + Texto das Páginas) pode ser grande. Sugere-se enviá-lo como "System Message" ou "User Context" na primeira iteração ou repetido se o modelo não tiver janela de contexto longa (precisaremos usar LLM da google modelo "gemini-2.0-flash" ).*Criar arquivo .env contendo as chaves (GOOGLE_API_KEY=
GEMINI_MODEL=gemini-2.0-flash)
      4. Salva pergunta e resposta no banco.

#### Frontend (Streamlit)
- **UI:** Coluna lateral adicional ou componente `st.chat_message` em um container expansível.
- **Logica:**
  - Ao clicar em "Iniciar Chat com Filtro Atual", o front coleta o filtro atual, identifica as páginas das evidências listadas, chama o backend para criar sessão e carregar o contexto.

---

## 2. Botão "Copiar Texto" (Pagina da Evidência)
### Requisitos Funcionais
- Na lista de evidências (Sidebar), ao lado do botão "👁️ PDF", adicionar botão "📄 Copiar Texto".
- Ao clicar, o sistema busca o texto daquela página específica e exibe em um modal (dialog) pronto para copiar (ou copia direto se possível via JS injection, mas no Streamlit nativo o modal é mais seguro).

### Estratégia Técnica
- **Dependência:** Requer o "Arquivo Texto" (Item 3) já carregado e estruturado.
- **Parsing de Páginas:**
  - O arquivo texto precisa ter demarcadores de página. **Premissa:** O arquivo texto deve conter marcadores padrão como `[[PAGINA X]]` ou caractere *Form Feed* (`\f`). Caso contrário, será difícil buscar a página exata.
  - Criar um local onde o usuario possa informar o marcador de pagina daquele processo, assim será possível buscar a página exata usando o marcador informado pelo usuario.
  - *Estratégia Adotada:* O backend fará o parse do arquivo texto inteiro em memória (ou stream) e buscará o trecho correspondente à página solicitada.
- **Endpoint:**
  - `GET /processos/{id}/pagina_texto?pagina={numero}`: Retorna o string de texto daquela página.

---

## 3. Upload de Arquivo TEXTO do Processo
### Requisitos Funcionais
- No formulário "Novo Processo", adicionar campo para upload de `.txt`.
- Permitir upload posterior (endpoint `/upload_texto`) caso o processo já exista.

### Estratégia Técnica
- **Backend:**
  - Atualizar Tabela `Processo`: Adicionar coluna `caminho_texto` (String).
  - Atualizar Endpoint criação: Aceitar novo arquivo `file_texto`.
  - Salvar arquivo em `backend/static/uploads/{id}_full.txt`.
- **Frontend:**
  - Adicionar `st.file_uploader("Arquivo Texto (Extração)", type=["txt"])` na tela `Novo Processo`.

---

## Plano de Implementação Resumido (Task List)

1. **Modelagem de Dados (Backend)**
   - Criar models `ChatSession`, `ChatMessage`.
   - Migration (via `alembic` ou recriar banco se estiver em dev simples, como temos `create_all`, podemos apenas adicionar).
2. **Backend Services**
   - Serviço `TextFileService`: Funções para ler o arquivo .txt e extrair página específica.
   - Serviço `ChatService`: Funções para interagir com OpenAI.
3. **API Endpoints**
   - Implementar rotas de Chat e Texto.
4. **Frontend Integration**
   - Atualizar tela de Cadastro.
   - Implementar Interface de Chat.
   - Implementar Botão Copiar Texto.

## Dúvidas / Validações Necessárias
- [ ] **Formato do TXT:** O "Arquivo Texto Resultado da Extração" já possui marcadores de página? Se não, como saberemos onde começa/termina a página X? 
Resposta: Atraves da informacao do usuario, que informara o marcador de pagina daquele processo, sera possivel buscar a pagina exata. 

- [ ] **Motor LLM:** Confirmar que usaremos `openai` (GPT-4o/mini) via `.env`.
Resposta: Usaremos gemini-2.0-flash via google api key no arquivo .env 

