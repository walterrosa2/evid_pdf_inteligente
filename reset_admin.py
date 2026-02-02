from backend.database import SessionLocal
from backend.models import Usuario
from backend.auth import get_password_hash
import sys

def reset_admin_password():
    db = SessionLocal()
    try:
        # Busca o usuário admin
        admin = db.query(Usuario).filter(Usuario.username == "admin").first()
        
        nova_senha = "admin"
        hashed_password = get_password_hash(nova_senha)
        
        if admin:
            print(f"Usuário 'admin' encontrado. Resetando a senha...")
            admin.hashed_password = hashed_password
            admin.is_active = True
            admin.is_admin = True
            admin.can_create_users = True
        else:
            print(f"Usuário 'admin' não encontrado. Criando novo usuário...")
            admin = Usuario(
                username="admin",
                hashed_password=hashed_password,
                is_active=True,
                is_admin=True,
                can_create_users=True
            )
            db.add(admin)
        
        db.commit()
        print(f"✅ Sucesso! O usuário 'admin' agora tem a senha: {nova_senha}")
        
    except Exception as e:
        print(f"❌ Erro ao resetar senha: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    reset_admin_password()
