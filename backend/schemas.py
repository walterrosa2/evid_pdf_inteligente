
from pydantic import BaseModel
from typing import List, Optional
from datetime import date, datetime
from decimal import Decimal

# Shared properties
class EvidenciaBase(BaseModel):
    processo_id: int
    pagina_inicial: Optional[int] = None
    pagina_final: Optional[int] = None
    referencia_original: Optional[str] = None
    trecho: Optional[str] = None

class EvidenciaMapeadaSchema(EvidenciaBase):
    id: int
    tipo_evidencia: Optional[str] = None
    conteudo: Optional[str] = None
    resumo: Optional[str] = None

    class Config:
        from_attributes = True

class EvidenciaCatalogadaSchema(EvidenciaBase):
    id: int
    origem_tipo: Optional[str] = None
    chave_nfe: Optional[str] = None
    cnpj_emitente: Optional[str] = None
    cnpj_destinatario: Optional[str] = None
    numero_nf: Optional[str] = None
    serie: Optional[str] = None
    data_emissao: Optional[date] = None
    valor_total: Optional[Decimal] = None
    cfop: Optional[str] = None
    documento_ref: Optional[str] = None

    class Config:
        from_attributes = True

# Unified Evidence Schema for Frontend
class EvidenciaUnificada(BaseModel):
    id: int
    source_type: str  # "mapeada" or "catalogada"
    tipo: Optional[str] = None # Map 'tipo_evidencia' or 'origem_tipo' here
    resumo_conteudo: Optional[str] = None # Map 'resumo' or 'trecho'
    pagina_inicial: Optional[int]
    pagina_final: Optional[int]
    
    # Fiscal Details (Nullable)
    cnpj: Optional[str] = None
    data_emissao: Optional[date] = None
    valor: Optional[Decimal] = None

    original_data: dict # Full payload


# -- Chat Schemas --

class ChatMessageBase(BaseModel):
    role: str
    content: str

class ChatMessageCreate(ChatMessageBase):
    pass

class ChatMessageSchema(ChatMessageBase):
    id: int
    session_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class ChatSessionBase(BaseModel):
    name: str

class ChatSessionCreate(ChatSessionBase):
    processo_id: int
    context_summary: Optional[str] = None

class ChatSessionInit(BaseModel):
    evidencias: List[dict] = []

class ChatSessionSchema(ChatSessionBase):
    id: int
    created_at: datetime
    messages: List[ChatMessageSchema] = []

    class Config:
        from_attributes = True

# -- Processo Schemas --

class ProcessoBase(BaseModel):
    numero_processo: str
    nome_descricao: Optional[str] = None
    caminho_pdf: Optional[str] = None
    caminho_texto: Optional[str] = None
    marcador_pagina: Optional[str] = None

class ProcessoCreate(ProcessoBase):
    pass

class ProcessoSchema(ProcessoBase):
    id: int
    data_cadastro: datetime
    # We might not want to return all evidences in the list view, so kept optional/separate
    
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class UsuarioBase(BaseModel):
    username: str
    is_admin: bool = False
    can_create_users: bool = False

class UsuarioCreate(UsuarioBase):
    password: str

class UsuarioDisplay(UsuarioBase):
    id: int
    is_active: bool

    class Config:
        from_attributes = True
