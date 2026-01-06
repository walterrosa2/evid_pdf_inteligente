
import pandas as pd
import re
from sqlalchemy.orm import Session
from .models import Processo, EvidenciaMapeada, EvidenciaCatalogada
from datetime import datetime

def parse_reference(ref: str):
    """
    Parses a reference string to extract start and end page numbers.
    Examples:
    "fls. 10" -> (10, 10)
    "fls. 10/12" -> (10, 12)
    "fls. 10-12" -> (10, 12)
    "Pág. 5" -> (5, 5)
    """
    if not isinstance(ref, str):
        return None, None
    
    # Clean string
    ref = ref.lower().strip()
    
    # Extract all numbers
    numbers = [int(n) for n in re.findall(r'\d+', ref)]
    
    if not numbers:
        return None, None
    
    if len(numbers) == 1:
        return numbers[0], numbers[0]
    
    if len(numbers) >= 2:
        # Check if it's likely a range (sequential or close)
        # For now, simply take the first two as start/end
        return numbers[0], numbers[1]
    
    return None, None

def clean_row_data(row_dict):
    cleaned = {}
    for k, v in row_dict.items():
        if pd.isna(v):
            cleaned[k] = None
        elif isinstance(v, (pd.Timestamp, datetime)):
            cleaned[k] = v.isoformat()
        else:
            cleaned[k] = v
    return cleaned

def import_mapeamento(db: Session, processo_id: int, file_path: str):
    try:
        df = pd.read_excel(file_path)
    except Exception as e:
        print(f"Error reading Mapeamento excel: {e}")
        return

    # Normalize headers
    df.columns = [c.strip() for c in df.columns]

    for _, row in df.iterrows():
        tipo = row.get('Tipo de Evidência')
        trecho = row.get('Trecho')
        conteudo = row.get('Conteúdo')
        resumo = row.get('Resumo')
        ref = str(row.get('Referência', ''))

        pg_ini, pg_fim = parse_reference(ref)

        # Full row data for JSON storage
        extra_data = clean_row_data(row.to_dict())

        evidencia = EvidenciaMapeada(
            processo_id=processo_id,
            tipo_evidencia=tipo,
            conteudo=conteudo,
            resumo=resumo,
            trecho=trecho,
            referencia_original=ref,
            pagina_inicial=pg_ini,
            pagina_final=pg_fim,
            dados_extras=extra_data
        )
        db.add(evidencia)
    
    db.commit()

def import_catalogador(db: Session, processo_id: int, file_path: str):
    try:
        df = pd.read_excel(file_path)
    except Exception as e:
        print(f"Error reading Catalogador excel: {e}")
        return

    df.columns = [c.strip() for c in df.columns]

    for _, row in df.iterrows():
        # Full row data for JSON storage
        extra_data = clean_row_data(row.to_dict())

        evidencia = EvidenciaCatalogada(
            processo_id=processo_id,
            origem_tipo=row.get('origem_tipo'),
            trecho=row.get('trecho'),
            referencia_original=str(row.get('referencia', '')),
            # fiscal fields
            chave_nfe=str(row.get('chave_nfe')) if pd.notna(row.get('chave_nfe')) else None,
            cnpj_emitente=str(row.get('cnpj_emitente')) if pd.notna(row.get('cnpj_emitente')) else None,
            cnpj_destinatario=str(row.get('cnpj_destinatario')) if pd.notna(row.get('cnpj_destinatario')) else None,
            numero_nf=str(row.get('numero_nf')) if pd.notna(row.get('numero_nf')) else None,
            serie=str(row.get('serie')) if pd.notna(row.get('serie')) else None,
            valor_total=row.get('valor_total') if pd.notna(row.get('valor_total')) else None,
            cfop=str(row.get('cfop')) if pd.notna(row.get('cfop')) else None,
            documento_ref=str(row.get('documento_ref')) if pd.notna(row.get('documento_ref')) else None,
            dados_extras=extra_data
        )

        # Parse reference
        if evidencia.referencia_original:
            pg_ini, pg_fim = parse_reference(evidencia.referencia_original)
            evidencia.pagina_inicial = pg_ini
            evidencia.pagina_final = pg_fim

        # Date handling
        dt_emissao = row.get('data_emissao')
        if pd.notna(dt_emissao):
            if isinstance(dt_emissao, datetime):
                evidencia.data_emissao = dt_emissao.date()

        db.add(evidencia)
    
    db.commit()

def create_processo(db: Session, numero: str, nome: str, pdf_path: str):
    processo = Processo(
        numero_processo=numero,
        nome_descricao=nome,
        caminho_pdf=pdf_path
    )
    db.add(processo)
    db.commit()
    db.refresh(processo)
    return processo
