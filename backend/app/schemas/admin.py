from pydantic import BaseModel, EmailStr, Field, validator
from typing import List, Optional
import re

# --- Players ---
class PlayerBase(BaseModel):
    firstname: str = Field(..., min_length=2, max_length=50)
    lastname: str = Field(..., min_length=2, max_length=50)
    company: str = Field(..., min_length=2, max_length=100)
    license_number: str
    email: EmailStr

    @validator('firstname', 'lastname')
    def validate_name(cls, v):
        if not re.match(r"^[a-zA-Z\s]+$", v):
            raise ValueError("Le nom/prénom ne doit contenir que des lettres et espaces")
        return v

    @validator('license_number')
    def validate_license(cls, v):
        if not re.match(r"^L\d{6}$", v):
            raise ValueError("Le numéro de licence doit être au format LXXXXXX")
        return v

class PlayerCreate(PlayerBase):
    pass

class PlayerUpdate(BaseModel):
    firstname: Optional[str] = Field(None, min_length=2, max_length=50)
    lastname: Optional[str] = Field(None, min_length=2, max_length=50)
    company: Optional[str] = Field(None, min_length=2, max_length=100)
    
    @validator('firstname', 'lastname')
    def validate_name(cls, v):
        if v and not re.match(r"^[a-zA-Z\s]+$", v):
            raise ValueError("Le nom/prénom ne doit contenir que des lettres et espaces")
        return v

class PlayerResponse(PlayerBase):
    id: int
    team_id: Optional[int] = None
    user_role: Optional[str] = None
    
    class Config:
        from_attributes = True

# --- Teams ---
class TeamCreate(BaseModel):
    company: str
    player1_id: int
    player2_id: int

class TeamResponse(BaseModel):
    id: int
    company: str
    players: List[PlayerResponse]
    pool_id: Optional[int] = None
    
    class Config:
        from_attributes = True

# --- Pools ---
class PoolCreate(BaseModel):
    name: str
    team_ids: List[int]

    @validator('team_ids')
    def validate_team_count(cls, v):
        if len(v) != 6:
            raise ValueError("Une poule doit contenir exactement 6 équipes")
        return v

class PoolResponse(BaseModel):
    id: int
    name: str
    teams: List[TeamResponse]
    
    class Config:
        from_attributes = True

# --- Accounts ---
class AccountCreate(BaseModel):
    player_id: int

class AccountResponse(BaseModel):
    email: str
    temp_password: str
