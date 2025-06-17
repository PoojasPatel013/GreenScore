class CarbonCalculator:
    def __init__(self):
        # Average carbon emissions factors (kg CO2e)
        self.emission_factors = {
            'transport': 0.2,  # kg CO2e per dollar
            'utilities': 0.05,  # kg CO2e per dollar
            'food': 0.1,  # kg CO2e per dollar
            'groceries': 0.08,  # kg CO2e per dollar
            'other': 0.03  # kg CO2e per dollar
        }

    def calculate_footprint(self, transaction):
        """Calculate carbon footprint for a single transaction."""
        category = transaction.get('category', 'other')
        amount = transaction.get('amount', 0)
        
        if category in self.emission_factors:
            return amount * self.emission_factors[category]
        return amount * self.emission_factors['other']

    def calculate_weekly_footprint(self, transactions):
        """Calculate total weekly carbon footprint."""
        weekly_footprint = 0
        for _, transaction in transactions.iterrows():
            weekly_footprint += self.calculate_footprint(transaction)
        return weekly_footprint

    def get_carbon_offset_recommendation(self, footprint):
        """Get recommendation for carbon offset."""
        # Simple recommendation based on footprint
        if footprint < 10:
            return "Great job! Your footprint is low."
        elif footprint < 50:
            return "Consider planting 1 tree this month."
        else:
            return "Consider planting 2 trees this month."
