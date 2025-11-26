from pydantic import BaseModel, Field, field_validator, ValidationInfo
from typing import Optional, List
from datetime import date, time
from enum import Enum

class MatchStatus(str, Enum):
    A_VENIR = "A_VENIR"
    TERMINE = "TERMINE"
    ANNULE = "ANNULE"

class PlayerMatchInfo(BaseModel):
    id: int
    firstname: str
    lastname: str
    
    class Config:
        from_attributes = True

class TeamMatchInfo(BaseModel):
    id: int
    company: str
    players: List[PlayerMatchInfo]
    
    class Config:
        from_attributes = True

class MatchCreate(BaseModel):
    date: date
    time: time
    court_number: int = Field(..., ge=1, le=10)
    team1_id: int
    team2_id: int

    @field_validator('team2_id')
    @classmethod
    def validate_teams(cls, v, info: ValidationInfo):
        if 'team1_id' in info.data and v == info.data['team1_id']:
            raise ValueError("Une équipe ne peut pas jouer contre elle-même")
        return v
    
    @field_validator('date')
    @classmethod
    def validate_date(cls, v):
        from datetime import date
        if v < date.today():
            raise ValueError("La date ne peut pas être dans le passé")
        return v

class MatchUpdate(BaseModel):
    date: Optional[date] = None
    time: Optional[time] = None
    court_number: Optional[int] = Field(None, ge=1, le=10)
    status: Optional[MatchStatus] = None
    score_team1: Optional[str] = None
    score_team2: Optional[str] = None

class MatchResponse(BaseModel):
    id: int
    date: date
    time: time
    court_number: int
    status: MatchStatus
    score_team1: Optional[str] = None
    score_team2: Optional[str] = None
    team1: TeamMatchInfo
    team2: TeamMatchInfo
    
    class Config:
        from_attributes = True
