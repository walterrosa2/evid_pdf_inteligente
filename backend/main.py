
from fastapi import FastAPI, Depends, HTTPException, Query, UploadFile, File, Form, status
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List, Optional
from datetime import timedelta
import shutil
import os
from .database import get_db, engine, Base
from .models import Processo, EvidenciaMapeada, EvidenciaCatalogada, Usuario, ChatSession, ChatMessage
from .schemas import ProcessoSchema, EvidenciaUnificada, Token, UsuarioCreate, UsuarioDisplay, ChatSessionSchema, ChatSessionCreate, ChatMessageSchema, ChatMessageCreate, ChatSessionInit
from . import auth, etl_service, text_service, chat_service
import uvicorn

# Create tables if they don't exist (helpful for auto-init)
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Leitor Inteligente API")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount Static Files
# Serve 'backend/static' at '/static'
static_dir = os.path.join(os.path.dirname(__file__), "static")
if not os.path.exists(static_dir):
    os.makedirs(static_dir)
app.mount("/static", StaticFiles(directory=static_dir), name="static")

# -- Auth Endpoints --

@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(Usuario).filter(Usuario.username == form_data.username).first()
    if not user or not auth.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/users", response_model=UsuarioDisplay)
def create_user(user: UsuarioCreate, db: Session = Depends(get_db), current_user: Usuario = Depends(auth.get_admin_user)):
    db_user = db.query(Usuario).filter(Usuario.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    hashed_password = auth.get_password_hash(user.password)
    new_user = Usuario(
        username=user.username,
        hashed_password=hashed_password,
        is_admin=user.is_admin,
        can_create_users=user.can_create_users
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

# -- Process Endpoints --

@app.post("/processos")
def create_processo_completo(
    numero: str = Form(...),
    nome: str = Form(...),
    marcador_pagina: Optional[str] = Form(None),
    file_pdf: UploadFile = File(...),
    file_mapeamento: Optional[UploadFile] = File(None),
    file_catalogador: Optional[UploadFile] = File(None),
    file_texto: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    # current_user: Usuario = Depends(auth.get_current_active_user)
):
    # Create Process
    processo = Processo(
        numero_processo=numero, 
        nome_descricao=nome, 
        caminho_pdf="",
        marcador_pagina=marcador_pagina
    )
    db.add(processo)
    db.commit()
    db.refresh(processo)

    # Ensure uploads dir exists
    uploads_dir = os.path.join(static_dir, "uploads")
    if not os.path.exists(uploads_dir):
        os.makedirs(uploads_dir)

    # Save PDF
    pdf_path = os.path.join(uploads_dir, f"{processo.id}.pdf")
    with open(pdf_path, "wb") as buffer:
        shutil.copyfileobj(file_pdf.file, buffer)
    
    processo.caminho_pdf = f"uploads/{processo.id}.pdf"
    
    # Save Text File if provided
    if file_texto:
        txt_path = os.path.join(uploads_dir, f"{processo.id}_full.txt")
        with open(txt_path, "wb") as buffer:
            shutil.copyfileobj(file_texto.file, buffer)
        processo.caminho_texto = f"uploads/{processo.id}_full.txt"

    db.commit()

    # Process Excels
    if file_mapeamento:
        map_path = os.path.join(uploads_dir, f"{processo.id}_mapeamento.xlsx")
        with open(map_path, "wb") as buffer:
            shutil.copyfileobj(file_mapeamento.file, buffer)
        etl_service.import_mapeamento(db, processo.id, map_path)
    
    if file_catalogador:
        cat_path = os.path.join(uploads_dir, f"{processo.id}_catalogador.xlsx")
        with open(cat_path, "wb") as buffer:
            shutil.copyfileobj(file_catalogador.file, buffer)
        etl_service.import_catalogador(db, processo.id, cat_path)
    
    return {"message": "Processo criado com sucesso", "id": processo.id}


@app.post("/processos/{processo_id}/upload")
def upload_pdf(processo_id: int, file: UploadFile = File(...), db: Session = Depends(get_db)):
    processo = db.query(Processo).filter(Processo.id == processo_id).first()
    if not processo:
        raise HTTPException(status_code=404, detail="Process not found")
    
    # Ensure uploads dir exists
    uploads_dir = os.path.join(static_dir, "uploads")
    if not os.path.exists(uploads_dir):
        os.makedirs(uploads_dir)
    
    # Save file
    file_location = os.path.join(uploads_dir, f"{processo_id}.pdf")
    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    # Update DB path (relative URL for frontend)
    # We serve backend/static at /static. So backend/static/uploads/1.pdf is /static/uploads/1.pdf
    processo.caminho_pdf = f"uploads/{processo_id}.pdf"
    db.commit()
    db.refresh(processo)
    
    return {"filename": file.filename, "path": processo.caminho_pdf}

# -- Endpoints --

@app.get("/processos", response_model=List[ProcessoSchema])
def list_processos(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    processos = db.query(Processo).offset(skip).limit(limit).all()
    return processos

@app.get("/processos/{processo_id}", response_model=ProcessoSchema)
def get_processo(processo_id: int, db: Session = Depends(get_db)):
    processo = db.query(Processo).filter(Processo.id == processo_id).first()
    if not processo:
        raise HTTPException(status_code=404, detail="Process not found")
    return processo

@app.get("/processos/{processo_id}/evidencias", response_model=List[EvidenciaUnificada])
def list_evidencias_processo(
    processo_id: int,
    tipo: Optional[str] = None, # Filter by type
    pg_min: Optional[int] = None,
    pg_max: Optional[int] = None,
    q: Optional[str] = None, # Free text search
    db: Session = Depends(get_db)
):
    """
    Returns a unified list of evidences (both mapped and cataloged) for a process.
    Supports filtering.
    """
    
    # 1. Query Mapeadas
    query_map = db.query(EvidenciaMapeada).filter(EvidenciaMapeada.processo_id == processo_id)
    if pg_min is not None:
        query_map = query_map.filter(EvidenciaMapeada.pagina_final >= pg_min)
    if pg_max is not None:
        query_map = query_map.filter(EvidenciaMapeada.pagina_inicial <= pg_max)
    if tipo:
        query_map = query_map.filter(EvidenciaMapeada.tipo_evidencia.ilike(f"%{tipo}%"))
    if q:
        search = f"%{q}%"
        query_map = query_map.filter(
            or_(
                EvidenciaMapeada.conteudo.ilike(search),
                EvidenciaMapeada.resumo.ilike(search),
                EvidenciaMapeada.trecho.ilike(search)
            )
        )
    
    # 2. Query Catalogadas
    query_cat = db.query(EvidenciaCatalogada).filter(EvidenciaCatalogada.processo_id == processo_id)
    if pg_min is not None:
        query_cat = query_cat.filter(EvidenciaCatalogada.pagina_final >= pg_min)
    if pg_max is not None:
        query_cat = query_cat.filter(EvidenciaCatalogada.pagina_inicial <= pg_max)
    # For cataloged, 'type' might map to 'origem_tipo'
    if tipo:
        query_cat = query_cat.filter(EvidenciaCatalogada.origem_tipo.ilike(f"%{tipo}%"))
    if q:
        search = f"%{q}%"
        query_cat = query_cat.filter(
            or_(
                EvidenciaCatalogada.trecho.ilike(search),
                EvidenciaCatalogada.chave_nfe.ilike(search),
                EvidenciaCatalogada.numero_nf.ilike(search)
            )
        )

    results_map = query_map.all()
    results_cat = query_cat.all()

    unified_results = []

    # Transform Mapeada
    for item in results_map:
        original_data = dict(item.dados_extras) if item.dados_extras else {}
        original_data.update({ 
            "referencia": item.referencia_original, 
            "trecho": item.trecho 
        })
        
        unified_results.append(EvidenciaUnificada(
            id=item.id,
            source_type="mapeada",
            tipo=item.tipo_evidencia,
            resumo_conteudo=item.resumo or item.conteudo[:200], # Fallback
            pagina_inicial=item.pagina_inicial,
            pagina_final=item.pagina_final,
            original_data=original_data
        ))

    # Transform Catalogada
    for item in results_cat:
        original_data = dict(item.dados_extras) if item.dados_extras else {}
        original_data.update({
            "chave_nfe": item.chave_nfe,
            "trecho": item.trecho
        })

        unified_results.append(EvidenciaUnificada(
            id=item.id,
            source_type="catalogada",
            tipo=item.origem_tipo,
            resumo_conteudo=f"NF: {item.numero_nf} - Valor: {item.valor_total}",
            pagina_inicial=item.pagina_inicial,
            pagina_final=item.pagina_final,
            cnpj=item.cnpj_emitente,
            data_emissao=item.data_emissao,
            valor=item.valor_total,
            original_data=original_data
        ))
    
    # Sort by page number
    unified_results.sort(key=lambda x: x.pagina_inicial or 0)
    
    return unified_results

@app.get("/processos/{processo_id}/tipos_evidencia")
def get_tipos_evidencia(processo_id: int, db: Session = Depends(get_db)):
    # Distinct types
    q_map = db.query(EvidenciaMapeada.tipo_evidencia).filter(EvidenciaMapeada.processo_id == processo_id).distinct()
    q_cat = db.query(EvidenciaCatalogada.origem_tipo).filter(EvidenciaCatalogada.processo_id == processo_id).distinct()
    
    tipos = set()
    for (t,) in q_map.all():
        if t: types = [x.strip() for x in t.split('/') if x.strip()] # Split if multiple or just add
        if t: tipos.add(t)
            
    for (t,) in q_cat.all():
        if t: tipos.add(t)
        
    return list(sorted(tipos))

# -- Text & Chat Endpoints --

@app.get("/processos/{processo_id}/pagina_texto")
def get_pagina_texto(processo_id: int, pagina: int, db: Session = Depends(get_db)):
    processo = db.query(Processo).filter(Processo.id == processo_id).first()
    if not processo or not processo.caminho_texto:
        raise HTTPException(status_code=404, detail="Arquivo de texto não encontrado para este processo.")
    
    # Resolve path
    # stored as uploads/X.txt, relative to backend/static
    real_path = os.path.join(static_dir, processo.caminho_texto.replace("/", os.sep))
    
    content = text_service.get_page_content(real_path, processo.marcador_pagina, pagina)
    return {"conteudo": content}

@app.post("/processos/{processo_id}/chat_sessions", response_model=ChatSessionSchema)
def create_chat_session(
    processo_id: int, 
    payload: ChatSessionInit, 
    db: Session = Depends(get_db)
):
    # Fetch process to get text path
    processo = db.query(Processo).filter(Processo.id == processo_id).first()
    if not processo:
        raise HTTPException(status_code=404, detail="Process not found")

    evidencias = payload.evidencias

    # Helper to fetch text pages
    # We need to know which pages to fetch.
    pages_to_fetch = set()
    for ev in evidencias:
        if ev.get('pagina_inicial'):
            pages_to_fetch.add(ev['pagina_inicial'])
    
    # Fetch texts
    paginas_texto = {}
    if processo.caminho_texto:
        real_path = os.path.join(static_dir, processo.caminho_texto.replace("/", os.sep))
        for pg in pages_to_fetch:
            if pg:
                paginas_texto[pg] = text_service.get_page_content(real_path, processo.marcador_pagina, pg)
    
    context_data = {
        "evidencias": evidencias,
        "paginas_texto": paginas_texto
    }
    
    session = chat_service.create_session(db, processo_id, context_data)
    return session

@app.get("/processos/{processo_id}/chat_sessions", response_model=List[ChatSessionSchema])
def list_chat_sessions(processo_id: int, db: Session = Depends(get_db)):
    sessions = db.query(ChatSession).filter(ChatSession.processo_id == processo_id).order_by(ChatSession.created_at.desc()).all()
    return sessions

@app.get("/chat_sessions/{session_id}/messages", response_model=List[ChatMessageSchema])
def get_chat_messages(session_id: int, db: Session = Depends(get_db)):
    msgs = db.query(ChatMessage).filter(ChatMessage.session_id == session_id).order_by(ChatMessage.created_at).all()
    return msgs

@app.post("/chat_sessions/{session_id}/messages")
def send_chat_message(session_id: int, payload: ChatMessageCreate, db: Session = Depends(get_db)):
    if payload.role != "user":
        raise HTTPException(status_code=400, detail="Only can send user messages")
    
    response_text = chat_service.process_user_message(db, session_id, payload.content)
    return {"role": "assistant", "content": response_text}

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("backend.main:app", host="0.0.0.0", port=port, reload=True)
