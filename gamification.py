from typing import List, Dict
import random
from datetime import datetime, timedelta
import math
import pandas as pd

class GamificationEngine:
    def __init__(self):
        self.levels = [
            {'name': 'Eco Newbie', 'min_score': 0, 'max_score': 1499, 'color': '#888888'},
            {'name': 'Green Warrior', 'min_score': 1500, 'max_score': 3499, 'color': '#2ed573'},
            {'name': 'Carbon Crusher', 'min_score': 3500, 'max_score': 6999, 'color': '#00d4ff'},
            {'name': 'Sustainability Hero', 'min_score': 7000, 'max_score': 12999, 'color': '#9b59b6'},
            {'name': 'Planet Protector', 'min_score': 13000, 'max_score': float('inf'), 'color': '#f39c12'}
        ]
        
        self.weekly_challenges = [
            {
                'id': 'public_transport_week',
                'title': 'Public Transport Champion',
                'description': 'Use public transportation for 70% of your trips this week',
                'reward': 750,
                'type': 'transportation',
                'difficulty': 'Medium',
                'target_metric': 'public_transport_percentage',
                'target_value': 70
            },
            {
                'id': 'meatless_meals',
                'title': 'Plant-Based Pioneer',
                'description': 'Eat 8 plant-based meals this week',
                'reward': 500,
                'type': 'food',
                'difficulty': 'Easy',
                'target_metric': 'plant_based_meals',
                'target_value': 8
            },
            {
                'id': 'energy_reduction',
                'title': 'Energy Efficiency Expert',
                'description': 'Reduce energy consumption by 15% compared to last week',
                'reward': 600,
                'type': 'energy',
                'difficulty': 'Medium',
                'target_metric': 'energy_reduction_percentage',
                'target_value': 15
            },
            {
                'id': 'local_shopping',
                'title': 'Local Economy Supporter',
                'description': 'Make 5 purchases from local businesses this week',
                'reward': 400,
                'type': 'shopping',
                'difficulty': 'Easy',
                'target_metric': 'local_purchases',
                'target_value': 5
            },
            {
                'id': 'zero_waste_day',
                'title': 'Zero Waste Warrior',
                'description': 'Have 3 zero-waste days this week',
                'reward': 800,
                'type': 'lifestyle',
                'difficulty': 'Hard',
                'target_metric': 'zero_waste_days',
                'target_value': 3
            },
            {
                'id': 'bike_commute',
                'title': 'Pedal Power',
                'description': 'Bike or walk for 5 trips instead of driving',
                'reward': 650,
                'type': 'transportation',
                'difficulty': 'Medium',
                'target_metric': 'active_transport_trips',
                'target_value': 5
            },
            {
                'id': 'energy_audit',
                'title': 'Home Energy Detective',
                'description': 'Complete a home energy audit and implement 3 improvements',
                'reward': 900,
                'type': 'energy',
                'difficulty': 'Hard',
                'target_metric': 'energy_improvements',
                'target_value': 3
            }
        ]
        
        self.achievements = [
            {
                'id': 'first_steps',
                'name': 'First Steps',
                'description': 'Logged your first carbon activity',
                'icon': '👶',
                'points': 100,
                'rarity': 'Common',
                'unlock_condition': {'transactions': 1}
            },
            {
                'id': 'week_warrior',
                'name': 'Week Warrior',
                'description': 'Tracked activities for 7 consecutive days',
                'icon': '⚡',
                'points': 300,
                'rarity': 'Common',
                'unlock_condition': {'streak_days': 7}
            },
            {
                'id': 'month_master',
                'name': 'Month Master',
                'description': 'Tracked activities for 30 consecutive days',
                'icon': '📅',
                'points': 800,
                'rarity': 'Rare',
                'unlock_condition': {'streak_days': 30}
            },
            {
                'id': 'carbon_crusher',
                'name': 'Carbon Crusher',
                'description': 'Reduced monthly emissions by 25%',
                'icon': '💪',
                'points': 1000,
                'rarity': 'Rare',
                'unlock_condition': {'carbon_reduction_percentage': 25}
            },
            {
                'id': 'tree_hugger',
                'name': 'Tree Hugger',
                'description': 'Saved the equivalent of 50 trees worth of CO₂',
                'icon': '🌳',
                'points': 1500,
                'rarity': 'Epic',
                'unlock_condition': {'co2_saved_kg': 1100}  # 50 trees * 22kg CO2/tree/year
            },
            {
                'id': 'efficiency_expert',
                'name': 'Efficiency Expert',
                'description': 'Achieved carbon efficiency of <0.2 kg CO₂ per dollar',
                'icon': '🎯',
                'points': 1200,
                'rarity': 'Epic',
                'unlock_condition': {'carbon_efficiency': 0.2}
            },
            {
                'id': 'green_machine',
                'name': 'Green Machine',
                'description': 'Completed 10 weekly challenges',
                'icon': '🤖',
                'points': 2000,
                'rarity': 'Legendary',
                'unlock_condition': {'challenges_completed': 10}
            },
            {
                'id': 'planet_protector',
                'name': 'Planet Protector',
                'description': 'Saved 1000kg of CO₂ equivalent',
                'icon': '🛡️',
                'points': 2500,
                'rarity': 'Legendary',
                'unlock_condition': {'co2_saved_kg': 1000}
            },
            {
                'id': 'influence_master',
                'name': 'Influence Master',
                'description': 'Inspired 5 friends to join CarbonTrace',
                'icon': '👥',
                'points': 1800,
                'rarity': 'Epic',
                'unlock_condition': {'referrals': 5}
            },
            {
                'id': 'data_champion',
                'name': 'Data Champion',
                'description': 'Logged 100 transactions',
                'icon': '📊',
                'points': 600,
                'rarity': 'Rare',
                'unlock_condition': {'transactions': 100}
            }
        ]
    
    def calculate_score(self, user_id: str, transactions: List[Dict], user_stats: Dict = None) -> float:
        """Calculate comprehensive user score based on multiple factors"""
        if not transactions:
            return 1000  # Starting score
        
        base_score = 1000
        
        # Factor 1: Carbon efficiency (CO2 per dollar spent)
        total_spent = sum(t.get('amount', 0) for t in transactions)
        total_carbon = sum(t.get('carbon_kg', 0) for t in transactions)
        
        if total_spent > 0:
            carbon_efficiency = total_carbon / total_spent
            # Reward lower carbon per dollar (better efficiency)
            efficiency_score = max(0, (0.5 - carbon_efficiency) * 2000)
            base_score += efficiency_score
        
        # Factor 2: Absolute carbon reduction
        if user_stats:
            target_carbon = user_stats.get('monthly_target_kg', 500)
            if total_carbon < target_carbon:
                reduction_bonus = (target_carbon - total_carbon) * 2
                base_score += reduction_bonus
        
        # Factor 3: Category-specific bonuses
        category_bonuses = {
            'Transportation': self._calculate_transport_bonus(transactions),
            'Food': self._calculate_food_bonus(transactions),
            'Energy': self._calculate_energy_bonus(transactions),
            'Shopping': self._calculate_shopping_bonus(transactions)
        }
        
        total_bonus = sum(category_bonuses.values())
        
        # Factor 4: Consistency bonus (streak days)
        if user_stats:
            streak_days = user_stats.get('streak_days', 0)
            consistency_bonus = min(streak_days * 10, 500)  # Max 500 points for consistency
            base_score += consistency_bonus
        
        # Factor 5: Achievement multiplier
        if user_stats:
            achievements_count = len(user_stats.get('achievements', []))
            achievement_multiplier = 1 + (achievements_count * 0.05)  # 5% bonus per achievement
            base_score *= achievement_multiplier
        
        return base_score + total_bonus
    
    def _calculate_transport_bonus(self, transactions: List[Dict]) -> float:
        """Calculate transportation-specific bonuses"""
        transport_transactions = [t for t in transactions if t['category'] == 'Transportation']
        if not transport_transactions:
            return 0
        
        bonus = 0
        for t in transport_transactions:
            subcategory = t.get('subcategory', '').lower()
            carbon_per_dollar = t.get('carbon_kg', 0) / max(t.get('amount', 1), 1)
            
            # Bonus for low-carbon transportation
            if any(keyword in subcategory for keyword in ['public', 'bus', 'train', 'subway']):
                bonus += 75
            elif any(keyword in subcategory for keyword in ['electric', 'hybrid']):
                bonus += 50
            elif any(keyword in subcategory for keyword in ['bike', 'walk']):
                bonus += 100
            elif carbon_per_dollar > 0.6:  # Penalty for high-carbon transport
                bonus -= 25
        
        return bonus
    
    def _calculate_food_bonus(self, transactions: List[Dict]) -> float:
        """Calculate food-specific bonuses"""
        food_transactions = [t for t in transactions if t['category'] == 'Food']
        if not food_transactions:
            return 0
        
        bonus = 0
        for t in food_transactions:
            subcategory = t.get('subcategory', '').lower()
            carbon_per_dollar = t.get('carbon_kg', 0) / max(t.get('amount', 1), 1)
            
            # Bonus for sustainable food choices
            if any(keyword in subcategory for keyword in ['organic', 'local', 'plant', 'vegetarian', 'vegan']):
                bonus += 40
            elif any(keyword in subcategory for keyword in ['beef', 'lamb']) and carbon_per_dollar > 3:
                bonus -= 30  # Penalty for high-carbon meat
            elif carbon_per_dollar < 1.5:  # Bonus for low-carbon food choices
                bonus += 20
        
        return bonus
    
    def _calculate_energy_bonus(self, transactions: List[Dict]) -> float:
        """Calculate energy-specific bonuses"""
        energy_transactions = [t for t in transactions if t['category'] == 'Energy']
        if not energy_transactions:
            return 0
        
        bonus = 0
        for t in energy_transactions:
            subcategory = t.get('subcategory', '').lower()
            carbon_per_dollar = t.get('carbon_kg', 0) / max(t.get('amount', 1), 1)
            
            # Bonus for renewable energy
            if any(keyword in subcategory for keyword in ['renewable', 'solar', 'wind']):
                bonus += 150
            elif carbon_per_dollar < 0.3:  # Efficient energy use
                bonus += 50
        
        return bonus
    
    def _calculate_shopping_bonus(self, transactions: List[Dict]) -> float:
        """Calculate shopping-specific bonuses"""
        shopping_transactions = [t for t in transactions if t['category'] == 'Shopping']
        if not shopping_transactions:
            return 0
        
        bonus = 0
        for t in shopping_transactions:
            subcategory = t.get('subcategory', '').lower()
            carbon_per_dollar = t.get('carbon_kg', 0) / max(t.get('amount', 1), 1)
            
            # Bonus for sustainable shopping
            if any(keyword in subcategory for keyword in ['sustainable', 'local', 'secondhand', 'refurbished']):
                bonus += 35
            elif carbon_per_dollar < 0.3:  # Low-carbon purchases
                bonus += 15
        
        return bonus
    
    def get_user_level(self, score: float) -> Dict:
        """Get user's current level based on score"""
        for level in self.levels:
            if level['min_score'] <= score <= level['max_score']:
                # Add progress to next level
                if level != self.levels[-1]:  # Not the highest level
                    next_level = next(l for l in self.levels if l['min_score'] > level['min_score'])
                    progress = (score - level['min_score']) / (next_level['min_score'] - level['min_score'])
                    level['progress_to_next'] = min(progress, 1.0)
                    level['points_to_next'] = max(0, next_level['min_score'] - score)
                else:
                    level['progress_to_next'] = 1.0
                    level['points_to_next'] = 0
                
                return level
        
        return self.levels[-1]  # Return highest level if score exceeds all ranges
    
    def get_weekly_challenges(self, user_stats: Dict = None) -> List[Dict]:
        """Get personalized weekly challenges based on user behavior"""
        if not user_stats:
            return random.sample(self.weekly_challenges, 3)
        
        # Analyze user's weak areas and suggest relevant challenges
        available_challenges = self.weekly_challenges.copy()
        
        # Prioritize challenges based on user's carbon footprint patterns
        # This would be enhanced with actual user data analysis
        
        return random.sample(available_challenges, 3)
    
    def check_achievements(self, user_stats: Dict, transactions: List[Dict]) -> List[Dict]:
        """Check which achievements the user has unlocked"""
        unlocked_achievements = []
        current_achievements = user_stats.get('achievements', [])
        
        for achievement in self.achievements:
            if achievement['id'] in [a.get('id', a) if isinstance(a, dict) else a for a in current_achievements]:
                continue  # Already unlocked
            
            # Check unlock conditions
            conditions_met = True
            for condition, required_value in achievement['unlock_condition'].items():
                
                if condition == 'transactions':
                    if len(transactions) < required_value:
                        conditions_met = False
                        break
                
                elif condition == 'streak_days':
                    if user_stats.get('streak_days', 0) < required_value:
                        conditions_met = False
                        break
                
                elif condition == 'carbon_reduction_percentage':
                    # Calculate reduction compared to baseline or target
                    target = user_stats.get('monthly_target_kg', 500)
                    current = sum(t.get('carbon_kg', 0) for t in transactions[-30:])  # Last 30 transactions
                    if target > 0:
                        reduction = ((target - current) / target) * 100
                        if reduction < required_value:
                            conditions_met = False
                            break
                
                elif condition == 'co2_saved_kg':
                    if user_stats.get('co2_saved_kg', 0) < required_value:
                        conditions_met = False
                        break
                
                elif condition == 'carbon_efficiency':
                    if transactions:
                        total_spent = sum(t.get('amount', 0) for t in transactions)
                        total_carbon = sum(t.get('carbon_kg', 0) for t in transactions)
                        if total_spent > 0:
                            efficiency = total_carbon / total_spent
                            if efficiency > required_value:  # Lower is better for efficiency
                                conditions_met = False
                                break
                
                # Add more condition checks as needed
            
            if conditions_met:
                unlocked_achievements.append(achievement)
        
        return unlocked_achievements
    
    def calculate_environmental_impact(self, transactions: List[Dict]) -> Dict:
        """Calculate real-world environmental impact metrics"""
        total_carbon = sum(t.get('carbon_kg', 0) for t in transactions)
        
        # Conversion factors based on scientific data
        impact_metrics = {
            'trees_equivalent': total_carbon / 22,  # Average tree absorbs 22kg CO2/year
            'car_miles_equivalent': total_carbon / 0.404,  # Average car emits 0.404 kg CO2/mile
            'home_energy_days': total_carbon / (877 * 0.5 / 365),  # Average US home energy per day
            'flights_avoided': total_carbon / 90,  # Rough estimate for short domestic flight
            'plastic_bottles_equivalent': total_carbon / 0.082,  # CO2 from plastic bottle production
            'gasoline_gallons_equivalent': total_carbon / 8.89,  # CO2 from burning 1 gallon gasoline
        }
        
        return {k: max(0, v) for k, v in impact_metrics.items()}
    
    def get_personalized_tips(self, transactions: List[Dict], user_stats: Dict) -> List[Dict]:
        """Generate personalized eco-tips based on user behavior"""
        tips = []
        
        if not transactions:
            return [
                {
                    'title': 'Start Your Journey',
                    'description': 'Begin by logging your daily activities to understand your carbon footprint.',
                    'category': 'general',
                    'difficulty': 'easy',
                    'impact': 'high'
                }
            ]
        
        # Analyze user's highest impact categories
        df = pd.DataFrame(transactions)
        category_totals = df.groupby('category')['carbon_kg'].sum().sort_values(ascending=False)
        
        top_category = category_totals.index[0] if len(category_totals) > 0 else 'general'
        
        category_tips = {
            'Transportation': [
                {
                    'title': 'Try Car-Free Days',
                    'description': 'Designate one day per week as car-free. Walk, bike, or use public transit.',
                    'category': 'transportation',
                    'difficulty': 'medium',
                    'impact': 'high'
                },
                {
                    'title': 'Combine Your Errands',
                    'description': 'Plan your trips to combine multiple errands into one outing.',
                    'category': 'transportation',
                    'difficulty': 'easy',
                    'impact': 'medium'
                }
            ],
            'Food': [
                {
                    'title': 'Meatless Monday',
                    'description': 'Try replacing meat with plant-based proteins one day per week.',
                    'category': 'food',
                    'difficulty': 'easy',
                    'impact': 'high'
                },
                {
                    'title': 'Shop Local and Seasonal',
                    'description': 'Choose locally grown, seasonal produce to reduce transportation emissions.',
                    'category': 'food',
                    'difficulty': 'easy',
                    'impact': 'medium'
                }
            ],
            'Energy': [
                {
                    'title': 'Adjust Your Thermostat',
                    'description': 'Lower heating by 2°F in winter and raise cooling by 2°F in summer.',
                    'category': 'energy',
                    'difficulty': 'easy',
                    'impact': 'medium'
                },
                {
                    'title': 'Unplug Electronics',
                    'description': 'Unplug devices when not in use to eliminate phantom energy draw.',
                    'category': 'energy',
                    'difficulty': 'easy',
                    'impact': 'low'
                }
            ]
        }
        
        # Return tips for the user's highest impact category
        return category_tips.get(top_category, [
            {
                'title': 'Track Consistently',
                'description': 'Regular tracking helps identify patterns and opportunities for improvement.',
                'category': 'general',
                'difficulty': 'easy',
                'impact': 'medium'
            }
        ])
