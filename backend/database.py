from pymongo import MongoClient
from dotenv import load_dotenv
import os
from datetime import datetime
from typing import Optional, List, Dict
from .models import User, EcoEvent, Achievement, UserProfile, LeaderboardEntry

load_dotenv()

class Database:
    def __init__(self):
        # Use MongoDB Compass connection string format
        connection_string = f"mongodb://{os.getenv('MONGODB_HOST', 'localhost')}:{os.getenv('MONGODB_PORT', '27017')}/green"
        self.client = MongoClient(connection_string)
        self.db = self.client['green']
        self.users = self.db['users']
        self.eco_events = self.db['eco_events']
        self.achievements = self.db['achievements']
        self.profiles = self.db['profiles']
        self.leaderboard = self.db['leaderboard']

    def create_user(self, user: User) -> str:
        """Create a new user account"""
        user_dict = user.__dict__
        user_dict['id'] = str(user_dict.pop('id'))  # Convert dataclass id to string
        result = self.users.insert_one(user_dict)
        return str(result.inserted_id)

    def get_user_by_email(self, email: str) -> Optional[Dict]:
        """Get user by email"""
        return self.users.find_one({'email': email})

    def get_user_by_id(self, user_id: str) -> Optional[Dict]:
        """Get user by ID"""
        return self.users.find_one({'id': user_id})

    def update_user(self, user_id: str, data: Dict) -> bool:
        """Update user information"""
        result = self.users.update_one(
            {'id': user_id},
            {'$set': data}
        )
        return result.modified_count > 0

    def log_eco_event(self, event: EcoEvent) -> str:
        """Log a new eco-friendly event"""
        event_dict = event.__dict__
        event_dict['id'] = str(event_dict.pop('id'))
        result = self.eco_events.insert_one(event_dict)
        return str(result.inserted_id)

    def get_user_events(self, user_id: str) -> List[Dict]:
        """Get all eco events for a user"""
        return list(self.eco_events.find({'user_id': user_id}))

    def create_achievement(self, achievement: Achievement) -> str:
        """Create a new achievement"""
        achievement_dict = achievement.__dict__
        achievement_dict['id'] = str(achievement_dict.pop('id'))
        result = self.achievements.insert_one(achievement_dict)
        return str(result.inserted_id)

    def get_user_achievements(self, user_id: str) -> List[Dict]:
        """Get all achievements for a user"""
        return list(self.achievements.find({'user_id': user_id}))

    def update_leaderboard(self, user_id: str, points: int, carbon_saved: float):
        """Update user's position in leaderboard"""
        user = self.get_user_by_id(user_id)
        if user:
            self.users.update_one(
                {'id': user_id},
                {
                    '$set': {
                        'points': user.get('points', 0) + points,
                        'carbon_saved': user.get('carbon_saved', 0) + carbon_saved,
                        'last_active': datetime.now()
                    }
                }
            )

    def get_leaderboard(self, limit: int = 10) -> List[Dict]:
        """Get top users from leaderboard"""
        return list(self.users.find()
                    .sort([('points', -1), ('carbon_saved', -1)])
                    .limit(limit))

    def update_profile(self, user_id: str, profile: UserProfile) -> bool:
        """Update user profile information"""
        profile_dict = profile.__dict__
        result = self.profiles.update_one(
            {'user_id': user_id},
            {'$set': profile_dict},
            upsert=True
        )
        return result.modified_count > 0

    def get_profile(self, user_id: str) -> Optional[Dict]:
        """Get user profile information"""
        return self.profiles.find_one({'user_id': user_id})

    def get_user_rank(self, user_id: str) -> int:
        """Get user's rank in the leaderboard"""
        user = self.get_user_by_id(user_id)
        if not user:
            return 0
        
        pipeline = [
            {
                '$sort': {
                    'points': -1,
                    'carbon_saved': -1
                }
            },
            {
                '$group': {
                    '_id': None,
                    'rank': {
                        '$sum': {
                            '$cond': [
                                {
                                    '$and': [
                                        {'$gt': ['$points', user.get('points', 0)]},
                                        {'$or': [
                                            {'$gt': ['$carbon_saved', user.get('carbon_saved', 0)]},
                                            {'$eq': ['$carbon_saved', user.get('carbon_saved', 0)]}
                                        ]}
                                    ]
                                },
                                1,
                                0
                            ]
                        }
                    }
                }
            }
        ]
        
        result = list(self.users.aggregate(pipeline))
        return result[0]['rank'] + 1 if result else 0
