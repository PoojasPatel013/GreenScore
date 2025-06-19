import streamlit as st
import hashlib
import jwt
from datetime import datetime, timedelta
from functools import wraps
import re

class AuthManager:
    def __init__(self, db):
        self.db = db
        self.secret_key = "your-secret-key-change-in-production"
        self.algorithm = "HS256"
    
    def hash_password(self, password: str) -> str:
        """Hash password using SHA256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def validate_email(self, email: str) -> bool:
        """Validate email format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    def validate_password(self, password: str) -> tuple:
        """Validate password strength"""
        errors = []
        if len(password) < 8:
            errors.append("Password must be at least 8 characters long")
        if not re.search(r"[A-Z]", password):
            errors.append("Password must contain at least one uppercase letter")
        if not re.search(r"[a-z]", password):
            errors.append("Password must contain at least one lowercase letter")
        if not re.search(r"\d", password):
            errors.append("Password must contain at least one number")
        
        return len(errors) == 0, errors
    
    def register_user(self, email: str, password: str, username: str) -> tuple:
        """Register a new user"""
        try:
            # Validate inputs
            if not self.validate_email(email):
                return False, "Invalid email format"
            
            is_valid, errors = self.validate_password(password)
            if not is_valid:
                return False, "; ".join(errors)
            
            if len(username.strip()) < 3:
                return False, "Username must be at least 3 characters long"
            
            # Check if user already exists
            if self.db.get_user_by_email(email):
                return False, "User with this email already exists"
            
            if self.db.get_user_by_username(username):
                return False, "Username is already taken"
            
            # Create user
            user_data = {
                'email': email.lower().strip(),
                'username': username.strip(),
                'password_hash': self.hash_password(password),
                'created_at': datetime.now(),
                'profile': {
                    'first_name': '',
                    'last_name': '',
                    'avatar_url': '',
                    'bio': '',
                    'location': '',
                    'preferences': {
                        'units': 'metric',
                        'notifications': True,
                        'public_profile': False
                    }
                },
                'stats': {
                    'total_score': 1000,
                    'co2_saved_kg': 0,
                    'trees_equivalent': 0,
                    'streak_days': 0,
                    'level': 'Eco Newbie',
                    'achievements': ['First Steps']
                },
                'settings': {
                    'monthly_target_kg': 500,
                    'currency': 'USD',
                    'timezone': 'UTC'
                }
            }
            
            result = self.db.create_user(user_data)
            if result:
                return True, "Account created successfully!"
            else:
                return False, "Failed to create account. Please try again."
                
        except Exception as e:
            return False, f"Registration error: {str(e)}"
    
    def login_user(self, email: str, password: str) -> tuple:
        """Authenticate user login"""
        try:
            user = self.db.get_user_by_email(email.lower().strip())
            if not user:
                return False, "Invalid email or password", None
            
            # Verify password
            if user['password_hash'] != self.hash_password(password):
                return False, "Invalid email or password", None
            
            # Generate JWT token
            token_payload = {
                'user_id': str(user['_id']),
                'email': user['email'],
                'exp': datetime.utcnow() + timedelta(days=7)
            }
            
            token = jwt.encode(token_payload, self.secret_key, algorithm=self.algorithm)
            
            # Update last login
            self.db.update_user_login(str(user['_id']))
            
            return True, "Login successful!", {
                'token': token,
                'user': user
            }
            
        except Exception as e:
            return False, f"Login error: {str(e)}", None
    
    def verify_token(self, token: str) -> tuple:
        """Verify JWT token and return user data"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            user_id = payload['user_id']
            user = self.db.get_user_by_id(user_id)
            
            if user:
                return True, user
            else:
                return False, None
                
        except jwt.ExpiredSignatureError:
            return False, None
        except jwt.InvalidTokenError:
            return False, None
    
    def logout_user(self):
        """Logout user by clearing session"""
        for key in ['authenticated', 'user_token', 'user_data']:
            if key in st.session_state:
                del st.session_state[key]

def require_auth(func):
    """Decorator to require authentication for pages"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not st.session_state.get('authenticated', False):
            st.error("🔒 Please log in to access this page")
            st.stop()
        return func(*args, **kwargs)
    return wrapper

def check_authentication():
    """Check if user is authenticated and validate token"""
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    
    if st.session_state.get('authenticated') and st.session_state.get('user_token'):
        from database import Database
        db = Database()
        auth = AuthManager(db)
        
        is_valid, user_data = auth.verify_token(st.session_state.user_token)
        if is_valid:
            st.session_state.user_data = user_data
            return True
        else:
            # Token invalid, logout
            auth.logout_user()
            return False
    
    return st.session_state.get('authenticated', False)
