from pydantic import BaseModel, EmailStr, Field, field_validator, ConfigDict
from typing import List, Optional
import re

# --- Players ---
class PlayerBase(BaseModel):
    firstname: str = Field(..., min_length=2, max_length=50)
    lastname: str = Field(..., min_length=2, max_length=50)
    company: str = Field(..., min_length=2, max_length=100)
    license_number: str
    email: EmailStr

    @field_validator('firstname')
    @classmethod
    def validate_firstname(cls, v):
        if not re.match(r"^[a-zA-Z\s\-_']+$", v):
            raise ValueError("Le prénom ne doit contenir que des lettres, espaces, tirets, underscores et apostrophes")
        return v

    @field_validator('lastname')
    @classmethod
    def validate_lastname(cls, v):
        if not re.match(r"^[a-zA-Z\s\-_\.']+$", v):
            raise ValueError("Le nom ne doit contenir que des lettres, espaces, tirets, underscores, points et apostrophes")
        return v

    @field_validator('license_number')
    @classmethod
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
    
    @field_validator('firstname')
    @classmethod
    def validate_firstname(cls, v):
        if v and not re.match(r"^[a-zA-Z\s\-_']+$", v):
            raise ValueError("Le prénom ne doit contenir que des lettres, espaces, tirets, underscores et apostrophes")
        return v

    @field_validator('lastname')
    @classmethod
    def validate_lastname(cls, v):
        if v and not re.match(r"^[a-zA-Z\s\-_\.']+$", v):
            raise ValueError("Le nom ne doit contenir que des lettres, espaces, tirets, underscores, points et apostrophes")
        return v

class PlayerResponse(PlayerBase):
    id: int
    team_id: Optional[int] = None
    user_role: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)

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
    
    model_config = ConfigDict(from_attributes=True)

# --- Pools ---
class PoolCreate(BaseModel):
    name: str
    team_ids: List[int]

    @field_validator('team_ids')
    @classmethod
    def validate_team_count(cls, v):
        if len(v) != 6:
            raise ValueError("Une poule doit contenir exactement 6 équipes")
        return v

class PoolResponse(BaseModel):
    id: int
    name: str
    teams: List[TeamResponse]
    
    model_config = ConfigDict(from_attributes=True)

# --- Accounts ---
class AccountCreate(BaseModel):
    player_id: int

class AccountResponse(BaseModel):
    email: str
    temp_password: str

class RoleUpdate(BaseModel):
    role: str
