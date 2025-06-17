class RecommendationEngine:
    def __init__(self):
        self.recommendations = {
            'transport': [
                "Consider using public transport instead of ridesharing",
                "Carpool with colleagues or friends",
                "Use a bike for short distances"
            ],
            'food': [
                "Reduce meat consumption",
                "Buy local and seasonal produce",
                "Reduce food waste"
            ],
            'utilities': [
                "Switch to energy-efficient appliances",
                "Use LED light bulbs",
                "Install a smart thermostat"
            ],
            'groceries': [
                "Buy in bulk to reduce packaging",
                "Choose products with minimal packaging",
                "Support eco-friendly brands"
            ]
        }

    def get_recommendations(self, transactions=None):
        """Get personalized recommendations based on transactions"""
        if transactions is None:
            # Return general recommendations
            return [
                "Consider using public transport instead of ridesharing",
                "Switch to energy-efficient appliances",
                "Reduce meat consumption"
            ]

        # Analyze transactions and generate specific recommendations
        recommendations = []
        categories = transactions['category'].unique()
        
        for category in categories:
            if category in self.recommendations:
                recommendations.extend(self.recommendations[category])
                
        return list(set(recommendations))[:3]  # Return unique recommendations
