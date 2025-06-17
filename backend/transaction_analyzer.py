import pandas as pd
import datetime
from random import choice

class TransactionAnalyzer:
    def __init__(self):
        # Define categories and their keywords
        self.categories = {
            'transport': ['uber', 'lyft', 'taxi', 'bus', 'train'],
            'food': ['starbucks', 'coffee', 'restaurant', 'grocery'],
            'utilities': ['electricity', 'water', 'gas', 'bill'],
            'shopping': ['amazon', 'walmart', 'target'],
            'other': ['miscellaneous']
        }

    def get_recent_transactions(self, num_transactions=10):
        """Generate mock transactions"""
        transactions = []
        today = datetime.date.today()
        
        for i in range(num_transactions):
            date = today - datetime.timedelta(days=i)
            amount = round(random.uniform(10, 100), 2)
            description = self._generate_description()
            category = self.categorize_transaction(description)
            
            transactions.append({
                'date': date,
                'description': description,
                'amount': amount,
                'category': category
            })
        
        return pd.DataFrame(transactions)

    def categorize_transaction(self, description):
        """Categorize transaction based on keywords"""
        description = description.lower()
        
        for category, keywords in self.categories.items():
            if any(keyword in description for keyword in keywords):
                return category
        
        return 'other'

    def _generate_description(self):
        """Generate a random transaction description"""
        category = choice(list(self.categories.keys()))
        merchant = choice(self.categories[category])
        return f"Payment to {merchant}"

    def get_recent_transactions(self):
        # This would normally connect to Plaid API
        # For demo purposes, we'll return sample data
        sample_data = {
            'date': pd.date_range(start='2024-01-01', periods=10),
            'description': ['Uber Ride', 'Starbucks Coffee', 'Bus Fare', 'Electricity Bill', 'Groceries'],
            'amount': [15.0, 5.0, 2.5, 100.0, 50.0],
            'category': ['transport', 'food', 'transport', 'utilities', 'groceries']
        }
        return pd.DataFrame(sample_data)

    def categorize_transaction(self, description):
        doc = nlp(description)
        # Simple categorization based on keywords
        if any(token.text.lower() in ['uber', 'lyft', 'taxi'] for token in doc):
            return 'transport'
        elif any(token.text.lower() in ['electricity', 'energy'] for token in doc):
            return 'utilities'
        elif any(token.text.lower() in ['coffee', 'restaurant'] for token in doc):
            return 'food'
        return 'other'
