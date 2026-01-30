import os

def get_page_content(file_path: str, marker: str, page_num: int) -> str:
    """
    Parses the text file using the provided marker and returns the content of the specific page.
    Page numbers are assumed to be 1-based logic (User says "Page 1", we look for 1st block).
    
    If no marker is provided or file doesn't exist, returns None or specific error string.
    """
    if not os.path.exists(file_path):
        return "Arquivo de texto não encontrado."

    if not marker:
        # If no marker, return whole text or just first chunk? 
        # Requirement implies mapping evidence page to text. Without marker, impossible.
        return "Marcador de página não definido para este processo. Não é possível localizar a página específica."

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            full_text = f.read()
    except Exception as e:
        return f"Erro ao ler arquivo: {str(e)}"

    # Splitting logic
    # We assume markers separate pages.
    # Example: [[PAGINA]] Text [[PAGINA]] Text...
    # Split results in ['', 'Text 1', 'Text 2'...] depending on if marker is at start
    
    pages = full_text.split(marker)
    
    # Filter out empty strings if marker was at start
    pages = [p for p in pages if p.strip()]

    # Adjust index (page_num 1 -> index 0)
    if 1 <= page_num <= len(pages):
        return pages[page_num - 1].strip()
    else:
        return f"Página {page_num} não encontrada no texto (Total de páginas identificadas: {len(pages)})."
