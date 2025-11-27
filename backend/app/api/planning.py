from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
from datetime import date, timedelta

from app.database import get_db
from app.models.models import Event, Match, MatchStatus, Team
from app.schemas.planning import EventCreate, EventResponse
from app.api.deps import get_current_user, get_current_admin
from app.models.models import User

router = APIRouter()

@router.get("/", response_model=List[EventResponse])
def get_events(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Récupère le planning des événements.
    """
    if not start_date:
        start_date = date.today().replace(day=1) # Début du mois courant
    if not end_date:
        # Fin du mois suivant par défaut pour avoir une bonne vue
        next_month = start_date.replace(day=28) + timedelta(days=4)
        end_date = (next_month.replace(day=1) + timedelta(days=32)).replace(day=1) - timedelta(days=1)

    query = db.query(Event).options(
        joinedload(Event.matches).joinedload(Match.team1).joinedload(Team.players),
        joinedload(Event.matches).joinedload(Match.team2).joinedload(Team.players)
    ).filter(
        Event.date >= start_date,
        Event.date <= end_date
    ).order_by(Event.date, Event.start_time)

    events = query.all()
    
    # Filtrage pour les joueurs : voir seulement leurs événements ?
    # Requirement 2.3.5: "Voir uniquement les événements où ils sont impliqués (filtre automatique)"
    # "Option pour voir tous les événements (décocher le filtre)"
    # Ce filtrage se fera plutôt côté frontend ou via un paramètre de query string.
    # Ici on renvoie tout, le front filtrera ou on ajoute un paramètre ?
    # Le requirement dit "Option pour voir tous les événements", donc l'API doit pouvoir tout renvoyer.
    # On va tout renvoyer par défaut et laisser le front filtrer, sauf si c'est trop lourd.
    # Vu la taille probable, tout renvoyer est OK.
    
    return events

@router.post("/", response_model=EventResponse)
def create_event(
    event_in: EventCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    """Crée un événement avec ses matchs (Admin uniquement)"""
    
    # 1. Vérifier conflits de pistes
    requested_courts = [m.court_number for m in event_in.matches]
    
    conflicts = db.query(Match).join(Event).filter(
        Event.date == event_in.date,
        Event.start_time == event_in.start_time,
        Match.court_number.in_(requested_courts),
        Match.status != MatchStatus.ANNULE
    ).first()
    
    if conflicts:
        raise HTTPException(
            status_code=400,
            detail=f"La piste {conflicts.court_number} est déjà occupée à ce créneau"
        )

    # 2. Créer l'événement
    event = Event(
        date=event_in.date,
        start_time=event_in.start_time
    )
    db.add(event)
    db.commit()
    db.refresh(event)
    
    # 3. Créer les matchs
    for match_in in event_in.matches:
        match = Match(
            event_id=event.id,
            court_number=match_in.court_number,
            team1_id=match_in.team1_id,
            team2_id=match_in.team2_id,
            status=MatchStatus.A_VENIR
        )
        db.add(match)
    
    db.commit()
    db.refresh(event)
    
    # Recharger avec les relations pour la réponse
    # (Astuce: on peut refaire une query ou laisser SQLAlchemy lazy loader, 
    # mais joinedload est mieux pour la perf si on renvoie tout)
    return db.query(Event).options(
        joinedload(Event.matches).joinedload(Match.team1),
        joinedload(Event.matches).joinedload(Match.team2)
    ).filter(Event.id == event.id).first()

@router.delete("/{event_id}")
def delete_event(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    """Supprime un événement (Admin uniquement)"""
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(404, "Événement non trouvé")
        
    # Vérifier si l'événement a déjà eu lieu ou contient des matchs terminés
    # Règle métier : Un événement ne peut être supprimé que s'il n'a pas encore eu lieu (statut A_VENIR)
    # On vérifie si un match n'est PAS A_VENIR
    for match in event.matches:
        if match.status != MatchStatus.A_VENIR:
            raise HTTPException(400, "Impossible de supprimer un événement contenant des matchs terminés ou annulés")
            
    db.delete(event)
    db.commit()
    return {"message": "Événement supprimé"}
