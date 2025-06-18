import pandas as pd
import re
from typing import List, Dict
import spacy
from datetime import datetime

class TransactionParser:
    def __init__(self):
        # Load spaCy model (install with: python -m spacy download en_core_web_sm)
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            print("spaCy model not found. Install with: python -m spacy download en_core_web_sm")
            self.nlp = None
        
        # Category keywords
        self.category_keywords = {
            'Food': ['grocery', 'restaurant', 'food', 'cafe', 'market', 'supermarket', 
                    'whole foods', 'safeway', 'kroger', 'mcdonalds', 'starbucks'],
            'Transportation': ['gas', 'fuel', 'uber', 'lyft', 'taxi', 'metro', 'bus',
                             'airline', 'flight', 'parking', 'toll', 'car wash'],
            'Energy': ['electric', 'utility', 'power', 'gas company', 'energy',
                      'pge', 'edison', 'utility bill'],
            'Shopping': ['amazon', 'target', 'walmart', 'mall', 'store', 'shop',
                        'clothing', 'fashion', 'electronics', 'best buy'],
            'Entertainment': ['movie', 'theater', 'netflix', 'spotify', 'gym',
                            'entertainment', 'games', 'concert', 'ticket']
        }
        
        # Subcategory patterns
        self.subcategory_patterns = {
            'meat': ['beef', 'chicken', 'pork', 'meat', 'butcher'],
            'dairy': ['milk', 'cheese', 'yogurt', 'dairy'],
            'organic': ['organic', 'whole foods', 'natural'],
            'gas': ['shell', 'chevron', 'exxon', 'bp', 'gas station'],
            'uber': ['uber', 'lyft', 'rideshare'],
            'flight': ['airline', 'flight', 'airport', 'delta', 'united'],
            'electricity': ['electric', 'power', 'utility'],
            'clothing': ['clothing', 'fashion', 'apparel', 'h&m', 'zara'],
            'electronics': ['electronics', 'best buy', 'apple', 'samsung']
        }
    
    def parse_transactions(self, df: pd.DataFrame, user_id: str) -> List[Dict]:
        """Parse bank transactions and categorize them"""
        transactions = []
        
        # Assume CSV has columns: date, description, amount
        for _, row in df.iterrows():
            description = str(row.get('description', '')).lower()
            amount = abs(float(row.get('amount', 0)))
            date = row.get('date', datetime.now().isoformat())
            
            if amount == 0:
                continue
            
            # Categorize transaction
            category = self._categorize_transaction(description)
            subcategory = self._get_subcategory(description)
            
            # Calculate carbon footprint
            from carbon_calculator import CarbonCalculator
            calculator = CarbonCalculator()
            carbon_kg = calculator.calculate_footprint(category, subcategory, amount)
            
            transaction = {
                'user_id': user_id,
                'date': date,
                'description': row.get('description', ''),
                'amount': amount,
                'category': category,
                'subcategory': subcategory,
                'carbon_kg': carbon_kg
            }
            
            transactions.append(transaction)
        
        return transactions
    
    def _categorize_transaction(self, description: str) -> str:
        """Categorize transaction based on description"""
        description = description.lower()
        
        # Check each category
        for category, keywords in self.category_keywords.items():
            for keyword in keywords:
                if keyword in description:
                    return category
        
        return 'Other'
    
    def _get_subcategory(self, description: str) -> str:
        """Get subcategory based on description patterns"""
        description = description.lower()
        
        for subcategory, patterns in self.subcategory_patterns.items():
            for pattern in patterns:
                if pattern in description:
                    return subcategory
        
        return ''
    
    def extract_entities(self, text: str) -> Dict:
        """Extract entities using spaCy NLP"""
        if not self.nlp:
            return {}
        
        doc = self.nlp(text)
        entities = {
            'organizations': [ent.text for ent in doc.ents if ent.label_ == 'ORG'],
            'money': [ent.text for ent in doc.ents if ent.label_ == 'MONEY'],
            'locations': [ent.text for ent in doc.ents if ent.label_ in ['GPE', 'LOC']]
        }
        
        return entities
