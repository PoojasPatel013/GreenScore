import os
from pymongo import MongoClient
from bson import ObjectId
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import json

class Database:
    def __init__(self):
        # MongoDB connection string - replace with your actual connection string
        # For development, you can use MongoDB Atlas free tier or local MongoDB
        mongo_uri = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/')
        
        try:
            self.client = MongoClient(mongo_uri)
            self.db = self.client['greenscore_app']
            
            # Collections
            self.users = self.db['users']
            self.transactions = self.db['transactions']
            self.goals = self.db['goals']
            self.challenges = self.db['challenges']
            self.achievements = self.db['achievements']
            
            # Test connection
            self.client.admin.command('ping')
            print("✅ Connected to MongoDB successfully!")
            
        except Exception as e:
            print(f"❌ MongoDB connection failed: {e}")
            # Fallback to JSON file storage for development
            self.use_json_fallback = True
            self.json_file = "greenscore_data.json"
            self._load_json_data()
    
    def _load_json_data(self):
        """Load data from JSON file as fallback"""
        if os.path.exists(self.json_file):
            try:
                with open(self.json_file, 'r') as f:
                    self.json_data = json.load(f)
            except:
                self.json_data = self._get_default_data()
        else:
            self.json_data = self._get_default_data()
    
    def _save_json_data(self):
        """Save data to JSON file"""
        try:
            with open(self.json_file, 'w') as f:
                json.dump(self.json_data, f, indent=2, default=str)
        except Exception as e:
            print(f"Error saving JSON data: {e}")
    
    def _get_default_data(self):
        """Get default data structure"""
        return {
            'users': {},
            'transactions': [],
            'goals': [],
            'challenges': [],
            'achievements': []
        }
    
    # User Management
    def create_user(self, user_data: Dict) -> bool:
        """Create a new user"""
        try:
            if hasattr(self, 'use_json_fallback'):
                user_id = str(len(self.json_data['users']) + 1)
                user_data['_id'] = user_id
                self.json_data['users'][user_id] = user_data
                self._save_json_data()
                return True
            else:
                result = self.users.insert_one(user_data)
                return result.inserted_id is not None
        except Exception as e:
            print(f"Error creating user: {e}")
            return False
    
    def get_user_by_email(self, email: str) -> Optional[Dict]:
        """Get user by email"""
        try:
            if hasattr(self, 'use_json_fallback'):
                for user_id, user in self.json_data['users'].items():
                    if user.get('email') == email:
                        return user
                return None
            else:
                return self.users.find_one({'email': email})
        except Exception as e:
            print(f"Error getting user by email: {e}")
            return None
    
    def get_user_by_username(self, username: str) -> Optional[Dict]:
        """Get user by username"""
        try:
            if hasattr(self, 'use_json_fallback'):
                for user_id, user in self.json_data['users'].items():
                    if user.get('username') == username:
                        return user
                return None
            else:
                return self.users.find_one({'username': username})
        except Exception as e:
            print(f"Error getting user by username: {e}")
            return None
    
    def get_user_by_id(self, user_id: str) -> Optional[Dict]:
        """Get user by ID"""
        try:
            if hasattr(self, 'use_json_fallback'):
                return self.json_data['users'].get(user_id)
            else:
                return self.users.find_one({'_id': ObjectId(user_id)})
        except Exception as e:
            print(f"Error getting user by ID: {e}")
            return None
    
    def update_user_login(self, user_id: str):
        """Update user's last login time"""
        try:
            if hasattr(self, 'use_json_fallback'):
                if user_id in self.json_data['users']:
                    self.json_data['users'][user_id]['last_login'] = datetime.now().isoformat()
                    self._save_json_data()
            else:
                self.users.update_one(
                    {'_id': ObjectId(user_id)},
                    {'$set': {'last_login': datetime.now()}}
                )
        except Exception as e:
            print(f"Error updating user login: {e}")
    
    def update_user_profile(self, user_id: str, profile_data: Dict) -> bool:
        """Update user profile"""
        try:
            if hasattr(self, 'use_json_fallback'):
                if user_id in self.json_data['users']:
                    self.json_data['users'][user_id]['profile'].update(profile_data)
                    self._save_json_data()
                    return True
                return False
            else:
                result = self.users.update_one(
                    {'_id': ObjectId(user_id)},
                    {'$set': {'profile': profile_data}}
                )
                return result.modified_count > 0
        except Exception as e:
            print(f"Error updating user profile: {e}")
            return False
    
    def update_user_stats(self, user_id: str, stats_data: Dict) -> bool:
        """Update user statistics"""
        try:
            if hasattr(self, 'use_json_fallback'):
                if user_id in self.json_data['users']:
                    self.json_data['users'][user_id]['stats'].update(stats_data)
                    self._save_json_data()
                    return True
                return False
            else:
                result = self.users.update_one(
                    {'_id': ObjectId(user_id)},
                    {'$set': {'stats': stats_data}}
                )
                return result.modified_count > 0
        except Exception as e:
            print(f"Error updating user stats: {e}")
            return False
    
    # Transaction Management
    def add_transaction(self, transaction_data: Dict) -> bool:
        """Add a new transaction"""
        try:
            transaction_data['created_at'] = datetime.now()
            
            if hasattr(self, 'use_json_fallback'):
                transaction_data['_id'] = str(len(self.json_data['transactions']) + 1)
                self.json_data['transactions'].append(transaction_data)
                self._save_json_data()
                return True
            else:
                result = self.transactions.insert_one(transaction_data)
                return result.inserted_id is not None
        except Exception as e:
            print(f"Error adding transaction: {e}")
            return False
    
    def get_user_transactions(self, user_id: str, days: int = 30, limit: int = 100) -> List[Dict]:
        """Get user transactions"""
        try:
            start_date = datetime.now() - timedelta(days=days)
            
            if hasattr(self, 'use_json_fallback'):
                user_transactions = [
                    t for t in self.json_data['transactions']
                    if t.get('user_id') == user_id and
                    datetime.fromisoformat(t['date']) >= start_date
                ]
                return sorted(user_transactions, key=lambda x: x['date'], reverse=True)[:limit]
            else:
                cursor = self.transactions.find({
                    'user_id': user_id,
                    'date': {'$gte': start_date}
                }).sort('date', -1).limit(limit)
                return list(cursor)
        except Exception as e:
            print(f"Error getting user transactions: {e}")
            return []
    
    def get_user_monthly_stats(self, user_id: str) -> Dict:
        """Get user's monthly carbon footprint statistics"""
        try:
            start_of_month = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            
            transactions = self.get_user_transactions(user_id, days=30)
            
            total_amount = sum(t.get('amount', 0) for t in transactions)
            total_carbon = sum(t.get('carbon_kg', 0) for t in transactions)
            
            # Category breakdown
            categories = {}
            for t in transactions:
                category = t.get('category', 'Other')
                if category not in categories:
                    categories[category] = {'amount': 0, 'carbon': 0, 'count': 0}
                
                categories[category]['amount'] += t.get('amount', 0)
                categories[category]['carbon'] += t.get('carbon_kg', 0)
                categories[category]['count'] += 1
            
            return {
                'total_amount': total_amount,
                'total_carbon': total_carbon,
                'transaction_count': len(transactions),
                'categories': categories,
                'daily_average': total_carbon / 30 if total_carbon > 0 else 0
            }
            
        except Exception as e:
            print(f"Error getting monthly stats: {e}")
            return {
                'total_amount': 0,
                'total_carbon': 0,
                'transaction_count': 0,
                'categories': {},
                'daily_average': 0
            }
    
    # Goals Management
    def add_user_goal(self, user_id: str, goal_data: Dict) -> bool:
        """Add a new goal for user"""
        try:
            goal_data.update({
                'user_id': user_id,
                'created_at': datetime.now(),
                'active': True,
                'completed': False
            })
            
            if hasattr(self, 'use_json_fallback'):
                goal_data['_id'] = str(len(self.json_data['goals']) + 1)
                self.json_data['goals'].append(goal_data)
                self._save_json_data()
                return True
            else:
                result = self.goals.insert_one(goal_data)
                return result.inserted_id is not None
        except Exception as e:
            print(f"Error adding goal: {e}")
            return False
    
    def get_user_goals(self, user_id: str) -> List[Dict]:
        """Get active user goals"""
        try:
            if hasattr(self, 'use_json_fallback'):
                return [
                    g for g in self.json_data['goals']
                    if g.get('user_id') == user_id and g.get('active', True)
                ]
            else:
                cursor = self.goals.find({
                    'user_id': user_id,
                    'active': True
                }).sort('created_at', -1)
                return list(cursor)
        except Exception as e:
            print(f"Error getting user goals: {e}")
            return []
    
    def update_goal_progress(self, goal_id: str, progress: float) -> bool:
        """Update goal progress"""
        try:
            if hasattr(self, 'use_json_fallback'):
                for goal in self.json_data['goals']:
                    if goal.get('_id') == goal_id:
                        goal['current'] = progress
                        if progress >= goal.get('target', 100):
                            goal['completed'] = True
                            goal['completed_at'] = datetime.now().isoformat()
                        self._save_json_data()
                        return True
                return False
            else:
                update_data = {'current': progress}
                if progress >= 100:
                    update_data.update({
                        'completed': True,
                        'completed_at': datetime.now()
                    })
                
                result = self.goals.update_one(
                    {'_id': ObjectId(goal_id)},
                    {'$set': update_data}
                )
                return result.modified_count > 0
        except Exception as e:
            print(f"Error updating goal progress: {e}")
            return False
    
    # Achievements Management
    def add_user_achievement(self, user_id: str, achievement_name: str) -> bool:
        """Add achievement to user"""
        try:
            user = self.get_user_by_id(user_id)
            if user:
                achievements = user.get('stats', {}).get('achievements', [])
                if achievement_name not in achievements:
                    achievements.append(achievement_name)
                    
                    if hasattr(self, 'use_json_fallback'):
                        self.json_data['users'][user_id]['stats']['achievements'] = achievements
                        self._save_json_data()
                    else:
                        self.users.update_one(
                            {'_id': ObjectId(user_id)},
                            {'$set': {'stats.achievements': achievements}}
                        )
                    return True
            return False
        except Exception as e:
            print(f"Error adding achievement: {e}")
            return False
    
    # Analytics and Leaderboard
    def get_leaderboard(self, limit: int = 10) -> List[Dict]:
        """Get global leaderboard"""
        try:
            if hasattr(self, 'use_json_fallback'):
                users_list = list(self.json_data['users'].values())
                sorted_users = sorted(
                    users_list,
                    key=lambda x: x.get('stats', {}).get('total_score', 0),
                    reverse=True
                )
                return sorted_users[:limit]
            else:
                cursor = self.users.find({}, {
                    'username': 1,
                    'stats': 1,
                    'profile.avatar_url': 1
                }).sort('stats.total_score', -1).limit(limit)
                return list(cursor)
        except Exception as e:
            print(f"Error getting leaderboard: {e}")
            return []
