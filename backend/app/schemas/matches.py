# ============================================
# FICHIER : backend/app/schemas/matches.py
# ============================================

from pydantic import BaseModel, Field, field_validator, ValidationInfo, ConfigDict, model_validator
from typing import Optional, List
from datetime import date as date_type, time as time_type
from enum import Enum

class MatchStatus(str, Enum):
    A_VENIR = "A_VENIR"
    TERMINE = "TERMINE"
    ANNULE = "ANNULE"

class PlayerMatchInfo(BaseModel):
    id: int
    firstname: str
    lastname: str
    company: str
    
    model_config = ConfigDict(from_attributes=True)

class TeamMatchInfo(BaseModel):
    id: int
    name: str
    players: List[PlayerMatchInfo]
    company: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)

    @field_validator('company', mode='before')
    @classmethod
    def get_company(cls, v, info: ValidationInfo):
        # Si v est déjà défini, on le garde
        if v:
            return v
        # Sinon on essaie de le récupérer depuis les joueurs
        # Note: Lors de la sérialisation depuis l'ORM, 'players' n'est peut-être pas encore dans 'info.data'
        # ou c'est l'objet ORM qui est passé.
        return None

    def model_post_init(self, __context):
        if not self.company and self.players:
            self.company = self.players[0].company

class MatchCreate(BaseModel):
    date: date_type
    time: time_type
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
    date: Optional[date_type] = None
    time: Optional[time_type] = None
    court_number: Optional[int] = Field(None, ge=1, le=10)
    status: Optional[MatchStatus] = None
    score_team1: Optional[str] = None
    score_team2: Optional[str] = None

    @field_validator('score_team1', 'score_team2')
    @classmethod
    def validate_score(cls, v):
        if v is None or (isinstance(v, str) and v.strip() == ""):
            return None
        
        if not re.match(r"^\d+-\d+(, \d+-\d+){1,2}$", v):
            raise ValueError("Format de score invalide")
        
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
                 raise ValueError("Il faut 2 jeux d'écart pour gagner un set (sauf tie-break 7-6)")
                 
            if max(games_1, games_2) > 7:
                 raise ValueError("Impossible d'avoir plus de 7 jeux dans un set")

        # Vérifier qu'une équipe a gagné au moins 2 sets
        sets_won_1 = 0
        sets_won_2 = 0
        
        for i, s in enumerate(sets):
            g1, g2 = map(int, s.split("-"))
            if g1 > g2:
                sets_won_1 += 1
            elif g2 > g1:
                sets_won_2 += 1
            
            # Si une équipe a déjà gagné 2 sets et qu'il reste des sets à jouer
            if (sets_won_1 == 2 or sets_won_2 == 2) and i < len(sets) - 1:
                 raise ValueError("Le match est déjà terminé après 2 sets gagnants")
        
        if sets_won_1 < 2 and sets_won_2 < 2:
            raise ValueError("Il faut au moins 2 sets gagnants pour terminer un match")
            
        return v
    
    @field_validator('date')
    @classmethod
    def validate_date(cls, v):
        if v is None:
            return v
        from datetime import date
        if v < date.today():
            raise ValueError("La date ne peut pas être dans le passé")
        return v

class MatchResponse(BaseModel):
    id: int
    date: date_type
    time: time_type
    court_number: int
    status: MatchStatus
    score_team1: Optional[str] = None
    score_team2: Optional[str] = None
    team1: TeamMatchInfo
    team2: TeamMatchInfo
    
    model_config = ConfigDict(from_attributes=True)
