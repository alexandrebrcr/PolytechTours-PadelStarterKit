# ============================================
# FICHIER : backend/app/api/matches.py
# ============================================

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
from datetime import date, datetime, timedelta, timezone

from app.database import get_db
from app.models.models import Match, Event, Team, Player, User, MatchStatus
from app.schemas.matches import MatchCreate, MatchUpdate, MatchResponse, TeamMatchInfo, PlayerMatchInfo
from app.api.deps import get_current_user, get_current_admin

router = APIRouter()

def map_match_to_response(match: Match) -> MatchResponse:
    return MatchResponse(
        id=match.id,
        date=match.event.date,
        time=match.event.start_time,
        court_number=match.court_number,
        status=match.status,
        score_team1=match.score_team1,
        score_team2=match.score_team2,
        team1=TeamMatchInfo.model_validate(match.team1),
        team2=TeamMatchInfo.model_validate(match.team2)
    )

@router.get("/", response_model=List[MatchResponse])
def get_matches(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    all_matches: bool = False,
    company: Optional[str] = None,
    pool_id: Optional[int] = None,
    status_filter: Optional[MatchStatus] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Récupère la liste des matchs avec filtres.
    Par défaut : 30 prochains jours.
    Pour les joueurs : uniquement leurs matchs sauf si all_matches=True.
    """
    query = db.query(Match).join(Event).join(Team, Match.team1_id == Team.id).options(
        joinedload(Match.event),
        joinedload(Match.team1).joinedload(Team.players),
        joinedload(Match.team2).joinedload(Team.players)
    )

    # Filtre date (défaut : aujourd'hui -> +30 jours)
    if not start_date:
        start_date = date.today()
    if not end_date:
        end_date = start_date + timedelta(days=30)
    
    query = query.filter(Event.date >= start_date, Event.date <= end_date)

    # Filtres Admin / Options
    if company:
        # On cherche si l'une des équipes est de cette entreprise
        # Note: Cela suppose que Team a un champ company.
        # Il faut faire une jointure ou un OR.
        # Déjà joint sur Team1, il faudrait aussi vérifier Team2.
        # Simplification : on filtre sur les équipes chargées
        # query = query.join(Team, Match.team2_id == Team.id, aliased=True) # Compliqué avec SQLAlchemy simple
        # On va faire plus simple : filter sur team1.company OR team2.company
        # Mais on a déjà join Team pour team1.
        pass # TODO: Implémenter filtre complexe si nécessaire, pour l'instant on filtre en Python ou on améliore la query

    if pool_id:
        query = query.filter((Match.team1.has(pool_id=pool_id)) | (Match.team2.has(pool_id=pool_id)))

    if status_filter:
        query = query.filter(Match.status == status_filter)

    # Filtre Joueur (si pas admin et pas all_matches)
    if current_user.role != "ADMINISTRATEUR" and not all_matches:
        if not current_user.player:
             # Si l'utilisateur n'est pas lié à un joueur, il ne voit rien par défaut ?
             # Ou on lui montre tout ? Disons qu'il voit tout s'il n'est pas joueur.
             pass
        else:
            player_id = current_user.player.id
            # Matchs où le joueur est dans team1 ou team2
            # C'est complexe à exprimer en pure query sans alias multiples.
            # On peut filtrer sur les IDs d'équipe du joueur.
            if current_user.player.team_id:
                team_id = current_user.player.team_id
                query = query.filter((Match.team1_id == team_id) | (Match.team2_id == team_id))
            else:
                # Joueur sans équipe -> pas de matchs
                return []

    matches = query.order_by(Event.date, Event.start_time).all()
    
    # Filtrage Python pour 'company' si nécessaire car la query est complexe
    if company:
        company_lower = company.lower()
        # On filtre sur le nom de l'équipe OU l'entreprise des joueurs
        matches = [
            m for m in matches 
            if company_lower in m.team1.name.lower() 
            or company_lower in m.team2.name.lower()
            or any(company_lower in p.company.lower() for p in m.team1.players)
            or any(company_lower in p.company.lower() for p in m.team2.players)
        ]

    return [map_match_to_response(m) for m in matches]

@router.post("/", response_model=MatchResponse)
def create_match(
    match_in: MatchCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    """Crée un nouveau match (Admin uniquement)"""
    
    # Vérifier disponibilité piste/créneau
    # On cherche s'il existe un match sur le même créneau et la même piste
    # Créneau = Event.date + Event.start_time
    # On suppose durée standard ou on vérifie juste le début pour l'instant
    
    existing_match = db.query(Match).join(Event).filter(
        Event.date == match_in.date,
        Event.start_time == match_in.time,
        Match.court_number == match_in.court_number,
        Match.status != MatchStatus.ANNULE
    ).first()
    
    if existing_match:
        raise HTTPException(
            status_code=400,
            detail="Un match est déjà prévu sur cette piste à ce créneau"
        )

    # Créer l'événement
    # TODO: Gérer la durée (end_time). Pour l'instant on met null ou +1h30
    event = Event(
        date=match_in.date,
        start_time=match_in.time
    )
    db.add(event)
    db.commit()
    db.refresh(event)
    
    # Créer le match
    match = Match(
        event_id=event.id,
        court_number=match_in.court_number,
        team1_id=match_in.team1_id,
        team2_id=match_in.team2_id,
        status=MatchStatus.A_VENIR
    )
    
    db.add(match)
    db.commit()
    db.refresh(match)
    
    return map_match_to_response(match)

@router.put("/{match_id}", response_model=MatchResponse)
def update_match(
    match_id: int,
    match_in: MatchUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    """Modifie un match (Admin uniquement)"""
    
    match = db.query(Match).filter(Match.id == match_id).first()
    if not match:
        raise HTTPException(404, "Match non trouvé")
        
    # Modification date/heure/piste
    if match_in.date or match_in.time or match_in.court_number:
        if match.status != MatchStatus.A_VENIR:
            raise HTTPException(400, "Impossible de modifier la date/piste d'un match terminé ou annulé")
            
        # Vérifier disponibilité si changement
        new_date = match_in.date or match.event.date
        new_time = match_in.time or match.event.start_time
        new_court = match_in.court_number or match.court_number
        
        if (new_date != match.event.date or 
            new_time != match.event.start_time or 
            new_court != match.court_number):
            
            conflict = db.query(Match).join(Event).filter(
                Event.date == new_date,
                Event.start_time == new_time,
                Match.court_number == new_court,
                Match.id != match_id,
                Match.status != MatchStatus.ANNULE
            ).first()
            
            if conflict:
                raise HTTPException(400, "Créneau indisponible")
                
        if match_in.date: match.event.date = match_in.date
        if match_in.time: match.event.start_time = match_in.time
        if match_in.court_number: match.court_number = match_in.court_number

    # Modification statut
    if match_in.status:
        match.status = match_in.status
        
        # Si le statut passe à TERMINE, on vérifie que les scores sont présents
        if match.status == MatchStatus.TERMINE:
            # On vérifie soit dans match_in (nouveau score), soit dans match (score existant)
            s1 = match_in.score_team1 if match_in.score_team1 is not None else match.score_team1
            s2 = match_in.score_team2 if match_in.score_team2 is not None else match.score_team2
            
            if not s1 or not s2:
                raise HTTPException(400, "Impossible de terminer un match sans scores")
        
        # Si le statut n'est pas TERMINE, on efface les scores
        if match.status != MatchStatus.TERMINE:
            match.score_team1 = None
            match.score_team2 = None
            # On ignore les scores envoyés dans match_in si le statut n'est pas TERMINE
            match_in.score_team1 = None
            match_in.score_team2 = None

    # Scores (seulement si TERMINE)
    if match.status == MatchStatus.TERMINE:
        if match_in.score_team1 is not None:
            match.score_team1 = match_in.score_team1
        if match_in.score_team2 is not None:
            match.score_team2 = match_in.score_team2
        
    db.commit()
    db.refresh(match)
    return map_match_to_response(match)

@router.delete("/{match_id}")
def delete_match(
    match_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    """Supprime un match (Admin uniquement)"""
    
    match = db.query(Match).filter(Match.id == match_id).first()
    if not match:
        raise HTTPException(404, "Match non trouvé")
        
    if match.status != MatchStatus.A_VENIR:
        raise HTTPException(400, "Seuls les matchs à venir peuvent être supprimés")
        
    # Supprimer l'événement associé aussi ?
    # Oui car cascade="all, delete-orphan" est sur Event.matches, pas l'inverse.
    # Si on supprime le match, l'event reste orphelin si on ne fait pas gaffe.
    # Mais ici Match -> Event (FK).
    # Si on supprime le Match, l'Event reste.
    # On devrait supprimer l'Event si c'est du 1-1.
    event_id = match.event_id
    db.delete(match)
    
    # Vérifier s'il reste des matchs pour cet event
    # On exclut le match qu'on vient de supprimer (au cas où le flush n'est pas fait)
    other_matches = db.query(Match).filter(Match.event_id == event_id, Match.id != match_id).count()
    
    if other_matches == 0:
        event = db.query(Event).filter(Event.id == event_id).first()
        if event:
            db.delete(event)
            
    db.commit()
    return {"message": "Match supprimé"}
