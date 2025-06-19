import pandas as pd
from typing import List, Dict, Optional
import math

class CarbonCalculator:
    def __init__(self):
        # Updated emission factors based on EPA, IPCC, and scientific research
        # All values in kg CO2 equivalent per unit
        self.emission_factors = {
            'Transportation': {
                # Per mile driven
                'gasoline_car': 0.404,  # EPA average for passenger vehicles
                'diesel_car': 0.463,
                'hybrid_car': 0.200,
                'electric_car': 0.180,  # Varies by grid, US average
                'motorcycle': 0.280,
                'bus': 0.080,  # Per passenger mile
                'train': 0.060,  # Per passenger mile
                'subway': 0.040,  # Per passenger mile
                'taxi': 0.500,  # Higher due to empty miles
                'uber_lyft': 0.520,
                'flight_domestic': 0.255,  # Per passenger mile
                'flight_international': 0.195,  # More efficient per mile
                'default': 0.404
            },
            'Energy': {
                # Per kWh or per dollar spent
                'electricity_us_avg': 0.500,  # kg CO2 per kWh (US grid average)
                'electricity_coal': 0.820,
                'electricity_natural_gas': 0.350,
                'electricity_renewable': 0.020,
                'natural_gas_heating': 0.185,  # kg CO2 per kWh thermal
                'heating_oil': 0.264,
                'propane': 0.215,
                'default': 0.500
            },
            'Food': {
                # Per kg of food
                'beef': 60.0,  # Extremely high carbon footprint
                'lamb': 39.2,
                'pork': 12.1,
                'chicken': 6.9,
                'fish_farmed': 5.4,
                'fish_wild': 2.9,
                'dairy_milk': 3.2,  # Per liter
                'cheese': 13.5,
                'eggs': 4.2,  # Per dozen
                'rice': 2.7,
                'wheat_bread': 0.9,
                'vegetables_avg': 0.4,
                'fruits_avg': 0.3,
                'nuts': 0.3,
                'legumes': 0.4,
                'tofu': 2.0,
                'plant_milk': 0.9,
                'default': 2.5  # Mixed diet average per dollar
            },
            'Shopping': {
                # Per dollar spent (rough estimates)
                'clothing_fast_fashion': 0.8,
                'clothing_sustainable': 0.3,
                'electronics': 1.2,
                'furniture': 0.6,
                'books_paper': 0.2,
                'books_digital': 0.01,
                'cosmetics': 0.4,
                'household_items': 0.5,
                'default': 0.5
            },
            'Entertainment': {
                # Per dollar spent or per hour
                'streaming_video': 0.0036,  # Per hour
                'gaming': 0.012,  # Per hour
                'movie_theater': 0.15,  # Per ticket
                'concert': 0.25,  # Per ticket
                'sports_event': 0.30,
                'default': 0.2
            },
            'Other': {
                'default': 0.3
            }
        }
        
        # Conversion factors
        self.conversions = {
            'miles_to_km': 1.60934,
            'gallons_to_liters': 3.78541,
            'lbs_to_kg': 0.453592,
            'kwh_to_mj': 3.6
        }
    
    def calculate_footprint(self, category: str, subcategory: str, amount: float, 
                          unit: str = 'dollar', additional_data: Dict = None) -> float:
        """
        Calculate carbon footprint with improved accuracy
        
        Args:
            category: Main category (Transportation, Energy, etc.)
            subcategory: Specific type within category
            amount: Quantity (dollars, miles, kWh, etc.)
            unit: Unit of measurement
            additional_data: Extra data for more accurate calculations
        
        Returns:
            Carbon footprint in kg CO2 equivalent
        """
        if additional_data is None:
            additional_data = {}
        
        category_factors = self.emission_factors.get(category, {'default': 0.3})
        
        # Get emission factor
        if subcategory and subcategory.lower() in category_factors:
            factor = category_factors[subcategory.lower()]
        else:
            factor = category_factors['default']
        
        # Apply unit conversions and special calculations
        carbon_kg = self._apply_unit_conversion(category, subcategory, amount, unit, factor, additional_data)
        
        return max(0, carbon_kg)  # Ensure non-negative result
    
    def _apply_unit_conversion(self, category: str, subcategory: str, amount: float, 
                             unit: str, factor: float, additional_data: Dict) -> float:
        """Apply unit conversions and category-specific calculations"""
        
        if category == 'Transportation':
            return self._calculate_transportation(subcategory, amount, unit, factor, additional_data)
        elif category == 'Energy':
            return self._calculate_energy(subcategory, amount, unit, factor, additional_data)
        elif category == 'Food':
            return self._calculate_food(subcategory, amount, unit, factor, additional_data)
        else:
            # Default calculation for other categories
            return amount * factor
    
    def _calculate_transportation(self, subcategory: str, amount: float, unit: str, 
                                factor: float, additional_data: Dict) -> float:
        """Calculate transportation emissions with improved accuracy"""
        
        if unit == 'miles':
            return amount * factor
        elif unit == 'km':
            return amount * factor / self.conversions['miles_to_km']
        elif unit == 'gallons':
            # Convert gallons to miles using fuel efficiency
            mpg = additional_data.get('mpg', 25)  # Default 25 MPG
            miles = amount * mpg
            return miles * factor
        elif unit == 'dollar':
            # Estimate based on fuel cost
            if 'gas' in subcategory.lower() or 'fuel' in subcategory.lower():
                gas_price_per_gallon = additional_data.get('gas_price', 3.50)
                gallons = amount / gas_price_per_gallon
                mpg = additional_data.get('mpg', 25)
                miles = gallons * mpg
                return miles * factor
            else:
                # For ride-sharing, estimate miles from cost
                estimated_miles = amount / 2.5  # Rough estimate: $2.5 per mile
                return estimated_miles * factor
        else:
            return amount * factor
    
    def _calculate_energy(self, subcategory: str, amount: float, unit: str, 
                         factor: float, additional_data: Dict) -> float:
        """Calculate energy emissions with grid mix considerations"""
        
        if unit == 'kwh':
            # Apply regional grid mix if available
            grid_factor = additional_data.get('grid_carbon_intensity', factor)
            return amount * grid_factor
        elif unit == 'dollar':
            # Convert dollars to kWh based on local electricity rates
            kwh_per_dollar = additional_data.get('kwh_per_dollar', 8.5)  # US average ~$0.12/kWh
            kwh = amount * kwh_per_dollar
            return kwh * factor
        elif unit == 'therms':
            # Natural gas in therms
            return amount * 5.3  # kg CO2 per therm
        else:
            return amount * factor
    
    def _calculate_food(self, subcategory: str, amount: float, unit: str, 
                       factor: float, additional_data: Dict) -> float:
        """Calculate food emissions with portion size considerations"""
        
        if unit == 'kg':
            return amount * factor
        elif unit == 'lbs':
            kg = amount * self.conversions['lbs_to_kg']
            return kg * factor
        elif unit == 'servings':
            # Convert servings to kg based on food type
            serving_weights = {
                'beef': 0.113,  # 4 oz serving
                'chicken': 0.085,  # 3 oz serving
                'fish': 0.085,
                'vegetables': 0.080,
                'rice': 0.045,  # 1/4 cup dry
                'default': 0.100
            }
            serving_weight = serving_weights.get(subcategory.lower(), serving_weights['default'])
            kg = amount * serving_weight
            return kg * factor
        elif unit == 'dollar':
            # Estimate based on food cost and type
            if subcategory.lower() in ['beef', 'lamb']:
                # Expensive meat, lower quantity per dollar
                estimated_kg = amount / 15  # ~$15/kg for beef
            elif subcategory.lower() in ['chicken', 'pork']:
                estimated_kg = amount / 8   # ~$8/kg
            elif subcategory.lower() in ['vegetables', 'fruits']:
                estimated_kg = amount / 4   # ~$4/kg
            else:
                estimated_kg = amount / 6   # Mixed average
            
            return estimated_kg * factor
        else:
            return amount * factor
    
    def get_recommendations(self, transactions: List[Dict]) -> List[Dict]:
        """Generate personalized recommendations with improved accuracy"""
        if not transactions:
            return []
        
        df = pd.DataFrame(transactions)
        
        # Calculate category totals and intensities
        category_analysis = df.groupby('category').agg({
            'amount': 'sum',
            'carbon_kg': 'sum'
        }).reset_index()
        
        category_analysis['carbon_intensity'] = (
            category_analysis['carbon_kg'] / category_analysis['amount']
        )
        
        recommendations = []
        
        # Sort by highest carbon footprint
        high_carbon_categories = category_analysis.nlargest(3, 'carbon_kg')
        
        for _, row in high_carbon_categories.iterrows():
            category = row['category']
            carbon = row['carbon_kg']
            amount = row['amount']
            intensity = row['carbon_intensity']
            
            # Generate category-specific recommendations
            if category == 'Transportation' and carbon > 50:
                recommendations.extend(self._get_transportation_recommendations(carbon, amount, intensity))
            elif category == 'Food' and carbon > 30:
                recommendations.extend(self._get_food_recommendations(carbon, amount, intensity))
            elif category == 'Energy' and carbon > 40:
                recommendations.extend(self._get_energy_recommendations(carbon, amount, intensity))
            elif category == 'Shopping' and carbon > 20:
                recommendations.extend(self._get_shopping_recommendations(carbon, amount, intensity))
        
        # Sort by potential impact and return top recommendations
        recommendations.sort(key=lambda x: x['carbon_savings'], reverse=True)
        return recommendations[:5]
    
    def _get_transportation_recommendations(self, carbon: float, amount: float, intensity: float) -> List[Dict]:
        """Get transportation-specific recommendations"""
        recommendations = []
        
        if intensity > 0.4:  # High carbon intensity
            recommendations.append({
                'id': 'transport_efficiency',
                'title': 'Switch to More Efficient Transportation',
                'description': 'Consider hybrid/electric vehicles, public transit, or carpooling.',
                'cost_savings': amount * 0.3,
                'carbon_savings': carbon * 0.6,
                'details': 'Electric vehicles produce 60% less emissions than gas cars.',
                'difficulty': 'Medium',
                'timeframe': '1-6 months'
            })
        
        if carbon > 100:  # High absolute emissions
            recommendations.append({
                'id': 'transport_reduce',
                'title': 'Reduce Transportation Frequency',
                'description': 'Combine trips, work from home more, or use active transportation.',
                'cost_savings': amount * 0.2,
                'carbon_savings': carbon * 0.3,
                'details': 'Combining errands into one trip can reduce emissions by 30%.',
                'difficulty': 'Easy',
                'timeframe': 'Immediate'
            })
        
        return recommendations
    
    def _get_food_recommendations(self, carbon: float, amount: float, intensity: float) -> List[Dict]:
        """Get food-specific recommendations"""
        recommendations = []
        
        if intensity > 2.0:  # High carbon intensity (likely meat-heavy)
            recommendations.append({
                'id': 'food_plant_based',
                'title': 'Increase Plant-Based Meals',
                'description': 'Replace 2-3 meat meals per week with plant-based alternatives.',
                'cost_savings': amount * 0.1,
                'carbon_savings': carbon * 0.4,
                'details': 'Plant-based proteins produce 90% less emissions than beef.',
                'difficulty': 'Easy',
                'timeframe': 'Immediate'
            })
        
        recommendations.append({
            'id': 'food_local',
            'title': 'Choose Local and Seasonal Foods',
            'description': 'Buy from local farmers markets and choose seasonal produce.',
            'cost_savings': amount * 0.05,
            'carbon_savings': carbon * 0.2,
            'details': 'Local food reduces transportation emissions by up to 20%.',
            'difficulty': 'Easy',
            'timeframe': 'Immediate'
        })
        
        return recommendations
    
    def _get_energy_recommendations(self, carbon: float, amount: float, intensity: float) -> List[Dict]:
        """Get energy-specific recommendations"""
        recommendations = []
        
        recommendations.append({
            'id': 'energy_efficiency',
            'title': 'Improve Home Energy Efficiency',
            'description': 'Upgrade to LED bulbs, smart thermostat, and better insulation.',
            'cost_savings': amount * 0.25,
            'carbon_savings': carbon * 0.3,
            'details': 'Energy efficiency upgrades can reduce consumption by 30%.',
            'difficulty': 'Medium',
            'timeframe': '1-3 months'
        })
        
        if intensity > 0.6:  # High carbon intensity (dirty grid)
            recommendations.append({
                'id': 'energy_renewable',
                'title': 'Switch to Renewable Energy',
                'description': 'Choose a renewable energy provider or install solar panels.',
                'cost_savings': amount * 0.1,
                'carbon_savings': carbon * 0.8,
                'details': 'Renewable energy can reduce home emissions by up to 80%.',
                'difficulty': 'Hard',
                'timeframe': '3-12 months'
            })
        
        return recommendations
    
    def _get_shopping_recommendations(self, carbon: float, amount: float, intensity: float) -> List[Dict]:
        """Get shopping-specific recommendations"""
        recommendations = []
        
        recommendations.append({
            'id': 'shopping_sustainable',
            'title': 'Choose Sustainable Products',
            'description': 'Buy durable, repairable items and avoid fast fashion.',
            'cost_savings': amount * 0.2,
            'carbon_savings': carbon * 0.4,
            'details': 'Durable goods last longer and have lower lifetime emissions.',
            'difficulty': 'Easy',
            'timeframe': 'Immediate'
        })
        
        return recommendations
    
    def calculate_offset_cost(self, carbon_kg: float, offset_price_per_ton: float = 15.0) -> float:
        """Calculate cost to offset carbon emissions"""
        tons = carbon_kg / 1000
        return tons * offset_price_per_ton
    
    def get_carbon_intensity_by_region(self, region: str) -> float:
        """Get regional electricity carbon intensity (kg CO2/kWh)"""
        regional_factors = {
            'california': 0.200,  # Clean grid
            'texas': 0.450,
            'new_york': 0.280,
            'florida': 0.520,
            'washington': 0.110,  # Hydro power
            'west_virginia': 0.720,  # Coal heavy
            'us_average': 0.500
        }
        
        return regional_factors.get(region.lower(), regional_factors['us_average'])
