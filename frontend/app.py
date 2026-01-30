import streamlit as st
import requests
import pandas as pd
import json
from datetime import datetime

import os

# No Railway, o frontend precisa saber onde o backend está.
# Se não estiver setado, assume localhost para desenvolvimento local.
API_URL = os.getenv("BACKEND_URL", "http://localhost:8000")


st.set_page_config(layout="wide", page_title="Leitor Inteligente")

# -- Session State Init --
if 'token' not in st.session_state:
    st.session_state['token'] = None
if 'user' not in st.session_state:
    st.session_state['user'] = None
if 'is_admin' not in st.session_state:
    st.session_state['is_admin'] = False
if 'view_mode' not in st.session_state:
    st.session_state['view_mode'] = 'padrao' # padrao | foco

# -- Helper Functions --
def format_currency(val):
    if val is None: return "R$ 0,00"
    try:
        return f"R$ {float(val):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except:
        return str(val)

def format_date(val):
    if not val: return "-"
    try:
        # Check if already isoformat YYYY-MM-DD
        dt = datetime.fromisoformat(str(val))
        return dt.strftime("%d/%m/%Y")
    except:
        return str(val)
def api_get(endpoint, params=None):
    headers = {"Authorization": f"Bearer {st.session_state['token']}"} if st.session_state['token'] else {}
    try:
        resp = requests.get(f"{API_URL}/{endpoint}", params=params, headers=headers)
        if resp.status_code == 200:
            return resp.json()
        elif resp.status_code == 401:
            st.session_state['token'] = None
            st.rerun()
    except Exception as e:
        st.error(f"API Error: {e}")
    return None

def api_post(endpoint, data=None, files=None):
    headers = {"Authorization": f"Bearer {st.session_state['token']}"} if st.session_state['token'] else {}
    try:
        if files:
            # When files are present, do not set Content-Type header manually for multipart
            resp = requests.post(f"{API_URL}/{endpoint}", data=data, files=files, headers=headers)
        else:
            resp = requests.post(f"{API_URL}/{endpoint}", json=data, headers=headers)
            
        return resp
    except Exception as e:
        st.error(f"API Error: {e}")
        return None

# -- Pages --

def login_page():
    st.title("🔐 Login - Leitor Inteligente")
    
    col1, col2, col3 = st.columns([1,1,1])
    with col2:
        username = st.text_input("Usuário")
        password = st.text_input("Senha", type="password")
        
        if st.button("Entrar", use_container_width=True):
            data = {"username": username, "password": password}
            # Auth endpoint expects form data, not json
            try:
                resp = requests.post(f"{API_URL}/token", data=data)
                if resp.status_code == 200:
                    token_data = resp.json()
                    st.session_state['token'] = token_data['access_token']
                    st.session_state['user'] = username
                    
                    # Verify admin status (simple logic for now, ideally decoded from token or fetched)
                    # For strictly adhering to requested "user permissions", we might fetch user details?
                    # But token doesn't have is_admin. We can infer or fetchme.
                    # Simplified: if user is admin, assume admin capabilities.
                    if username == "admin": 
                        st.session_state['is_admin'] = True
                    else:
                        st.session_state['is_admin'] = False # Todo: fetch user details
                    
                    st.rerun()
                else:
                    st.error("Usuário ou senha incorretos")
            except Exception as e:
                st.error(f"Connection Failed: {e}")

def page_novo_processo():
    st.header("✨ Novo Processo")
    
    with st.form("new_process_form"):
        numero = st.text_input("Número do Processo")
        nome = st.text_input("Descrição / Nome")
        
        pdf_file = st.file_uploader("Arquivo PDF (Obrigatório)", type="pdf")
        map_file = st.file_uploader("Planilha Mapeamento (Opcional)", type="xlsx")
        cat_file = st.file_uploader("Planilha Catalogador (Opcional)", type="xlsx")
        
        st.markdown("---")
        st.markdown("###### Configuração de Texto para IA (Chatbot)")
        txt_file = st.file_uploader("Arquivo Texto Extraído (Opcional - Required for Chat)", type="txt")
        marker = st.text_input("Marcador de Página (ex: [[PAGINA]])", help="String usada para separar as páginas no arquivo texto.")
        
        submitted = st.form_submit_button("Cadastrar Processo")
        
        if submitted:
            if not numero or not pdf_file:
                st.warning("Número e PDF são obrigatórios.")
            else:
                files = [('file_pdf', pdf_file)]
                if map_file: files.append(('file_mapeamento', map_file))
                if cat_file: files.append(('file_catalogador', cat_file))
                if txt_file: files.append(('file_texto', txt_file))
                
                payload = {"numero": numero, "nome": nome, "marcador_pagina": marker}
                
                with st.spinner("Enviando e Processando..."):
                    resp = api_post("processos", data=payload, files=files)
                    if resp and resp.status_code == 200:
                        st.success("Processo cadastrado com sucesso!")
                    else:
                        err = resp.text if resp else "Erro desconhecido"
                        st.error(f"Falha ao cadastrar: {err}")

def page_admin():
    st.header("🛠️ Administração")
    
    st.subheader("Cadastrar Usuário")
    with st.form("new_user"):
        u_name = st.text_input("Username")
        u_pass = st.text_input("Password", type="password")
        u_admin = st.checkbox("É Admin?")
        u_create = st.checkbox("Pode criar usuários?")
        
        if st.form_submit_button("Criar Usuário"):
            payload = {
                "username": u_name, 
                "password": u_pass, 
                "is_admin": u_admin, 
                "can_create_users": u_create
            }
            resp = api_post("users", data=payload)
            if resp and resp.status_code == 200:
                st.success(f"Usuário {u_name} criado.")
            else:
                st.error(f"Erro: {resp.text if resp else ''}")

def page_dashboard():
    # Fetch Processes
    processos = api_get("processos") or []
    proc_options = {p['id']: f"{p['numero_processo']} - {p.get('nome_descricao','NA')}" for p in processos}
    
    # -- Sidebar Filters --
    st.sidebar.markdown("## Seleção")
    
    # Search Process
    # Check if we have many processes implies lazy loading needed, 
    # but for now a text filter helper
    filter_proc_text = st.sidebar.text_input("Filtrar Lista de Processos")
    filtered_options = proc_options
    if filter_proc_text:
        filtered_options = {k:v for k,v in proc_options.items() if filter_proc_text.lower() in v.lower()}
    
    selected_proc_id = st.sidebar.selectbox(
        "Selecione o Processo", 
        options=list(filtered_options.keys()), 
        format_func=lambda x: filtered_options[x]
    )
    
    if not selected_proc_id:
        st.info("Selecione um processo.")
        return

    # Load Details
    curr_proc = next((p for p in processos if p['id'] == selected_proc_id), None)
    
    # Load dynamic Types
    tipos_disponiveis = api_get(f"processos/{selected_proc_id}/tipos_evidencia") or []
    
    # -- Sidebar Content (Filtros & Evidências) --
    st.sidebar.markdown("---")
    st.sidebar.subheader("Filtros & Evidências")
    
    # Contextual Filters
    f_q = st.sidebar.text_input("Busca Textual", placeholder="Termo...")
    f_tipo = st.sidebar.selectbox("Tipo Evidência", options=["Todos"] + tipos_disponiveis)
    
    # Fetch Evidence
    params = {}
    if f_q: params['q'] = f_q
    if f_tipo and f_tipo != "Todos": params['tipo'] = f_tipo
    
    evidencias = api_get(f"processos/{selected_proc_id}/evidencias", params=params) or []
    
    st.sidebar.markdown(f"**Resultados:** {len(evidencias)}")
    
    # List Evidences in Sidebar
    for ev in evidencias:
        with st.sidebar.expander(f"Pg. {ev['pagina_inicial']} - {ev['tipo'] or ev['source_type'].title()}"):
            # Content
            resumo = ev['resumo_conteudo']
            st.markdown(f"**Resumo:** {resumo}")
            if ev['valor']:
                st.markdown(f"**Valor:** R$ {ev['valor']}")
            
            # Full Content logic
            original = ev.get('original_data', {})
            completo = original.get('trecho') or original.get('conteudo') or ""
            
            # Buttons Row
            b1, b2, b3 = st.columns([1,1,1])
            if b1.button("👁️ PDF", key=f"btn_pdf_{ev['source_type']}_{ev['id']}"):
                st.session_state['pdf_page'] = ev['pagina_inicial']
                st.session_state['pdf_highlight'] = completo
            
            if b2.button("📋 Detalhes", key=f"btn_det_{ev['source_type']}_{ev['id']}"):
                @st.dialog("Detalhes da Evidência", width="large")
                def show_details(data, tipo_origem):
                    # Separate long text from structured data
                    long_text_fields = ['trecho', 'conteudo', 'resumo']
                    structured_data = {k: v for k, v in data.items() if k not in long_text_fields and v is not None}
                    
                    # Format specific fields
                    if 'valor_total' in structured_data:
                        structured_data['valor_total'] = format_currency(structured_data['valor_total'])
                    if 'data_emissao' in structured_data:
                        structured_data['data_emissao'] = format_date(structured_data['data_emissao'])
                        
                    st.subheader("Dados Estruturados")
                    st.table(pd.DataFrame([structured_data]).T.rename(columns={0: "Valor"}))
                    
                    st.subheader("Conteúdo Textual")
                    for field in long_text_fields:
                        if field in data and data[field]:
                            with st.expander(f"{field.capitalize()}", expanded=True):
                                st.markdown(data[field])

                show_details(original, ev['source_type'])

            if b3.button("📄 Copiar", key=f"btn_txt_{ev['source_type']}_{ev['id']}"):
                # Fetch text content
                page_num = ev['pagina_inicial']
                if not page_num:
                    st.warning("Página não definida.")
                else:
                    resp_txt = api_get(f"processos/{selected_proc_id}/pagina_texto", params={"pagina": page_num})
                    if resp_txt and 'conteudo' in resp_txt:
                        @st.dialog(f"Texto da Página {page_num}", width="large")
                        def show_text_copy(txt):
                            st.text_area("Conteúdo", value=txt, height=400)
                            st.info("Ctrl+C para copiar.")
                        show_text_copy(resp_txt['conteudo'])
                    else:
                        st.error("Não foi possível obter o texto (Verifique se o arquivo texto foi enviado).")

    # -- Chatbot Section --
    st.sidebar.markdown("---")
    with st.sidebar.expander("💬 Chatbot Especializado", expanded=False):
        # Session Management
        # Check if we have an active session for this process
        if 'chat_session_id' not in st.session_state or st.session_state.get('chat_proc_id') != selected_proc_id:
            st.session_state['chat_session_id'] = None
            st.session_state['chat_proc_id'] = selected_proc_id
            st.session_state['chat_messages'] = []
        
        # Button to Start New Session with Current Filter
        if st.button("✨ Iniciar Nova Sessão com Filtro Atual"):
            # Prepare payload (evidences)
            # We send the filtered 'evidencias' list to create the context
            # To avoid huge payload, we pick only ID and Page info if possible, but our backend expects the list to build summary.
            # Let's clean the list a bit to minimal required fields if needed, or send as is.
            # Backend expects List[dict] matching schema... roughly. It uses .get() so loose dict is fine.
            
            with st.spinner("Criando contexto..."):
                resp = api_post(f"processos/{selected_proc_id}/chat_sessions", data={"evidencias": evidencias}) # Using 'data' as body for pydantic model? requests.post(json=...)
                # Wait, api_post helper uses json=data. Correct.
                
                if resp and resp.status_code == 200:
                    session_data = resp.json()
                    st.session_state['chat_session_id'] = session_data['id']
                    st.session_state['chat_messages'] = [] # Reset local msgs
                    st.success("Sessão iniciada!")
                    st.rerun()
                else:
                    st.error("Falha ao criar sessão.")

        # Chat Interface
        if st.session_state['chat_session_id']:
            # Load History if empty
            if not st.session_state['chat_messages']:
                msgs = api_get(f"chat_sessions/{st.session_state['chat_session_id']}/messages")
                if msgs:
                    st.session_state['chat_messages'] = msgs
            
            # Display Chat
            chat_container = st.container(height=400)
            with chat_container:
                for msg in st.session_state['chat_messages']:
                    with st.chat_message(msg['role']):
                        st.markdown(msg['content'])
            
            # Input
            if prompt := st.chat_input("Pergunte sobre as evidências..."):
                # Optimistic UI
                st.session_state['chat_messages'].append({"role": "user", "content": prompt})
                with chat_container:
                     with st.chat_message("user"):
                        st.markdown(prompt)
                
                # Send to Backend
                payload = {"role": "user", "content": prompt}
                resp = api_post(f"chat_sessions/{st.session_state['chat_session_id']}/messages", data=payload)
                
                if resp and resp.status_code == 200:
                    ai_msg = resp.json() # {"role": "assistant", "content": "..."}
                    st.session_state['chat_messages'].append(ai_msg)
                    st.rerun() # To refresh UI properly inside sidebar?
                else:
                    st.error("Erro ao enviar mensagem.")

    # -- Main Content (PDF Viewer Only) --
    st.subheader(f"Visualizador: {curr_proc['numero_processo']}")
    render_pdf_viewer(curr_proc, height="1000px")
            


def render_pdf_viewer(processo, height="800px"):
    if not processo or not processo.get('caminho_pdf'):
        st.warning("Sem PDF cadastrado.")
        return
        
    current_page = st.session_state.get('pdf_page', 1)
    highlight_text = st.session_state.get('pdf_highlight', '')
    
    full_pdf_url = f"{API_URL}/static/{processo['caminho_pdf']}"
    viewer_url = f"{API_URL}/static/viewer.html?file={full_pdf_url}&page={current_page}&highlight={highlight_text}"
    
    st.markdown(
        f'<iframe src="{viewer_url}" width="100%" height="{height}" style="border: none;"></iframe>',
        unsafe_allow_html=True
    )

# -- Main Logic --

if not st.session_state['token']:
    login_page()
else:
    # Sidebar Navigation
    st.sidebar.title("Navegação")
    menu_options = ["Dashboard", "Novo Processo"]
    if st.session_state['is_admin']:
        menu_options.append("Admin")
        
    choice = st.sidebar.radio("Ir para:", menu_options)
    
    if st.sidebar.button("Sair"):
        st.session_state['token'] = None
        st.rerun()
    
    st.sidebar.markdown("---")
    
    if choice == "Dashboard":
        page_dashboard()
    elif choice == "Novo Processo":
        page_novo_processo()
    elif choice == "Admin":
        page_admin()
