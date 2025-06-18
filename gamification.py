from typing import List, Dict
import random
from datetime import datetime, timedelta

class GamificationEngine:
    def __init__(self):
        self.levels = [
            {'name': 'Eco Newbie', 'min_score': 0, 'max_score': 999},
            {'name': 'Green Warrior', 'min_score': 1000, 'max_score': 2499},
            {'name': 'Carbon Crusher', 'min_score': 2500, 'max_score': 4999},
            {'name': 'Sustainability Hero', 'min_score': 5000, 'max_score': 9999},
            {'name': 'Planet Protector', 'min_score': 10000, 'max_score': float('inf')}
        ]
        
        self.weekly_challenges = [
            {
                'id': 'public_transport',
                'title': 'Public Transport Week',
                'description': 'Use public transportation for 5 trips this week',
                'reward': 500,
                'type': 'transportation'
            },
            {
                'id': 'meatless_meals',
                'title': 'Meatless Monday to Friday',
                'description': 'Have 5 plant-based meals this week',
                'reward': 300,
                'type': 'food'
            },
            {
                'id': 'energy_saver',
                'title': 'Energy Saver Challenge',
                'description': 'Reduce energy consumption by 20% this week',
                'reward': 400,
                'type': 'energy'
            },
            {
                'id': 'local_shopping',
                'title': 'Shop Local',
                'description': 'Make 3 purchases from local businesses',
                'reward': 250,
                'type': 'shopping'
            }
        ]
    
    def calculate_score(self, user_id: str, transactions: List[Dict]) -> float:
        """Calculate user's GreenScore based on transactions"""
        if not transactions:
            return 1000  # Starting score
        
        base_score = 1000
        
        # Calculate carbon efficiency score
        total_spent = sum(t['amount'] for t in transactions)
        total_carbon = sum(t['carbon_kg'] for t in transactions)
        
        if total_spent > 0:
            carbon_efficiency = total_carbon / total_spent
            # Lower carbon per dollar = higher score
            efficiency_bonus = max(0, (0.5 - carbon_efficiency) * 1000)
            base_score += efficiency_bonus
        
        # Bonus for low-carbon categories
        category_bonuses = {
            'Transportation': self._calculate_transport_bonus(transactions),
            'Food': self._calculate_food_bonus(transactions),
            'Energy': self._calculate_energy_bonus(transactions)
        }
        
        total_bonus = sum(category_bonuses.values())
        
        return base_score + total_bonus
    
    def _calculate_transport_bonus(self, transactions: List[Dict]) -> float:
        """Calculate bonus for sustainable transportation choices"""
        transport_transactions = [t for t in transactions if t['category'] == 'Transportation']
        if not transport_transactions:
            return 0
        
        bonus = 0
        for t in transport_transactions:
            if 'public' in t.get('subcategory', '').lower():
                bonus += 50
            elif 'electric' in t.get('subcategory', '').lower():
                bonus += 30
            elif 'uber' in t.get('subcategory', '').lower():
                bonus -= 10  # Penalty for ride-sharing
        
        return bonus
    
    def _calculate_food_bonus(self, transactions: List[Dict]) -> float:
        """Calculate bonus for sustainable food choices"""
        food_transactions = [t for t in transactions if t['category'] == 'Food']
        if not food_transactions:
            return 0
        
        bonus = 0
        for t in food_transactions:
            subcategory = t.get('subcategory', '').lower()
            if 'organic' in subcategory:
                bonus += 25
            elif 'local' in subcategory:
                bonus += 20
            elif 'meat' in subcategory:
                bonus -= 15  # Penalty for high-carbon foods
        
        return bonus
    
    def _calculate_energy_bonus(self, transactions: List[Dict]) -> float:
        """Calculate bonus for sustainable energy choices"""
        energy_transactions = [t for t in transactions if t['category'] == 'Energy']
        if not energy_transactions:
            return 0
        
        bonus = 0
        for t in energy_transactions:
            if 'renewable' in t.get('subcategory', '').lower():
                bonus += 100
        
        return bonus
    
    def get_user_level(self, score: float) -> Dict:
        """Get user's current level based on score"""
        for level in self.levels:
            if level['min_score'] <= score <= level['max_score']:
                return level
        return self.levels[-1]  # Return highest level if score exceeds all ranges
    
    def get_score_change(self, user_id: str) -> int:
        """Get recent score change (mock implementation)"""
        return random.randint(-50, 100)
    
    def get_weekly_challenges(self) -> List[Dict]:
        """Get current weekly challenges"""
        return random.sample(self.weekly_challenges, 3)
    
    def create_goal(self, user_id: str, goal_type: str, target: float) -> Dict:
        """Create a new user goal"""
        goal_templates = {
            'Reduce Monthly Footprint': {
                'title': f'Reduce Monthly Footprint by {target}%',
                'target': target,
                'current': 0,
                'unit': '%',
                'reward': f'{int(target * 10)} points'
            },
            'Use Public Transport': {
                'title': f'Use Public Transport {target} times',
                'target': target,
                'current': 0,
                'unit': 'trips',
                'reward': f'{int(target * 25)} points'
            },
            'Plant Trees': {
                'title': f'Plant {target} trees',
                'target': target,
                'current': 0,
                'unit': 'trees',
                'reward': f'{int(target * 50)} points + tree certificate'
            }
        }
        
        goal = goal_templates.get(goal_type, goal_templates['Reduce Monthly Footprint'])
        goal['user_id'] = user_id
        goal['type'] = goal_type
        goal['created_at'] = datetime.now()
        
        return goal
    
    def join_challenge(self, user_id: str, challenge_id: str):
        """Join a weekly challenge"""
        # In a real app, this would update the database
        print(f"User {user_id} joined challenge {challenge_id}")
    
    def get_global_leaderboard(self) -> List[Dict]:
        """Get global leaderboard (mock data)"""
        return [
            {'username': 'EcoChampion', 'score': 8500, 'footprint_reduction': 45.2},
            {'username': 'GreenGuru', 'score': 7800, 'footprint_reduction': 38.7},
            {'username': 'CarbonCrusher', 'score': 7200, 'footprint_reduction': 35.1},
            {'username': 'PlanetSaver', 'score': 6900, 'footprint_reduction': 32.8},
            {'username': 'EcoWarrior', 'score': 6500, 'footprint_reduction': 29.4},
            {'username': 'GreenMachine', 'score': 6100, 'footprint_reduction': 27.3},
            {'username': 'SustainabilityPro', 'score': 5800, 'footprint_reduction': 25.6},
            {'username': 'ClimateHero', 'score': 5400, 'footprint_reduction': 23.1},
            {'username': 'EcoFriendly', 'score': 5000, 'footprint_reduction': 20.8},
            {'username': 'GreenLiving', 'score': 4700, 'footprint_reduction': 18.9}
        ]
