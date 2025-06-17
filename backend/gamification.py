class Gamification:
    def __init__(self):
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
