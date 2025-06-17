class Gamification:
    def __init__(self):
        # Carbon impact factors (kg CO2 per unit)
        self.carbon_factors = {
            'transport': 0.2,  # kg CO2 per km
            'diet': {
                'vegetarian': 2.5,  # kg CO2 per day
                'pescatarian': 3.5,  # kg CO2 per day
                'omnivore': 4.5     # kg CO2 per day
            },
            'energy': 0.5,  # kg CO2 per kWh
            'shopping': 0.1  # kg CO2 per $100
        }
        
        # Points calculation factors
        self.points_factors = {
            'transport': 1,  # points per kg CO2 saved
            'diet': 2,      # points per kg CO2 saved
            'energy': 1.5,  # points per kg CO2 saved
            'shopping': 0.5 # points per kg CO2 saved
        }
        
        # Initialize badges and challenges
        self.badges = {
            'no_meat': {
                'name': 'Herbivore Hero',
                'description': 'No meat consumption for a week',
                'points': 100,
                'icon': '🌱'
            },
            'bike_commute': {
                'name': 'Bike Champion',
                'description': 'Biked to work 5 times in a week',
                'points': 150,
                'icon': '🚴‍♂️'
            },
            'public_transport': {
                'name': 'Public Transit Pro',
                'description': 'Used public transport for 10+ trips',
                'points': 200,
                'icon': '🚌'
            },
            'zero_waste': {
                'name': 'Zero Waste Warrior',
                'description': 'Achieved zero waste for a day',
                'points': 120,
                'icon': '🗑️'
            }
        }
        
        self.challenges = {
            'weekly_bike': {
                'name': 'Bike to Work',
                'description': 'Bike to work 5 times this week',
                'target': 5,
                'category': 'transport',
                'points': 150,
                'icon': '🚴‍♂️'
            },
            'no_meat_week': {
                'name': 'Meatless Week',
                'description': 'No meat consumption for 7 days',
                'target': 7,
                'category': 'food',
                'points': 200,
                'icon': '🥗'
            },
            'daily_recycling': {
                'name': 'Recycling Pro',
                'description': 'Recycle every day for a week',
                'target': 7,
                'category': 'utilities',
                'points': 180,
                'icon': '♻️'
            }
        }

    def calculate_carbon_impact(self, transport: float, diet: str, energy: float, shopping: float) -> float:
        """Calculate carbon impact based on user inputs"""
        impact = (
            transport * self.carbon_factors['transport'] +
            self.carbon_factors['diet'][diet] +
            energy * self.carbon_factors['energy'] +
            (shopping / 100) * self.carbon_factors['shopping']
        )
        return impact

    def calculate_points(self, carbon_impact: float, category: str = 'mixed') -> int:
        """Calculate points based on carbon impact and category"""
        if category == 'mixed':
            return int(carbon_impact * sum(self.points_factors.values()) / len(self.points_factors))
        return int(carbon_impact * self.points_factors.get(category, 1))

    def check_badges(self, user_id, transactions):
        """Check if user qualifies for any badges"""
        badges_earned = []
        
        # Check for no meat badge
        food_transactions = transactions[transactions['category'] == 'food']
        if len(food_transactions) > 0 and not any('meat' in desc.lower() for desc in food_transactions['description']):
            badges_earned.append('no_meat')
        
        # Check for bike badge
        transport_transactions = transactions[transactions['category'] == 'transport']
        bike_count = sum('bike' in desc.lower() for desc in transport_transactions['description'])
        if bike_count >= 5:
            badges_earned.append('bike_commute')
        
        return badges_earned

    def get_active_challenges(self):
        """Get all active challenges"""
        return list(self.challenges.values())

    def check_challenge_progress(self, user_id, transactions):
        """Check progress for all challenges"""
        progress = {}
        
        for challenge_id, challenge in self.challenges.items():
            relevant_transactions = transactions[transactions['category'] == challenge['category']]
            count = len(relevant_transactions)
            
            progress[challenge_id] = {
                'name': challenge['name'],
                'description': challenge['description'],
                'current': count,
                'target': challenge['target'],
                'progress': (count / challenge['target']) * 100,
                'icon': challenge['icon']
            }
        
        return progress
