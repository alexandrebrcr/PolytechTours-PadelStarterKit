
from app.database import SessionLocal
from app.models.models import LoginAttempt

db = SessionLocal()
try:
    db.query(LoginAttempt).filter(LoginAttempt.email == "admin@padel.com").delete()
    db.commit()
    print("Unlocked admin@padel.com")
except Exception as e:
    print(f"Error: {e}")
finally:
    db.close()
