# ============================================
# FICHIER : backend/app/api/auth.py
# ============================================

from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.models import User, LoginAttempt
from app.schemas.auth import LoginRequest, TokenResponse, UserResponse, ChangePasswordRequest, UserUpdate
from app.core.security import verify_password, get_password_hash, create_access_token
from app.api.deps import get_current_user
import shutil
import os
import uuid

router = APIRouter()

MAX_ATTEMPTS = 5
LOCKOUT_MINUTES = 30

def check_and_update_attempts(db: Session, email: str, success: bool = False):
    """Vérifie et met à jour les tentatives de connexion"""
    attempt = db.query(LoginAttempt).filter(LoginAttempt.email == email).first()
    
    if not attempt:
        attempt = LoginAttempt(email=email, attempts_count=0)
        db.add(attempt)
    
    now = datetime.now(timezone.utc)
    
    # Vérifier si le compte est bloqué
    if attempt.locked_until:
        # S'assurer que locked_until est aware (SQLite peut renvoyer du naïf)
        if attempt.locked_until.tzinfo is None:
            attempt.locked_until = attempt.locked_until.replace(tzinfo=timezone.utc)
            
        if attempt.locked_until > now:
            minutes_remaining = int((attempt.locked_until - now).total_seconds() / 60)
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "message": "Compte bloqué",
                    "locked_until": attempt.locked_until.isoformat(),
                    "minutes_remaining": minutes_remaining
                }
            )
    
    if success:
        # Réinitialiser les tentatives en cas de succès
        attempt.attempts_count = 0
        attempt.locked_until = None
    else:
        # Incrémenter les tentatives
        attempt.attempts_count += 1
        attempt.last_attempt = now
        
        if attempt.attempts_count >= MAX_ATTEMPTS:
            attempt.locked_until = now + timedelta(minutes=LOCKOUT_MINUTES)
            db.commit()
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "message": "Compte bloqué après 5 tentatives échouées",
                    "locked_until": attempt.locked_until.isoformat(),
                    "minutes_remaining": LOCKOUT_MINUTES
                }
            )
    
    db.commit()
    
    if not success:
        attempts_remaining = MAX_ATTEMPTS - attempt.attempts_count
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "message": "Email ou mot de passe incorrect",
                "attempts_remaining": attempts_remaining
            }
        )

@router.post("/login", response_model=TokenResponse)
def login(credentials: LoginRequest, db: Session = Depends(get_db)):
    """Authentifie un utilisateur et retourne un token JWT"""
    
    # Récupérer l'utilisateur
    user = db.query(User).filter(User.email == credentials.email).first()
    
    # Vérifier les credentials
    if not user or not verify_password(credentials.password, user.password_hash):
        check_and_update_attempts(db, credentials.email, success=False)
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Compte désactivé"
        )
    
    # Réinitialiser les tentatives en cas de succès
    check_and_update_attempts(db, credentials.email, success=True)
    
    # Créer le token
    access_token = create_access_token(
        data={
            "sub": str(user.id),
            "email": user.email,
            "role": user.role
        }
    )
    
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse.model_validate(user)
    )

@router.post("/change-password")
def change_password(
    request: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Change le mot de passe de l'utilisateur connecté"""
    
    # Vérifier le mot de passe actuel
    if not verify_password(request.current_password, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Mot de passe actuel incorrect"
        )
    
    # Vérifier que le nouveau mot de passe est différent
    if verify_password(request.new_password, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Le nouveau mot de passe doit être différent de l'ancien"
        )
    
    # Mettre à jour le mot de passe
    current_user.password_hash = get_password_hash(request.new_password)
    current_user.must_change_password = False
    db.commit()
    
    return {"message": "Mot de passe modifié avec succès"}

@router.post("/logout")
def logout(current_user: User = Depends(get_current_user)):
    """Déconnecte l'utilisateur (côté client, suppression du token)"""
    return {"message": "Déconnexion réussie"}

@router.get("/me", response_model=UserResponse)
def read_users_me(current_user: User = Depends(get_current_user)):
    """Retourne les informations de l'utilisateur connecté"""
    return current_user

@router.put("/me", response_model=UserResponse)
def update_user_me(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Met à jour les informations de l'utilisateur connecté"""
    
    # Vérifier l'unicité de l'email si changé
    if user_update.email != current_user.email:
        existing_user = db.query(User).filter(User.email == user_update.email).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cet email est déjà utilisé"
            )
    
    current_user.firstname = user_update.firstname
    current_user.lastname = user_update.lastname
    current_user.email = user_update.email
    current_user.birthdate = user_update.birthdate
    
    db.commit()
    db.refresh(current_user)
    return current_user

@router.post("/me/avatar", response_model=UserResponse)
async def upload_avatar(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upload une photo de profil"""
    
    # Validation du fichier
    if not file.content_type in ["image/jpeg", "image/png", "image/jpg"]:
        raise HTTPException(400, detail="Format de fichier non supporté (JPG/PNG uniquement)")
    
    # Vérifier la taille (approximatif car on lit le stream)
    content = await file.read()
    if len(content) > 2 * 1024 * 1024: # 2MB
        raise HTTPException(400, detail="La taille du fichier ne doit pas dépasser 2MB")
        
    await file.seek(0) # Rembobiner
    
    # Créer le dossier si nécessaire
    upload_dir = "static/uploads"
    os.makedirs(upload_dir, exist_ok=True)
    
    # Générer un nom unique
    file_ext = file.filename.split(".")[-1]
    filename = f"{current_user.id}_{uuid.uuid4()}.{file_ext}"
    file_path = os.path.join(upload_dir, filename)
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    # Supprimer l'ancienne photo si elle existe
    if current_user.profile_picture:
        # On suppose que profile_picture est stocké comme "/static/uploads/filename"
        # On doit enlever le premier "/" pour avoir le chemin relatif
        old_path = current_user.profile_picture.lstrip("/")
        if os.path.exists(old_path):
            os.remove(old_path)
            
    # Mettre à jour l'URL
    current_user.profile_picture = f"/static/uploads/{filename}"
    db.commit()
    db.refresh(current_user)
    
    return current_user

@router.delete("/me/avatar", response_model=UserResponse)
def delete_avatar(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Supprime la photo de profil"""
    if current_user.profile_picture:
        old_path = current_user.profile_picture.lstrip("/")
        if os.path.exists(old_path):
            os.remove(old_path)
        
        current_user.profile_picture = None
        db.commit()
        db.refresh(current_user)
        
    return current_user