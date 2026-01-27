# ============================================
# FICHIER : backend/app/schemas/planning.py
# ============================================

from pydantic import BaseModel, Field, field_validator, ValidationInfo, ConfigDict
from typing import List, Optional
from datetime import date, time
from app.schemas.matches import MatchStatus, TeamMatchInfo

class MatchCreationInEvent(BaseModel):
    court_number: int = Field(..., ge=1, le=10)
    team1_id: int
    team2_id: int

    @field_validator('team2_id')
    @classmethod
    def validate_teams(cls, v, info: ValidationInfo):
        if 'team1_id' in info.data and v == info.data['team1_id']:
            raise ValueError("Une équipe ne peut pas jouer contre elle-même")
        return v

class EventCreate(BaseModel):
    date: date
    start_time: time
    matches: List[MatchCreationInEvent]

    @field_validator('date')
    @classmethod
    def validate_date(cls, v):
        from datetime import date
        if v < date.today():
            raise ValueError("La date ne peut pas être dans le passé")
        return v
    
    @field_validator('matches')
    @classmethod
    def validate_matches(cls, v):
        if not (1 <= len(v) <= 3):
            raise ValueError("Un événement doit contenir entre 1 et 3 matchs")
        
        courts = [m.court_number for m in v]
        if len(courts) != len(set(courts)):
            raise ValueError("Deux matchs ne peuvent pas utiliser la même piste")
            
        teams = []
        for m in v:
            teams.extend([m.team1_id, m.team2_id])
        if len(teams) != len(set(teams)):
            raise ValueError("Une équipe ne peut jouer qu'un seul match par événement")
            
        return v

class MatchInEventResponse(BaseModel):
    id: int
    court_number: int
    status: MatchStatus
    team1: TeamMatchInfo
    team2: TeamMatchInfo
    score_team1: Optional[str] = None
    score_team2: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)

class EventResponse(BaseModel):
    id: int
    date: date
    start_time: time
    matches: List[MatchInEventResponse]
    
    model_config = ConfigDict(from_attributes=True)
