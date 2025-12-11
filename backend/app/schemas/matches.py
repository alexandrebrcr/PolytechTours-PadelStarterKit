from pydantic import BaseModel, Field, field_validator, ValidationInfo, ConfigDict
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
    
    model_config = ConfigDict(from_attributes=True)

class TeamMatchInfo(BaseModel):
    id: int
    company: str
    players: List[PlayerMatchInfo]
    
    model_config = ConfigDict(from_attributes=True)

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

import re

class MatchUpdate(BaseModel):
    date: Optional[date] = None
    time: Optional[time] = None
    court_number: Optional[int] = Field(None, ge=1, le=10)
    status: Optional[MatchStatus] = None
    score_team1: Optional[str] = None
    score_team2: Optional[str] = None

    @field_validator('score_team1', 'score_team2')
    @classmethod
    def validate_score(cls, v):
        if v is None or v == "":
            return None
        
        # Format "X-Y, X-Y" ou "X-Y, X-Y, X-Y"
        # Regex pour un set : \d+-\d+
        # Regex complet : ^\d+-\d+(, \d+-\d+){1,2}$
        if not re.match(r"^\d+-\d+(, \d+-\d+){1,2}$", v):
            raise ValueError("Format de score invalide. Attendu : 'X-Y, X-Y' (ex: 6-4, 6-3)")
        
        sets = v.split(", ")
        if len(sets) > 3:
            raise ValueError("Un match se joue au meilleur de 3 sets maximum")
            
        for s in sets:
            try:
                games_1, games_2 = map(int, s.split("-"))
            except ValueError:
                raise ValueError("Les scores doivent être des nombres entiers")
                
            if games_1 < 0 or games_2 < 0:
                raise ValueError("Les scores ne peuvent pas être négatifs")
                
            # Le vainqueur d'un set doit avoir au moins 6 jeux
            if max(games_1, games_2) < 6:
                raise ValueError("Le vainqueur d'un set doit avoir au moins 6 jeux")
                
            # Si un set se termine 7-X, X doit être <= 5 (sauf tie-break 7-6)
            if games_1 == 7 and games_2 > 6:
                raise ValueError("Score de set invalide (7-X avec X > 6 impossible)")
            if games_2 == 7 and games_1 > 6:
                raise ValueError("Score de set invalide (X-7 avec X > 6 impossible)")
                
            # Ecart de 2 jeux minimum sauf si 7-6
            diff = abs(games_1 - games_2)
            if diff < 2 and not (games_1 == 7 and games_2 == 6) and not (games_1 == 6 and games_2 == 7):
                 # Cas particulier : certains formats acceptent le point en or à 6-6 ? 
                 # Mais ici la règle dit "Si un set se termine 7-6, c'est un tie-break"
                 # Donc 6-5 n'est pas une fin de set valide.
                 raise ValueError("Il faut 2 jeux d'écart pour gagner un set (sauf tie-break 7-6)")
                 
            if max(games_1, games_2) > 7:
                 raise ValueError("Impossible d'avoir plus de 7 jeux dans un set")

        return v

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
    
    model_config = ConfigDict(from_attributes=True)
