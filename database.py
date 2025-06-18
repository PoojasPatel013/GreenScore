import json
import os
from datetime import datetime, timedelta
from typing import List, Dict, Optional

class Database:
    def __init__(self, data_file="greenscore_data.json"):
        self.data_file = data_file
        self.data = self._load_data()
    
    def _load_data(self) -> Dict:
        """Load data from JSON file or create default structure"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                pass
        
        # Default data structure
        return {
            'users': {},
            'transactions': [],
            'goals': [],
            'challenges': [],
            'leaderboard': []
        }
    
    def _save_data(self):
        """Save data to JSON file"""
        try:
            with open(self.data_file, 'w') as f:
                json.dump(self.data, f, indent=2, default=str)
        except Exception as e:
            print(f"Error saving data: {e}")
    
    def get_user_data(self, user_id: str) -> Dict:
        """Get user data or create new user"""
        if user_id not in self.data['users']:
            self.data['users'][user_id] = {
                'user_id': user_id,
                'username': f'EcoUser_{user_id[-4:]}',
                'created_at': datetime.now().isoformat(),
                'total_score': 1000,
                'trees_planted': 0,
                'level': 1,
                'achievements': ['First Steps'],
                'streak_days': 1
            }
            self._save_data()
        
        return self.data['users'][user_id]
    
    def update_user_data(self, user_id: str, updates: Dict):
        """Update user data"""
        if user_id in self.data['users']:
            self.data['users'][user_id].update(updates)
            self._save_data()
    
    def get_user_transactions(self, user_id: str, days: int = 30) -> List[Dict]:
        """Get user transactions for specified days"""
        start_date = datetime.now() - timedelta(days=days)
        
        user_transactions = [
            t for t in self.data['transactions']
            if t.get('user_id') == user_id and 
            datetime.fromisoformat(t['date']) >= start_date
        ]
        
        return sorted(user_transactions, key=lambda x: x['date'], reverse=True)
    
    def add_transaction(self, transaction: Dict) -> bool:
        """Add new transaction"""
        try:
            transaction['id'] = len(self.data['transactions']) + 1
            transaction['created_at'] = datetime.now().isoformat()
            self.data['transactions'].append(transaction)
            self._save_data()
            return True
        except Exception as e:
            print(f"Error adding transaction: {e}")
            return False
    
    def get_user_goals(self, user_id: str) -> List[Dict]:
        """Get active user goals"""
        return [
            g for g in self.data['goals']
            if g.get('user_id') == user_id and g.get('active', True)
        ]
    
    def add_user_goal(self, goal: Dict) -> bool:
        """Add new user goal"""
        try:
            goal['id'] = len(self.data['goals']) + 1
            goal['created_at'] = datetime.now().isoformat()
            self.data['goals'].append(goal)
            self._save_data()
            return True
        except Exception as e:
            print(f"Error adding goal: {e}")
            return False
    
    def update_goal_progress(self, goal_id: int, progress: float) -> bool:
        """Update goal progress"""
        try:
            for goal in self.data['goals']:
                if goal.get('id') == goal_id:
                    goal['current'] = progress
                    self._save_data()
                    return True
            return False
        except Exception as e:
            print(f"Error updating goal: {e}")
            return False
    
    def get_leaderboard(self, limit: int = 10) -> List[Dict]:
        """Get global leaderboard"""
        # Sort users by score
        sorted_users = sorted(
            self.data['users'].values(),
            key=lambda x: x.get('total_score', 0),
            reverse=True
        )
        
        leaderboard = []
        for i, user in enumerate(sorted_users[:limit]):
            leaderboard.append({
                'rank': i + 1,
                'username': user['username'],
                'score': user.get('total_score', 0),
                'level': user.get('level', 1),
                'achievements': len(user.get('achievements', [])),
                'streak': user.get('streak_days', 0)
            })
        
        return leaderboard
