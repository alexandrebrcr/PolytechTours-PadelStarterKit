# ============================================
# FICHIER : backend/app/schemas/auth.py
# ============================================

from pydantic import BaseModel, EmailStr, Field, field_validator, ValidationInfo
from typing import Optional
from datetime import date
import re

class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=1)

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class UserUpdate(BaseModel):
    firstname: str = Field(..., min_length=2, max_length=50)
    lastname: str = Field(..., min_length=2, max_length=50)
    email: EmailStr
    birthdate: Optional[date] = None

    @field_validator('firstname', 'lastname')
    @classmethod
    def validate_name(cls, v):
        if not re.match(r"^[a-zA-Z\s\-\']+$", v):
            raise ValueError("Le nom/prénom ne doit contenir que des lettres, espaces, tirets et apostrophes")
        return v

    @field_validator('birthdate')
    @classmethod
    def validate_age(cls, v):
        if v is None:
            return v
        today = date.today()
        age = today.year - v.year - ((today.month, today.day) < (v.month, v.day))
        if age < 16:
            raise ValueError("L'utilisateur doit avoir au moins 16 ans")
        if v > today:
            raise ValueError("La date de naissance ne peut pas être dans le futur")
        return v

class UserResponse(BaseModel):
    id: int
    email: str
    role: str
    must_change_password: bool
    firstname: Optional[str] = None
    lastname: Optional[str] = None
    birthdate: Optional[date] = None
    license_number: Optional[str] = None
    profile_picture: Optional[str] = None
    player_id: Optional[int] = None
    
    class Config:
        from_attributes = True

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse

class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str = Field(..., min_length=12)
    confirm_password: str
    
    @field_validator('new_password')
    @classmethod
    def validate_password(cls, v):
        if len(v) < 12:
            raise ValueError('Le mot de passe doit contenir au moins 12 caractères')
        if not re.search(r'[A-Z]', v):
            raise ValueError('Le mot de passe doit contenir au moins une majuscule')
        if not re.search(r'[a-z]', v):
            raise ValueError('Le mot de passe doit contenir au moins une minuscule')
        if not re.search(r'\d', v):
            raise ValueError('Le mot de passe doit contenir au moins un chiffre')
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            raise ValueError('Le mot de passe doit contenir au moins un caractère spécial')
        return v
    
    @field_validator('confirm_password')
    @classmethod
    def passwords_match(cls, v, info: ValidationInfo):
        if 'new_password' in info.data and v != info.data['new_password']:
            raise ValueError('Les mots de passe ne correspondent pas')
        return v
