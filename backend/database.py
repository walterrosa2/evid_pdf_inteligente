import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# No Railway, usaremos volumes para persistência. 
# DATA_PATH pode apontar para o diretório montado.
DATA_PATH = os.getenv("DATA_PATH", "./")
DB_NAME = "leitor_inteligente_v2.db"
SQLALCHEMY_DATABASE_URL = f"sqlite:///{os.path.join(DATA_PATH, DB_NAME)}"

# Create engine
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
