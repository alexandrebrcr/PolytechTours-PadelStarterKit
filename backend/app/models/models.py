# ============================================
# FICHIER : backend/app/models/models.py
# ============================================

from sqlalchemy import Boolean, Column, Integer, String, DateTime, ForeignKey, Date
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(String, nullable=False)  # JOUEUR ou ADMINISTRATEUR
    firstname = Column(String, nullable=True)
    lastname = Column(String, nullable=True)
    birthdate = Column(Date, nullable=True)
    license_number = Column(String, nullable=True)
    profile_picture = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    must_change_password = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relation avec Player (un User peut être lié à un Player)
    player_id = Column(Integer, ForeignKey("players.id"), nullable=True)
    player = relationship("Player", back_populates="user")

class LoginAttempt(Base):
    __tablename__ = "login_attempts"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, index=True, nullable=False)
    attempts_count = Column(Integer, default=0)
    last_attempt = Column(DateTime(timezone=True))
    locked_until = Column(DateTime(timezone=True), nullable=True)

class Player(Base):
    __tablename__ = "players"
    
    id = Column(Integer, primary_key=True, index=True)
    firstname = Column(String, nullable=False)
    lastname = Column(String, nullable=False)
    company = Column(String, nullable=False)
    license_number = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    
    # Relation avec User
    user = relationship("User", back_populates="player", uselist=False)
    
    # Relation avec Team
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=True)
    team = relationship("Team", back_populates="players")

    @property
    def user_role(self):
        return self.user.role if self.user else None

class Team(Base):
    __tablename__ = "teams"
    
    id = Column(Integer, primary_key=True, index=True)
    company = Column(String, nullable=False)
    
    # Relation avec Player
    players = relationship("Player", back_populates="team")
    
    # Relation avec Pool
    pool_id = Column(Integer, ForeignKey("pools.id"), nullable=True)
    pool = relationship("Pool", back_populates="teams")

class Pool(Base):
    __tablename__ = "pools"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    
    # Relation avec Team
    teams = relationship("Team", back_populates="pool")
