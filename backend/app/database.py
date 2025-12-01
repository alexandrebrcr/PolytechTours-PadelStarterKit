from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings

engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False}  # Nécessaire pour SQLite
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    """Générateur de session de base de données"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """Initialise la base de données avec un admin par défaut"""
    from app.models.models import User, Base
    from app.core.security import get_password_hash
    
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        # Vérifier si un admin existe déjà
        admin = db.query(User).filter(User.email == "admin@padel.com").first()
        if not admin:
            admin = User(
                email="admin@padel.com",
                password_hash=get_password_hash("Test@2025_2026"),
                role="ADMINISTRATEUR",
                is_active=True,
                firstname="Admin",
                lastname="System"
            )
            db.add(admin)
            db.commit()
            # Admin created
        else:
            pass
    finally:
        db.close()
