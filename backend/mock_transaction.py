import random
from datetime import datetime
from typing import List, Dict
import json
from dotenv import load_dotenv
import os

load_dotenv()

class MockTransaction:
    def __init__(self):
        self.categories = {
            'transport': ['Uber', 'Lyft', 'Taxi', 'Bus', 'Train'],
            'food': ['Starbucks', 'McDonalds', 'Restaurant', 'Grocery Store'],
            'utilities': ['Electricity', 'Water', 'Gas'],
            'shopping': ['Amazon', 'Walmart', 'Target'],
            'other': ['Miscellaneous']
        }

    def generate_mock_transaction(self, amount: float = None) -> Dict:
        """Generate a mock transaction"""
        category = random.choice(list(self.categories.keys()))
        merchant = random.choice(self.categories[category])
        
        if amount is None:
            if category == 'transport':
                amount = round(random.uniform(5, 50), 2)
            elif category == 'food':
                amount = round(random.uniform(5, 30), 2)
            elif category == 'utilities':
                amount = round(random.uniform(50, 200), 2)
            else:
                amount = round(random.uniform(10, 100), 2)

        return {
            'id': f"tx_{random.randint(100000, 999999)}",
            'date': datetime.now().isoformat(),
            'description': f"Payment to {merchant}",
            'amount': amount,
            'category': category,
            'pending': False
        }

    def generate_mock_transactions(self, num_transactions: int = 10) -> List[Dict]:
        """Generate multiple mock transactions"""
        return [self.generate_mock_transaction() for _ in range(num_transactions)]

    def get_recent_transactions(self) -> List[Dict]:
        """Get recent transactions (simulates API call)"""
        return self.generate_mock_transactions()

    def add_transaction(self, transaction_data: Dict) -> Dict:
        """Add a new transaction"""
        transaction = {
            'id': f"tx_{random.randint(100000, 999999)}",
            'date': datetime.now().isoformat(),
            **transaction_data
        }
        return transaction
