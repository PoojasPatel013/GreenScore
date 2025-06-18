from pymongo import MongoClient
from datetime import datetime, timedelta
import os

class Database:
    def __init__(self):
        # In production, use environment variables
        self.client = MongoClient('mongodb://localhost:27017/')
        self.db = self.client['greenscore']
        self.users = self.db['users']
        self.transactions = self.db['transactions']
        self.goals = self.db['goals']
        self.challenges = self.db['challenges']
    
    def get_user_data(self, user_id):
        user = self.users.find_one({'user_id': user_id})
        if not user:
            # Create new user
            user = {
                'user_id': user_id,
                'username': f'User_{user_id[-4:]}',
                'created_at': datetime.now(),
                'total_score': 1000,
                'trees_planted': 0,
                'level': 1
            }
            self.users.insert_one(user)
        return user
    
    def get_user_transactions(self, user_id, days=30):
        start_date = datetime.now() - timedelta(days=days)
        transactions = list(self.transactions.find({
            'user_id': user_id,
            'date': {'$gte': start_date.isoformat()}
        }).sort('date', -1))
        return transactions
    
    def add_transaction(self, transaction):
        transaction['created_at'] = datetime.now()
        return self.transactions.insert_one(transaction)
    
    def get_user_goals(self, user_id):
        return list(self.goals.find({
            'user_id': user_id,
            'active': True
        }))
    
    def add_user_goal(self, goal):
        goal['created_at'] = datetime.now()
        goal['active'] = True
        return self.goals.insert_one(goal)
    
    def update_goal_progress(self, goal_id, progress):
        return self.goals.update_one(
            {'_id': goal_id},
            {'$set': {'current': progress}}
        )
