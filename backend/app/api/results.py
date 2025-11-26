from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session, joinedload
from typing import List
from pydantic import BaseModel

from app.database import get_db
from app.models.models import Match, MatchStatus, Team
from app.api.deps import get_current_user

router = APIRouter()

class RankingEntry(BaseModel):
    position: int
    company: str
    matches_played: int
    wins: int
    losses: int
    points: int
    sets_won: int
    sets_lost: int

@router.get("/ranking", response_model=List[RankingEntry])
def get_ranking(db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    """
    Calcule et retourne le classement général des entreprises.
    """
    # Récupérer tous les matchs terminés
    matches = db.query(Match).options(
        joinedload(Match.team1),
        joinedload(Match.team2)
    ).filter(Match.status == MatchStatus.TERMINE).all()
    
    # Récupérer toutes les équipes pour initialiser le classement (même celles sans matchs)
    teams = db.query(Team).all()
    
    stats = {} # team_id -> {company, played, wins, losses, points, sets_won, sets_lost}
    
    for team in teams:
        stats[team.id] = {
            "company": team.company,
            "matches_played": 0,
            "wins": 0,
            "losses": 0,
            "points": 0,
            "sets_won": 0,
            "sets_lost": 0
        }
        
    for match in matches:
        if not match.score_team1:
            continue
            
        # Parser le score
        # On suppose que score_team1 est le score vu par l'équipe 1
        # Format "6-4, 6-3"
        try:
            sets = match.score_team1.split(", ")
            t1_sets = 0
            t2_sets = 0
            
            for s in sets:
                g1, g2 = map(int, s.split("-"))
                if g1 > g2:
                    t1_sets += 1
                else:
                    t2_sets += 1
            
            # Déterminer le vainqueur du match
            winner_id = None
            loser_id = None
            
            if t1_sets > t2_sets:
                winner_id = match.team1_id
                loser_id = match.team2_id
            else:
                winner_id = match.team2_id
                loser_id = match.team1_id
                
            # Mise à jour stats Team 1
            if match.team1_id in stats:
                stats[match.team1_id]["matches_played"] += 1
                stats[match.team1_id]["sets_won"] += t1_sets
                stats[match.team1_id]["sets_lost"] += t2_sets
                if match.team1_id == winner_id:
                    stats[match.team1_id]["wins"] += 1
                    stats[match.team1_id]["points"] += 3
                else:
                    stats[match.team1_id]["losses"] += 1
            
            # Mise à jour stats Team 2
            if match.team2_id in stats:
                stats[match.team2_id]["matches_played"] += 1
                stats[match.team2_id]["sets_won"] += t2_sets
                stats[match.team2_id]["sets_lost"] += t1_sets
                if match.team2_id == winner_id:
                    stats[match.team2_id]["wins"] += 1
                    stats[match.team2_id]["points"] += 3
                else:
                    stats[match.team2_id]["losses"] += 1
                    
        except ValueError:
            continue # Ignorer les scores mal formés
            
    # Convertir en liste et trier
    ranking = []
    for team_id, data in stats.items():
        ranking.append(data)
        
    # Tri : Points DESC, Victoires DESC, Diff Sets DESC, Nom ASC
    ranking.sort(key=lambda x: (
        -x["points"],
        -x["wins"],
        -(x["sets_won"] - x["sets_lost"]),
        x["company"]
    ))
    
    # Assigner les positions
    result = []
    for i, data in enumerate(ranking):
        result.append(RankingEntry(
            position=i + 1,
            company=data["company"],
            matches_played=data["matches_played"],
            wins=data["wins"],
            losses=data["losses"],
            points=data["points"],
            sets_won=data["sets_won"],
            sets_lost=data["sets_lost"]
        ))
        
    return result
