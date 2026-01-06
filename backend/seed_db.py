from backend.database import engine, SessionLocal, Base
from backend.models import Processo, EvidenciaMapeada, EvidenciaCatalogada, Usuario
from backend.etl_service import create_processo, import_mapeamento, import_catalogador
from backend.auth import get_password_hash
import os

def seed():
    # Create tables
    print("Creating tables...")
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()

    # 1. Create Admin User
    admin = db.query(Usuario).filter(Usuario.username == "admin").first()
    if not admin:
        print("Creating admin user...")
        admin_user = Usuario(
            username="admin",
            hashed_password=get_password_hash("admin"),
            is_active=True,
            is_admin=True,
            can_create_users=True
        )
        db.add(admin_user)
        db.commit()
    else:
        print("Admin user already exists.")

    # Check if process exists
    existing = db.query(Processo).filter(Processo.numero_processo == "0000000-00.0000.0.00.0000").first()
    if existing:
        print("Process already exists, skipping seed.")
        db.close()
        return

    print("Creating Processo...")
    # Dummy process data
    proc = create_processo(
        db, 
        numero="0000000-00.0000.0.00.0000", 
        nome="Processo Exemplo - Importação", 
        pdf_path="dummy.pdf"
    )

    # Paths to excel files
    # Assuming script is run from project root
    base_dir = os.getcwd()
    mapeamento_path = os.path.join(base_dir, "evidencias_extraidas_mapeamento.xlsx")
    catalogador_path = os.path.join(base_dir, "evidencias_extraidas_catalogador.xlsx")

    if os.path.exists(mapeamento_path):
        print(f"Importing Mapeamento from {mapeamento_path}...")
        import_mapeamento(db, proc.id, mapeamento_path)
    else:
        print("Mapeamento file not found.")

    if os.path.exists(catalogador_path):
        print(f"Importing Catalogador from {catalogador_path}...")
        import_catalogador(db, proc.id, catalogador_path)
    else:
        print("Catalogador file not found.")
    
    # Verification
    count_map = db.query(EvidenciaMapeada).filter(EvidenciaMapeada.processo_id == proc.id).count()
    count_cat = db.query(EvidenciaCatalogada).filter(EvidenciaCatalogada.processo_id == proc.id).count()
    
    print(f"Done. Imported {count_map} mapped evidences and {count_cat} cataloged evidences.")
    db.close()

if __name__ == "__main__":
    seed()
