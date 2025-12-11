from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.models import User, Player, Team, Pool
from app.schemas.admin import (
    PlayerCreate, PlayerUpdate, PlayerResponse,
    TeamCreate, TeamResponse,
    PoolCreate, PoolResponse,
    AccountCreate, AccountResponse,
    RoleUpdate
)
from app.api.deps import get_current_user
from app.core.security import get_password_hash
import secrets
import string

router = APIRouter()

def check_admin(current_user: User):
    if current_user.role != "ADMINISTRATEUR":
        raise HTTPException(status_code=403, detail="Accès réservé aux administrateurs")

# --- Players ---

@router.post("/players", response_model=PlayerResponse)
def create_player(
    player: PlayerCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    check_admin(current_user)
    
    # Vérifier unicité email et licence
    if db.query(Player).filter(Player.email == player.email).first():
        raise HTTPException(400, "Email déjà utilisé")
    if db.query(Player).filter(Player.license_number == player.license_number).first():
        raise HTTPException(400, "Numéro de licence déjà utilisé")
        
    db_player = Player(**player.model_dump())
    db.add(db_player)
    db.commit()
    db.refresh(db_player)
    return db_player

@router.get("/players", response_model=List[PlayerResponse])
def get_players(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    check_admin(current_user)
    return db.query(Player).all()

@router.put("/players/{player_id}", response_model=PlayerResponse)
def update_player(
    player_id: int,
    player_update: PlayerUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    check_admin(current_user)
    db_player = db.query(Player).filter(Player.id == player_id).first()
    if not db_player:
        raise HTTPException(404, "Joueur non trouvé")
        
    update_data = player_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_player, key, value)
        
    db.commit()
    db.refresh(db_player)
    return db_player

@router.delete("/players/{player_id}")
def delete_player(
    player_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    check_admin(current_user)
    db_player = db.query(Player).filter(Player.id == player_id).first()
    if not db_player:
        raise HTTPException(404, "Joueur non trouvé")
        
    if db_player.team_id:
        raise HTTPException(400, "Impossible de supprimer un joueur appartenant à une équipe")
        
    db.delete(db_player)
    db.commit()
    return {"message": "Joueur supprimé"}

@router.put("/players/{player_id}/role")
def change_player_role(
    player_id: int,
    role_update: RoleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    check_admin(current_user)
    player = db.query(Player).filter(Player.id == player_id).first()
    if not player:
        raise HTTPException(404, "Joueur non trouvé")
    
    if not player.user:
        raise HTTPException(400, "Ce joueur n'a pas de compte utilisateur")
        
    if role_update.role not in ["JOUEUR", "ADMINISTRATEUR"]:
        raise HTTPException(400, "Rôle invalide")
        
    player.user.role = role_update.role
    db.commit()
    return {"message": f"Rôle mis à jour : {role_update.role}"}

# --- Teams ---

@router.post("/teams", response_model=TeamResponse)
def create_team(
    team: TeamCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    check_admin(current_user)
    
    p1 = db.query(Player).filter(Player.id == team.player1_id).first()
    p2 = db.query(Player).filter(Player.id == team.player2_id).first()
    
    if not p1 or not p2:
        raise HTTPException(404, "Un ou plusieurs joueurs non trouvés")
        
    if p1.id == p2.id:
        raise HTTPException(400, "Impossible de sélectionner deux fois le même joueur")
        
    if p1.company != p2.company:
        raise HTTPException(400, "Les deux joueurs doivent appartenir à la même entreprise")

    if p1.team_id or p2.team_id:
        raise HTTPException(400, "Un joueur ne peut appartenir qu'à une seule équipe")
        
    # Vérifier si une équipe avec ce nom existe déjà
    existing_team = db.query(Team).filter(Team.name == team.name).first()
    if existing_team:
        raise HTTPException(400, "Une équipe avec ce nom existe déjà")

    db_team = Team(name=team.name)
    db.add(db_team)
    db.commit()
    
    p1.team_id = db_team.id
    p2.team_id = db_team.id
    db.commit()
    db.refresh(db_team)
    return db_team

@router.get("/teams", response_model=List[TeamResponse])
def get_teams(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    check_admin(current_user)
    return db.query(Team).all()

@router.delete("/teams/{team_id}")
def delete_team(
    team_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    check_admin(current_user)
    db_team = db.query(Team).filter(Team.id == team_id).first()
    if not db_team:
        raise HTTPException(404, "Équipe non trouvée")
        
    if db_team.matches_as_team1 or db_team.matches_as_team2:
        raise HTTPException(400, " Impossible de supprimer une équipe qui a déjà joué des matchs")
    
    # Libérer les joueurs
    for player in db_team.players:
        player.team_id = None
        
    db.delete(db_team)
    db.commit()
    return {"message": "Équipe supprimée"}

# --- Pools ---

@router.post("/pools", response_model=PoolResponse)
def create_pool(
    pool: PoolCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    check_admin(current_user)
    
    if db.query(Pool).filter(Pool.name == pool.name).first():
        raise HTTPException(400, "Nom de poule déjà utilisé")
        
    teams = db.query(Team).filter(Team.id.in_(pool.team_ids)).all()
    if len(teams) != 6:
        raise HTTPException(400, "6 équipes valides requises")
        
    for team in teams:
        if team.pool_id:
            raise HTTPException(400, f"L'équipe {team.name} est déjà dans une poule")
            
    db_pool = Pool(name=pool.name)
    db.add(db_pool)
    db.commit()
    
    for team in teams:
        team.pool_id = db_pool.id
        
    db.commit()
    db.refresh(db_pool)
    return db_pool

@router.get("/pools", response_model=List[PoolResponse])
def get_pools(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    check_admin(current_user)
    return db.query(Pool).all()

# --- Accounts ---

def generate_secure_password(length=12):
    alphabet = string.ascii_letters + string.digits + string.punctuation
    while True:
        password = ''.join(secrets.choice(alphabet) for i in range(length))
        if (any(c.islower() for c in password)
                and any(c.isupper() for c in password)
                and any(c.isdigit() for c in password)
                and any(c in string.punctuation for c in password)):
            return password

@router.post("/accounts", response_model=AccountResponse)
def create_player_account(
    account: AccountCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    check_admin(current_user)
    
    player = db.query(Player).filter(Player.id == account.player_id).first()
    if not player:
        raise HTTPException(404, "Joueur non trouvé")
        
    if player.user:
        raise HTTPException(400, "Ce joueur a déjà un compte")
        
    temp_password = generate_secure_password()
    
    user = User(
        email=player.email,
        password_hash=get_password_hash(temp_password),
        role="JOUEUR",
        firstname=player.firstname,
        lastname=player.lastname,
        license_number=player.license_number,
        must_change_password=True,
        player_id=player.id
    )
    
    db.add(user)
    db.commit()
    
    return AccountResponse(email=user.email, temp_password=temp_password)
