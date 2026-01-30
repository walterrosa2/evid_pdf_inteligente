from sqlalchemy import Column, Integer, String, Text, Date, Numeric, ForeignKey, DateTime, Boolean, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base

class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    can_create_users = Column(Boolean, default=False)

class Processo(Base):
    __tablename__ = "processos"

    id = Column(Integer, primary_key=True, index=True)
    numero_processo = Column(String, index=True)
    nome_descricao = Column(String)
    caminho_pdf = Column(String)
    caminho_texto = Column(String, nullable=True) # New: Path to full text file
    marcador_pagina = Column(String, nullable=True) # New: Marker used to split pages (e.g., [[PAGINA]])
    data_cadastro = Column(DateTime, default=datetime.utcnow)

    # Relationships
    evidencias_mapeadas = relationship("EvidenciaMapeada", back_populates="processo", cascade="all, delete-orphan")
    evidencias_catalogadas = relationship("EvidenciaCatalogada", back_populates="processo", cascade="all, delete-orphan")
    chat_sessions = relationship("ChatSession", back_populates="processo", cascade="all, delete-orphan")

class ChatSession(Base):
    __tablename__ = "chat_sessions"

    id = Column(Integer, primary_key=True, index=True)
    processo_id = Column(Integer, ForeignKey("processos.id"))
    name = Column(String) # E.g., "Analysis 12/05"
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Optional: store a summary of the context used (IDs of evidences) to replicate state if needed
    context_summary = Column(Text, nullable=True) 

    processo = relationship("Processo", back_populates="chat_sessions")
    messages = relationship("ChatMessage", back_populates="session", cascade="all, delete-orphan")

class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("chat_sessions.id"))
    role = Column(String) # "user" or "assistant"
    content = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    session = relationship("ChatSession", back_populates="messages")

class EvidenciaMapeada(Base):
    __tablename__ = "evidencias_mapeadas"

    id = Column(Integer, primary_key=True, index=True)
    processo_id = Column(Integer, ForeignKey("processos.id"))
    
    tipo_evidencia = Column(String)
    conteudo = Column(Text)
    resumo = Column(Text)
    referencia_original = Column(String)
    pagina_inicial = Column(Integer)
    pagina_final = Column(Integer)
    trecho = Column(Text)

    dados_extras = Column(JSON, nullable=True)

    processo = relationship("Processo", back_populates="evidencias_mapeadas")

class EvidenciaCatalogada(Base):
    __tablename__ = "evidencias_catalogadas"

    id = Column(Integer, primary_key=True, index=True)
    processo_id = Column(Integer, ForeignKey("processos.id"))

    origem_tipo = Column(String)
    trecho = Column(Text)
    referencia_original = Column(String)
    pagina_inicial = Column(Integer)
    pagina_final = Column(Integer)
    
    # Fiscal Data
    chave_nfe = Column(String, index=True)
    cnpj_emitente = Column(String, index=True)
    cnpj_destinatario = Column(String)
    numero_nf = Column(String)
    serie = Column(String)
    data_emissao = Column(Date)
    valor_total = Column(Numeric(precision=15, scale=2))
    cfop = Column(String)
    documento_ref = Column(String)
    
    dados_extras = Column(JSON, nullable=True)

    processo = relationship("Processo", back_populates="evidencias_catalogadas")
