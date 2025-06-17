from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from typing import Optional, List, Dict
from dataclasses import dataclass

@dataclass
class User(UserMixin):
    id: str
    email: str
    username: str
    password_hash: str
    level: int = 1
    xp: int = 0
    points: int = 0
    carbon_saved: float = 0.0
    created_at: datetime = datetime.utcnow()
    last_active: datetime = datetime.utcnow()
    
    def set_password(self, password: str):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

@dataclass
class EcoEvent:
    id: str
    user_id: str
    event_type: str
    impact: float
    points: int
    timestamp: datetime
    description: Optional[str] = None
    
@dataclass
class Achievement:
    id: str
    user_id: str
    name: str
    description: str
    points: int
    timestamp: datetime

@dataclass
class UserProfile:
    user_id: str
    full_name: str
    avatar_url: str
    bio: str
    location: str
    
@dataclass
class LeaderboardEntry:
    user_id: str
    username: str
    points: int
    level: int
    xp: int
    carbon_saved: float
    rank: int
