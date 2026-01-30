from sqlalchemy import create_engine, text
from database import engine

def migrate():
    with engine.connect() as conn:
        print("Migrating Database...")
        
        # Check if columns exist in 'processos'
        # SQLite doesn't have 'IF NOT EXISTS' for columns easily in one statement across versions,
        # but we can try catch or check pragma.
        # Simplest: Try ADD COLUMN, ignore error if duplicate.
        
        try:
            conn.execute(text("ALTER TABLE processos ADD COLUMN caminho_texto VARCHAR"))
            print("Added column 'caminho_texto'")
        except Exception as e:
            print(f"Skipped 'caminho_texto': {e}")

        try:
            conn.execute(text("ALTER TABLE processos ADD COLUMN marcador_pagina VARCHAR"))
            print("Added column 'marcador_pagina'")
        except Exception as e:
            print(f"Skipped 'marcador_pagina': {e}")
            
        # Create new tables if they don't exist
        # 'create_all' in main.py usually handles this, but we can rely on main startup.
        # This script focuses on ALTER.
        
        conn.commit()
        print("Migration compelete.")

if __name__ == "__main__":
    migrate()
