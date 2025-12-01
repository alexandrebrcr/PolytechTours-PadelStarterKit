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

def init_db_test():
    """Initialise la base de données avec des données de test"""
    init_db()
    
    from app.models.models import Player, Team
    
    db = SessionLocal()
    try:
        # Create test players for Matches test
        players_data = [
            {"email": "pierre@test.com", "firstname": "Pierre", "lastname": "Test", "company": "CompA", "license_number": "L000001"},
            {"email": "jean@test.com", "firstname": "Jean", "lastname": "Test", "company": "CompA", "license_number": "L000002"},
            {"email": "alice@test.com", "firstname": "Alice", "lastname": "Test", "company": "ResCompA", "license_number": "L000003"},
            {"email": "bob@test.com", "firstname": "Bob", "lastname": "Test", "company": "ResCompA", "license_number": "L000004"},
            {"email": "charlie@test.com", "firstname": "Charlie", "lastname": "Test", "company": "Other", "license_number": "L000005"},
        ]

        for p in players_data:
            player = db.query(Player).filter(Player.email == p["email"]).first()
            if not player:
                player = Player(
                    email=p["email"],
                    firstname=p["firstname"],
                    lastname=p["lastname"],
                    company=p["company"],
                    license_number=p["license_number"]
                )
                db.add(player)
        
        db.commit()

        # Create Teams
        # CompA Team
        p1 = db.query(Player).filter(Player.email == "pierre@test.com").first()
        p2 = db.query(Player).filter(Player.email == "jean@test.com").first()
        
        if p1 and p2:
            team_a = db.query(Team).filter(Team.company == "CompA").first()
            if not team_a:
                team_a = Team(company="CompA")
                db.add(team_a)
                db.commit()
                
                p1.team_id = team_a.id
                p2.team_id = team_a.id
                db.commit()

        # ResCompA Team
        p3 = db.query(Player).filter(Player.email == "alice@test.com").first()
        p4 = db.query(Player).filter(Player.email == "bob@test.com").first()
        
        if p3 and p4:
            team_b = db.query(Team).filter(Team.company == "ResCompA").first()
            if not team_b:
                team_b = Team(company="ResCompA")
                db.add(team_b)
                db.commit()
                
                p3.team_id = team_b.id
                p4.team_id = team_b.id
                db.commit()

    finally:
        db.close()
