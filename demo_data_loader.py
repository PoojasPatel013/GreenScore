
import pandas as pd
import json
from pathlib import Path
from datetime import datetime, timedelta
import random

class DemoDataLoader:
    def __init__(self):
        self.data_dir = Path("training_data")
        
    def load_sample_transactions(self):
        """Load sample transactions for demo"""
        
        sample_file = self.data_dir / "sample_transactions.csv"
        if sample_file.exists():
            return pd.read_csv(sample_file)
        else:
            return self.generate_demo_transactions()
    
    def generate_demo_transactions(self):
        """Generate demo transactions on the fly"""
        
        transactions = []
        
        # Demo transaction patterns
        demo_transactions = [
            {"description": "Shell Gas Station #1234", "amount": 45.67, "category": "Transportation", "carbon_kg": 36.5},
            {"description": "Starbucks Coffee", "amount": 12.50, "category": "Food", "carbon_kg": 3.8},
            {"description": "PG&E Electric Bill", "amount": 125.00, "category": "Energy", "carbon_kg": 50.0},
            {"description": "Amazon Purchase", "amount": 89.99, "category": "Shopping", "carbon_kg": 18.0},
            {"description": "Netflix Subscription", "amount": 15.99, "category": "Entertainment", "carbon_kg": 0.2},
            {"description": "Uber Ride", "amount": 23.45, "category": "Transportation", "carbon_kg": 11.7},
            {"description": "Whole Foods Grocery", "amount": 67.89, "category": "Food", "carbon_kg": 10.2},
            {"description": "Best Buy Electronics", "amount": 299.99, "category": "Shopping", "carbon_kg": 60.0},
        ]
        
        for i, base_transaction in enumerate(demo_transactions * 10):  # Repeat for more data
            transaction = base_transaction.copy()
            transaction.update({
                "id": i,
                "date": (datetime.now() - timedelta(days=random.randint(0, 30))).strftime('%Y-%m-%d'),
                "confidence": random.uniform(0.8, 1.0),
                "user_id": "demo_user"
            })
            transactions.append(transaction)
        
        return pd.DataFrame(transactions)
    
    def get_demo_user_data(self):
        """Get demo user data"""
        
        return {
            "_id": "demo_user",
            "username": "EcoWarrior",
            "email": "demo@carbontrace.com",
            "created_at": datetime.now() - timedelta(days=30),
            "profile": {
                "first_name": "Demo",
                "last_name": "User",
                "bio": "Testing CarbonTrace!",
                "preferences": {
                    "units": "metric",
                    "notifications": True
                }
            },
            "stats": {
                "total_score": 7500,
                "co2_saved_kg": 125.5,
                "trees_equivalent": 5,
                "level": "Carbon Crusher",
                "achievements": ["First Steps", "Week Warrior", "Tree Planter"]
            },
            "settings": {
                "monthly_target_kg": 400,
                "currency": "USD",
                "timezone": "UTC"
            }
        }

# Global demo data loader instance
demo_loader = DemoDataLoader()
