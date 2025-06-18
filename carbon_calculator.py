import pandas as pd
from typing import List, Dict

class CarbonCalculator:
    def __init__(self):
        # Carbon emission factors (kg CO2 per dollar spent)
        self.emission_factors = {
            'Food': {
                'default': 0.5,
                'meat': 2.5,
                'dairy': 1.2,
                'organic': 0.3,
                'local': 0.2,
                'processed': 0.8
            },
            'Transportation': {
                'default': 0.4,
                'gas': 2.3,
                'uber': 0.6,
                'flight': 5.0,
                'public_transport': 0.1,
                'electric': 0.1
            },
            'Energy': {
                'default': 0.7,
                'electricity': 0.8,
                'gas_bill': 1.2,
                'renewable': 0.1
            },
            'Shopping': {
                'default': 0.3,
                'clothing': 0.5,
                'electronics': 0.8,
                'furniture': 0.4,
                'books': 0.1
            },
            'Entertainment': {
                'default': 0.2,
                'streaming': 0.05,
                'movies': 0.1,
                'concerts': 0.3
            },
            'Other': {
                'default': 0.3
            }
        }
    
    def calculate_footprint(self, category: str, subcategory: str, amount: float) -> float:
        """Calculate carbon footprint for a transaction"""
        category_factors = self.emission_factors.get(category, {'default': 0.3})
        
        if subcategory and subcategory.lower() in category_factors:
            factor = category_factors[subcategory.lower()]
        else:
            factor = category_factors['default']
        
        return amount * factor
    
    def get_recommendations(self, transactions: List[Dict]) -> List[Dict]:
        """Generate personalized recommendations based on transaction history"""
        if not transactions:
            return []
        
        df = pd.DataFrame(transactions)
        category_spending = df.groupby('category').agg({
            'amount': 'sum',
            'carbon_kg': 'sum'
        }).reset_index()
        
        recommendations = []
        
        # High carbon categories
        high_carbon = category_spending.nlargest(3, 'carbon_kg')
        
        for _, row in high_carbon.iterrows():
            category = row['category']
            carbon = row['carbon_kg']
            amount = row['amount']
            
            if category == 'Transportation' and carbon > 50:
                recommendations.append({
                    'id': f'transport_{category}',
                    'title': 'Switch to Public Transportation',
                    'description': 'You could reduce your carbon footprint by using public transport more often.',
                    'cost_savings': amount * 0.3,
                    'carbon_savings': carbon * 0.6,
                    'details': 'Public transportation produces 95% less CO2 than driving alone.'
                })
            
            elif category == 'Food' and carbon > 30:
                recommendations.append({
                    'id': f'food_{category}',
                    'title': 'Try Plant-Based Alternatives',
                    'description': 'Reducing meat consumption can significantly lower your food carbon footprint.',
                    'cost_savings': amount * 0.1,
                    'carbon_savings': carbon * 0.4,
                    'details': 'Plant-based proteins produce 90% less emissions than beef.'
                })
            
            elif category == 'Energy' and carbon > 40:
                recommendations.append({
                    'id': f'energy_{category}',
                    'title': 'Switch to Renewable Energy',
                    'description': 'Consider switching to a renewable energy provider.',
                    'cost_savings': amount * 0.05,
                    'carbon_savings': carbon * 0.8,
                    'details': 'Renewable energy can reduce your home emissions by up to 80%.'
                })
        
        return recommendations[:5]  # Return top 5 recommendations
