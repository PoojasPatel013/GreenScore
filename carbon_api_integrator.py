import requests
import json
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import asyncio
import aiohttp
from dataclasses import dataclass
import os
from enum import Enum

class CarbonAPIProvider(Enum):
    CARBON_INTERFACE = "carbon_interface"
    CLOVERLY = "cloverly"
    CO2_SIGNAL = "co2_signal"
    CLIMATIQ = "climatiq"
    EPA = "epa"

@dataclass
class CarbonEstimate:
    carbon_kg: float
    carbon_lb: float
    carbon_mt: float
    confidence: float
    source: str
    methodology: str
    factors_used: Dict
    timestamp: datetime

class CarbonAPIIntegrator:
    def __init__(self):
        """Initialize carbon API integrator with multiple providers"""
        
        # API Keys (should be set as environment variables)
        self.api_keys = {
            'carbon_interface': os.getenv('CARBON_INTERFACE_API_KEY'),
            'cloverly': os.getenv('CLOVERLY_API_KEY'),
            'co2_signal': os.getenv('CO2_SIGNAL_API_KEY'),
            'climatiq': os.getenv('CLIMATIQ_API_KEY')
        }
        
        # API Endpoints
        self.endpoints = {
            'carbon_interface': 'https://www.carboninterface.com/api/v1',
            'cloverly': 'https://api.cloverly.com/2019-03-beta',
            'co2_signal': 'https://api.co2signal.com/v1',
            'climatiq': 'https://beta3.api.climatiq.io'
        }
        
        # Fallback emission factors (EPA/IPCC data)
        self.fallback_factors = self.load_fallback_factors()
        
        # Cache for API responses
        self.cache = {}
        self.cache_duration = timedelta(hours=24)
    
    def load_fallback_factors(self) -> Dict:
        """Load comprehensive fallback emission factors"""
        return {
            'electricity': {
                'us_average': 0.500,  # kg CO2/kWh
                'california': 0.200,
                'texas': 0.450,
                'new_york': 0.280,
                'florida': 0.520,
                'washington': 0.110,
                'coal': 0.820,
                'natural_gas': 0.350,
                'renewable': 0.020
            },
            'transportation': {
                'gasoline_car': 0.404,  # kg CO2/mile
                'diesel_car': 0.463,
                'hybrid_car': 0.200,
                'electric_car': 0.180,
                'motorcycle': 0.280,
                'bus': 0.080,
                'train': 0.060,
                'subway': 0.040,
                'flight_domestic': 0.255,
                'flight_international': 0.195
            },
            'fuel': {
                'gasoline': 8.89,  # kg CO2/gallon
                'diesel': 10.15,
                'natural_gas': 5.3,  # kg CO2/therm
                'propane': 5.75,  # kg CO2/gallon
                'heating_oil': 10.15
            },
            'food': {
                'beef': 60.0,  # kg CO2/kg
                'lamb': 39.2,
                'pork': 12.1,
                'chicken': 6.9,
                'fish_farmed': 5.4,
                'fish_wild': 2.9,
                'dairy_milk': 3.2,
                'cheese': 13.5,
                'eggs': 4.2,
                'rice': 2.7,
                'wheat': 0.9,
                'vegetables': 0.4,
                'fruits': 0.3
            },
            'manufacturing': {
                'steel': 2.3,  # kg CO2/kg
                'aluminum': 8.2,
                'cement': 0.9,
                'plastic': 2.0,
                'paper': 1.3,
                'glass': 0.5
            }
        }
    
    async def get_carbon_estimate(self, activity_type: str, activity_data: Dict, 
                                 preferred_provider: CarbonAPIProvider = None) -> CarbonEstimate:
        """
        Get carbon estimate from multiple providers with fallback
        
        Args:
            activity_type: Type of activity (electricity, transportation, etc.)
            activity_data: Activity-specific data (amount, location, etc.)
            preferred_provider: Preferred API provider
            
        Returns:
            CarbonEstimate object
        """
        
        # Try preferred provider first
        if preferred_provider:
            try:
                estimate = await self._get_estimate_from_provider(
                    preferred_provider, activity_type, activity_data
                )
                if estimate:
                    return estimate
            except Exception as e:
                print(f"Error with preferred provider {preferred_provider}: {e}")
        
        # Try all providers in order of reliability
        providers = [
            CarbonAPIProvider.CARBON_INTERFACE,
            CarbonAPIProvider.CLIMATIQ,
            CarbonAPIProvider.CLOVERLY,
            CarbonAPIProvider.CO2_SIGNAL
        ]
        
        for provider in providers:
            if provider == preferred_provider:
                continue  # Already tried
            
            try:
                estimate = await self._get_estimate_from_provider(
                    provider, activity_type, activity_data
                )
                if estimate:
                    return estimate
            except Exception as e:
                print(f"Error with provider {provider}: {e}")
                continue
        
        # Fallback to local calculations
        return self._calculate_fallback_estimate(activity_type, activity_data)
    
    async def _get_estimate_from_provider(self, provider: CarbonAPIProvider, 
                                        activity_type: str, activity_data: Dict) -> Optional[CarbonEstimate]:
        """Get estimate from specific provider"""
        
        if provider == CarbonAPIProvider.CARBON_INTERFACE:
            return await self._carbon_interface_estimate(activity_type, activity_data)
        elif provider == CarbonAPIProvider.CLOVERLY:
            return await self._cloverly_estimate(activity_type, activity_data)
        elif provider == CarbonAPIProvider.CO2_SIGNAL:
            return await self._co2_signal_estimate(activity_type, activity_data)
        elif provider == CarbonAPIProvider.CLIMATIQ:
            return await self._climatiq_estimate(activity_type, activity_data)
        
        return None
    
    async def _carbon_interface_estimate(self, activity_type: str, activity_data: Dict) -> Optional[CarbonEstimate]:
        """Get estimate from Carbon Interface API"""
        
        if not self.api_keys['carbon_interface']:
            return None
        
        headers = {
            'Authorization': f'Bearer {self.api_keys["carbon_interface"]}',
            'Content-Type': 'application/json'
        }
        
        # Map activity types to Carbon Interface endpoints
        endpoint_mapping = {
            'electricity': '/estimates',
            'transportation': '/estimates',
            'flight': '/estimates',
            'shipping': '/estimates',
            'fuel': '/estimates'
        }
        
        endpoint = endpoint_mapping.get(activity_type)
        if not endpoint:
            return None
        
        # Prepare request data based on activity type
        request_data = self._prepare_carbon_interface_data(activity_type, activity_data)
        if not request_data:
            return None
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.endpoints['carbon_interface']}{endpoint}",
                    headers=headers,
                    json=request_data
                ) as response:
                    
                    if response.status == 200:
                        data = await response.json()
                        return self._parse_carbon_interface_response(data)
                    else:
                        print(f"Carbon Interface API error: {response.status}")
                        return None
        
        except Exception as e:
            print(f"Carbon Interface request error: {e}")
            return None
    
    def _prepare_carbon_interface_data(self, activity_type: str, activity_data: Dict) -> Optional[Dict]:
        """Prepare request data for Carbon Interface API"""
        
        if activity_type == 'electricity':
            return {
                'type': 'electricity',
                'electricity_unit': 'kwh',
                'electricity_value': activity_data.get('kwh', 0),
                'country': activity_data.get('country', 'us'),
                'state': activity_data.get('state', None)
            }
        
        elif activity_type == 'transportation':
            vehicle_model = activity_data.get('vehicle_model', 'average_car')
            return {
                'type': 'vehicle',
                'distance_unit': 'mi',
                'distance_value': activity_data.get('distance_miles', 0),
                'vehicle_model_id': vehicle_model
            }
        
        elif activity_type == 'flight':
            return {
                'type': 'flight',
                'passengers': activity_data.get('passengers', 1),
                'legs': [
                    {
                        'departure_airport': activity_data.get('departure_airport', 'LAX'),
                        'destination_airport': activity_data.get('destination_airport', 'JFK')
                    }
                ]
            }
        
        elif activity_type == 'fuel':
            return {
                'type': 'fuel_combustion',
                'fuel_source_type': activity_data.get('fuel_type', 'gasoline'),
                'fuel_source_unit': 'gallon',
                'fuel_source_value': activity_data.get('gallons', 0)
            }
        
        return None
    
    def _parse_carbon_interface_response(self, data: Dict) -> CarbonEstimate:
        """Parse Carbon Interface API response"""
        
        attributes = data.get('data', {}).get('attributes', {})
        
        carbon_kg = attributes.get('carbon_kg', 0)
        carbon_lb = attributes.get('carbon_lb', 0)
        carbon_mt = attributes.get('carbon_mt', 0)
        
        return CarbonEstimate(
            carbon_kg=carbon_kg,
            carbon_lb=carbon_lb,
            carbon_mt=carbon_mt,
            confidence=0.9,  # High confidence for API data
            source='Carbon Interface',
            methodology='API',
            factors_used=attributes,
            timestamp=datetime.now()
        )
    
    async def _climatiq_estimate(self, activity_type: str, activity_data: Dict) -> Optional[CarbonEstimate]:
        """Get estimate from Climatiq API"""
        
        if not self.api_keys['climatiq']:
            return None
        
        headers = {
            'Authorization': f'Bearer {self.api_keys["climatiq"]}',
            'Content-Type': 'application/json'
        }
        
        # Climatiq uses emission factors
        emission_factor_id = self._get_climatiq_emission_factor(activity_type, activity_data)
        if not emission_factor_id:
            return None
        
        request_data = {
            'emission_factor': emission_factor_id,
            'parameters': self._prepare_climatiq_parameters(activity_type, activity_data)
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.endpoints['climatiq']}/estimate",
                    headers=headers,
                    json=request_data
                ) as response:
                    
                    if response.status == 200:
                        data = await response.json()
                        return self._parse_climatiq_response(data)
                    else:
                        print(f"Climatiq API error: {response.status}")
                        return None
        
        except Exception as e:
            print(f"Climatiq request error: {e}")
            return None
    
    def _get_climatiq_emission_factor(self, activity_type: str, activity_data: Dict) -> Optional[str]:
        """Get appropriate Climatiq emission factor ID"""
        
        # Mapping of activity types to Climatiq emission factor IDs
        factor_mapping = {
            'electricity': 'electricity-energy_source_grid_mix',
            'transportation': 'passenger_vehicle-vehicle_type_car-fuel_source_gasoline',
            'flight': 'passenger_flight-route_type_domestic',
            'fuel': 'fuel_combustion-fuel_source_gasoline'
        }
        
        return factor_mapping.get(activity_type)
    
    def _prepare_climatiq_parameters(self, activity_type: str, activity_data: Dict) -> Dict:
        """Prepare parameters for Climatiq API"""
        
        if activity_type == 'electricity':
            return {
                'energy': activity_data.get('kwh', 0),
                'energy_unit': 'kWh'
            }
        elif activity_type == 'transportation':
            return {
                'distance': activity_data.get('distance_miles', 0),
                'distance_unit': 'mi'
            }
        elif activity_type == 'fuel':
            return {
                'volume': activity_data.get('gallons', 0),
                'volume_unit': 'gal'
            }
        
        return {}
    
    def _parse_climatiq_response(self, data: Dict) -> CarbonEstimate:
        """Parse Climatiq API response"""
        
        co2e = data.get('co2e', 0)  # kg CO2 equivalent
        co2e_unit = data.get('co2e_unit', 'kg')
        
        # Convert to standard units
        carbon_kg = co2e if co2e_unit == 'kg' else co2e * 1000 if co2e_unit == 't' else co2e / 1000
        carbon_lb = carbon_kg * 2.20462
        carbon_mt = carbon_kg / 1000
        
        return CarbonEstimate(
            carbon_kg=carbon_kg,
            carbon_lb=carbon_lb,
            carbon_mt=carbon_mt,
            confidence=0.85,
            source='Climatiq',
            methodology='API',
            factors_used=data.get('emission_factor', {}),
            timestamp=datetime.now()
        )
    
    async def _co2_signal_estimate(self, activity_type: str, activity_data: Dict) -> Optional[CarbonEstimate]:
        """Get real-time electricity carbon intensity from CO2 Signal"""
        
        if activity_type != 'electricity' or not self.api_keys['co2_signal']:
            return None
        
        headers = {
            'auth-token': self.api_keys['co2_signal']
        }
        
        # Get carbon intensity for location
        country_code = activity_data.get('country_code', 'US')
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.endpoints['co2_signal']}/latest",
                    headers=headers,
                    params={'countryCode': country_code}
                ) as response:
                    
                    if response.status == 200:
                        data = await response.json()
                        
                        # Calculate carbon footprint
                        carbon_intensity = data.get('data', {}).get('carbonIntensity', 500)  # gCO2/kWh
                        kwh = activity_data.get('kwh', 0)
                        
                        carbon_kg = (carbon_intensity * kwh) / 1000  # Convert g to kg
                        
                        return CarbonEstimate(
                            carbon_kg=carbon_kg,
                            carbon_lb=carbon_kg * 2.20462,
                            carbon_mt=carbon_kg / 1000,
                            confidence=0.8,
                            source='CO2 Signal',
                            methodology='Real-time grid data',
                            factors_used={'carbon_intensity_gco2_kwh': carbon_intensity},
                            timestamp=datetime.now()
                        )
                    else:
                        print(f"CO2 Signal API error: {response.status}")
                        return None
        
        except Exception as e:
            print(f"CO2 Signal request error: {e}")
            return None
    
    def _calculate_fallback_estimate(self, activity_type: str, activity_data: Dict) -> CarbonEstimate:
        """Calculate estimate using fallback emission factors"""
        
        carbon_kg = 0
        factors_used = {}
        
        if activity_type == 'electricity':
            kwh = activity_data.get('kwh', 0)
            region = activity_data.get('region', 'us_average')
            factor = self.fallback_factors['electricity'].get(region, 0.5)
            carbon_kg = kwh * factor
            factors_used = {'emission_factor_kg_co2_kwh': factor, 'region': region}
        
        elif activity_type == 'transportation':
            miles = activity_data.get('distance_miles', 0)
            vehicle_type = activity_data.get('vehicle_type', 'gasoline_car')
            factor = self.fallback_factors['transportation'].get(vehicle_type, 0.404)
            carbon_kg = miles * factor
            factors_used = {'emission_factor_kg_co2_mile': factor, 'vehicle_type': vehicle_type}
        
        elif activity_type == 'fuel':
            gallons = activity_data.get('gallons', 0)
            fuel_type = activity_data.get('fuel_type', 'gasoline')
            factor = self.fallback_factors['fuel'].get(fuel_type, 8.89)
            carbon_kg = gallons * factor
            factors_used = {'emission_factor_kg_co2_gallon': factor, 'fuel_type': fuel_type}
        
        elif activity_type == 'food':
            kg = activity_data.get('kg', 0)
            food_type = activity_data.get('food_type', 'mixed')
            factor = self.fallback_factors['food'].get(food_type, 2.5)
            carbon_kg = kg * factor
            factors_used = {'emission_factor_kg_co2_kg': factor, 'food_type': food_type}
        
        return CarbonEstimate(
            carbon_kg=carbon_kg,
            carbon_lb=carbon_kg * 2.20462,
            carbon_mt=carbon_kg / 1000,
            confidence=0.7,  # Lower confidence for fallback
            source='EPA/IPCC Fallback',
            methodology='Local calculation',
            factors_used=factors_used,
            timestamp=datetime.now()
        )
    
    async def batch_estimate_transactions(self, transactions: List[Dict]) -> List[Dict]:
        """Process multiple transactions efficiently"""
        
        enhanced_transactions = []
        
        # Group transactions by type for batch processing
        grouped_transactions = {}
        for i, transaction in enumerate(transactions):
            activity_type = self._map_category_to_activity_type(
                transaction.get('ai_category', 'Other'),
                transaction.get('ai_subcategory', '')
            )
            
            if activity_type not in grouped_transactions:
                grouped_transactions[activity_type] = []
            
            grouped_transactions[activity_type].append((i, transaction))
        
        # Process each group
        for activity_type, transaction_group in grouped_transactions.items():
            tasks = []
            
            for i, transaction in transaction_group:
                activity_data = self._extract_activity_data(transaction, activity_type)
                task = self.get_carbon_estimate(activity_type, activity_data)
                tasks.append((i, transaction, task))
            
            # Execute batch requests
            for i, transaction, task in tasks:
                try:
                    estimate = await task
                    
                    # Add estimate to transaction
                    enhanced_transaction = transaction.copy()
                    enhanced_transaction.update({
                        'api_carbon_kg': estimate.carbon_kg,
                        'api_carbon_lb': estimate.carbon_lb,
                        'api_carbon_mt': estimate.carbon_mt,
                        'api_confidence': estimate.confidence,
                        'api_source': estimate.source,
                        'api_methodology': estimate.methodology,
                        'api_factors': estimate.factors_used,
                        'api_timestamp': estimate.timestamp.isoformat()
                    })
                    
                    enhanced_transactions.append((i, enhanced_transaction))
                
                except Exception as e:
                    print(f"Error processing transaction {i}: {e}")
                    enhanced_transactions.append((i, transaction))
        
        # Sort back to original order
        enhanced_transactions.sort(key=lambda x: x[0])
        return [t[1] for t in enhanced_transactions]
    
    def _map_category_to_activity_type(self, category: str, subcategory: str) -> str:
        """Map transaction category to API activity type"""
        
        mapping = {
            'Transportation': 'transportation',
            'Energy': 'electricity',
            'Food': 'food',
            'Shopping': 'manufacturing',  # Approximate
            'Entertainment': 'electricity'  # Approximate
        }
        
        # Special cases based on subcategory
        if category == 'Transportation' and 'flight' in subcategory.lower():
            return 'flight'
        elif category == 'Transportation' and any(fuel in subcategory.lower() for fuel in ['gas', 'fuel', 'gasoline']):
            return 'fuel'
        
        return mapping.get(category, 'other')
    
    def _extract_activity_data(self, transaction: Dict, activity_type: str) -> Dict:
        """Extract relevant data for API calls"""
        
        amount = transaction.get('amount', 0)
        subcategory = transaction.get('ai_subcategory', '')
        
        if activity_type == 'electricity':
            # Estimate kWh from dollar amount (average $0.12/kWh)
            kwh = amount / 0.12
            return {
                'kwh': kwh,
                'country': 'us',
                'region': 'us_average'
            }
        
        elif activity_type == 'transportation':
            # Estimate miles from dollar amount
            if 'gas' in subcategory or 'fuel' in subcategory:
                # Gas purchase - estimate gallons then miles
                gallons = amount / 3.50  # Average gas price
                miles = gallons * 25  # Average MPG
            else:
                # Other transport - estimate miles directly
                miles = amount / 2.5  # Rough estimate
            
            return {
                'distance_miles': miles,
                'vehicle_type': 'gasoline_car'
            }
        
        elif activity_type == 'fuel':
            gallons = amount / 3.50  # Average gas price
            return {
                'gallons': gallons,
                'fuel_type': 'gasoline'
            }
        
        elif activity_type == 'food':
            # Estimate food weight from spending
            kg = amount / 8  # Rough estimate $8/kg average
            return {
                'kg': kg,
                'food_type': 'mixed'
            }
        
        return {'amount': amount}
    
    def get_api_status(self) -> Dict:
        """Check status of all carbon APIs"""
        
        status = {}
        
        for provider in CarbonAPIProvider:
            api_key = self.api_keys.get(provider.value)
            status[provider.value] = {
                'api_key_configured': bool(api_key),
                'endpoint': self.endpoints.get(provider.value),
                'last_successful_call': None,  # Would track in production
                'rate_limit_remaining': None   # Would track in production
            }
        
        return status
