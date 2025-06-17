from pymongo import MongoClient
from dotenv import load_dotenv
import os
from datetime import datetime

load_dotenv()

class Database:
    def __init__(self):
        # Use MongoDB Compass connection string format
        connection_string = f"mongodb://{os.getenv('MONGODB_HOST', 'localhost')}:{os.getenv('MONGODB_PORT', '27017')}/green"
        self.client = MongoClient(connection_string)
        self.db = self.client['green']
        self.users = self.db['users']
        self.transactions = self.db['transactions']
        self.rewards = self.db['rewards']

    def get_user_score(self, user_id):
        user = self.users.find_one({'_id': user_id})
        return user['greenscore'] if user else 0

    def get_top_users(self):
        return list(self.users.find()
                    .sort('greenscore', -1)
                    .limit(10))

    def add_transaction(self, user_id, transaction):
        transaction['user_id'] = user_id
        self.transactions.insert_one(transaction)

    def add_reward(self, user_id, reward):
        reward['user_id'] = user_id
        self.rewards.insert_one(reward)

    def get_user_transactions(self, user_id):
        return list(self.transactions.find({'user_id': user_id}))

    def get_user_rewards(self, user_id):
        return list(self.rewards.find({'user_id': user_id}))

    def update_user_score(self, user_id, score):
        self.users.update_one(
            {'_id': user_id},
            {'$set': {'greenscore': score}},
            upsert=True
        )

    def initialize_user(self, username):
        user = self.users.find_one({'username': username})
        if not user:
            self.users.insert_one({
                'username': username,
                'greenscore': 0,
                'created_at': datetime.now()
            })
            return True
        return False
