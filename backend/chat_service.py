import os
import google.generativeai as genai
from sqlalchemy.orm import Session
from .models import ChatSession, ChatMessage, Processo
from . import text_service
from dotenv import load_dotenv

# Load env vars
load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")

if GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)

from loguru import logger
import datetime

# Configure Loguru
log_dir = os.path.join(os.path.dirname(__file__), "logs")
if not os.path.exists(log_dir):
    os.makedirs(log_dir)
logger.add(os.path.join(log_dir, "chatbot.log"), rotation="10 MB", level="INFO")

def save_prompt_evidence(session_id: int, prompt: str, response: str):
    """Saves the full prompt and response to a file for auditing."""
    evidence_dir = os.path.join(log_dir, "prompts")
    if not os.path.exists(evidence_dir):
        os.makedirs(evidence_dir)
    
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"prompt_session_{session_id}_{timestamp}.txt"
    filepath = os.path.join(evidence_dir, filename)
    
    with open(filepath, "w", encoding="utf-8") as f:
        f.write("=== SYSTEM PROMPT + CONTEXT ===\n")
        f.write(prompt)
        f.write("\n\n=== RESPONSE ===\n")
        f.write(response)
    
    logger.info(f"Evidência de prompt salva em: {filepath}")

def get_system_prompt():
    """Reads the system prompt from file."""
    try:
        base_path = os.path.dirname(os.path.dirname(__file__))
        prompt_path = os.path.join(base_path, "prompt", "prompt_chatbot.txt")
        with open(prompt_path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        logger.error(f"Erro ao ler arquivo de prompt: {e}")
        return "Você é um assistente útil."

def process_user_message(db: Session, session_id: int, user_content: str):
    """
    1. Saves user message.
    2. Builds context.
    3. Calls Gemini.
    4. Records evidence and returns response.
    """
    logger.info(f"Iniciando processamento de mensagem para sessão {session_id}")
    
    # 1. Inspect Session
    session = db.query(ChatSession).filter(ChatSession.id == session_id).first()
    if not session:
        logger.warning(f"Sessão {session_id} não encontrada no banco.")
        return "Sessão não encontrada."
    
    # 2. Save User Message
    msg_user = ChatMessage(session_id=session_id, role="user", content=user_content)
    db.add(msg_user)
    db.commit()

    # 3. Build Context
    history_msgs = db.query(ChatMessage).filter(ChatMessage.session_id == session_id).order_by(ChatMessage.created_at).all()
    gemini_history = []
    system_instr = get_system_prompt()
    
    match_context = ""
    if session.context_summary:
        match_context = f"\n\nCONTEXTO DO PROCESSO:\n{session.context_summary}\n\n"

    full_system_context = system_instr + match_context
    model = genai.GenerativeModel(GEMINI_MODEL, system_instruction=full_system_context)
    
    for m in history_msgs:
        if m.id == msg_user.id: continue
        role = "user" if m.role == "user" else "model"
        gemini_history.append({"role": role, "parts": [m.content]})
        
    chat = model.start_chat(history=gemini_history)
    
    try:
        logger.info(f"Enviando prompt ao Gemini (Modelo: {GEMINI_MODEL})...")
        response = chat.send_message(user_content)
        ai_text = response.text
        
        # Enviar evidência do que foi enviado
        prompt_to_log = f"SYSTEM INSTRUCTION:\n{full_system_context}\n\nHISTORY:\n{gemini_history}\n\nUSER MESSAGE:\n{user_content}"
        save_prompt_evidence(session_id, prompt_to_log, ai_text)
        
    except Exception as e:
        ai_text = f"Erro ao comunicar com Gemini: {str(e)}"
        logger.error(ai_text)
        save_prompt_evidence(session_id, f"ERROR PROMPT: {user_content}", ai_text)

    # 4. Save AI Response
    msg_ai = ChatMessage(session_id=session_id, role="model", content=ai_text)
    db.add(msg_ai)
    db.commit()
    
    return ai_text

def create_session(db: Session, processo_id: int, context_data: dict):
    """
    Creates a new chat session with initial context summary.
    context_data: {'evidencias': [...], 'paginas_texto': {...}}
    """
    # 1. Build Metadata Summary of Evidences
    summary_lines = ["RESUMO DAS EVIDÊNCIAS SELECIONADAS NO FILTRO:"]
    evidences = context_data.get('evidencias', [])
    pages_to_include = set()

    for ev in evidences:
        summary_lines.append(f"- Tipo: {ev.get('tipo', 'N/A')}")
        summary_lines.append(f"  Resumo: {ev.get('resumo_conteudo', 'N/A')}")
        pg = ev.get('pagina_inicial')
        summary_lines.append(f"  Página Original no PDF: {pg}")
        if pg:
            pages_to_include.add(pg)
        summary_lines.append("---")

    # 2. Add Unique Page Contents (Deduplicated)
    summary_lines.append("\nCONTEÚDO TEXTUAL DAS PÁGINAS MENCIONADAS (PARA CONSULTA):")
    page_texts = context_data.get('paginas_texto', {})
    
    for pg in sorted(list(pages_to_include)):
        txt = page_texts.get(str(pg)) or page_texts.get(pg)
        if txt:
             summary_lines.append(f"\n[TEXTO INTEGRAL DA PÁGINA {pg}]:")
             summary_lines.append(txt[:5000]) # Increased limit to 5k as Flash has large context, but avoiding extreme single page junk
             summary_lines.append("-" * 30)
        else:
             summary_lines.append(f"\n[TEXTO DA PÁGINA {pg} NÃO DISPONÍVEL NO ARQUIVO .TXT]")

    full_summary = "\n".join(summary_lines)
    
    # Name it
    proc = db.query(Processo).filter(Processo.id == processo_id).first()
    proc_num = proc.numero_processo if proc else "Processo"
    import datetime
    name = f"Chat {proc_num} - {datetime.datetime.now().strftime('%d/%m %H:%M')}"

    session = ChatSession(processo_id=processo_id, name=name, context_summary=full_summary)
    db.add(session)
    db.commit()
    db.refresh(session)
    logger.info(f"Sessão de chat criada para processo {processo_id} com {len(pages_to_include)} páginas únicas de contexto.")
    return session
