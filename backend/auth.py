from flask_login import LoginManager, UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from typing import Optional, Dict, List
from .database import Database
from .models import User

class AuthService:
    def __init__(self, db: Database):
        self.db = db
        self.login_manager = LoginManager()

    def init_app(self, app):
        self.login_manager.init_app(app)
        
    def register_user(self, email: str, password: str, username: str) -> Optional[str]:
        """Register a new user"""
        if self.db.get_user_by_email(email):
            return None  # Email already exists
            
        user = User(
            id=str(datetime.now().timestamp()),
            email=email,
            username=username,
            password_hash=generate_password_hash(password)
        )
        return self.db.create_user(user)

    def login_user(self, email: str, password: str) -> Optional[Dict]:
        """Authenticate user and return user data if successful"""
        user = self.db.get_user_by_email(email)
        if user and check_password_hash(user['password_hash'], password):
            return user
        return None

    def update_profile(self, user_id: str, full_name: str, bio: str, location: str) -> bool:
        """Update user profile information"""
        profile = {
            'full_name': full_name,
            'bio': bio,
            'location': location
        }
        return self.db.update_profile(user_id, profile)

    def get_profile(self, user_id: str) -> Optional[Dict]:
        """Get user profile information"""
        return self.db.get_profile(user_id)

    def update_user_data(self, user_id: str, data: Dict) -> bool:
        """Update user data (level, xp, points, etc.)"""
        return self.db.update_user(user_id, data)

    def get_user_rank(self, user_id: str) -> int:
        """Get user's rank in the leaderboard"""
        return self.db.get_user_rank(user_id)

    def get_leaderboard(self, limit: int = 10) -> List[Dict]:
        """Get top users from leaderboard"""
        return self.db.get_leaderboard(limit)
