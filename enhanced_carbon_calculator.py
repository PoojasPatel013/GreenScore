import asyncio
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import pandas as pd
from ai_transaction_parser import AITransactionParser, TransactionClassification
from carbon_api_integrator import CarbonAPIIntegrator, CarbonAPIProvider
from carbon_calculator import CarbonCalculator

class EnhancedCarbonCalculator:
    def __init__(self):
        """Initialize enhanced calculator with AI and API integration"""
        
        self.ai_parser = AITransactionParser()
        self.api_integrator = CarbonAPIIntegrator()
        self.base_calculator = CarbonCalculator()
        
        # Confidence thresholds for different calculation methods
        self.confidence_thresholds = {
            'api_primary': 0.8,      # Use API as primary source
            'api_secondary': 0.6,    # Use API to validate local calculation
            'ai_classification': 0.7, # Trust AI classification
            'fallback_only': 0.3     # Use only fallback calculations
        }
    
    async def process_transaction(self, description: str, amount: float, 
                                date: str = None, user_preferences: Dict = None) -> Dict:
        """
        Process a single transaction with full AI and API integration
        
        Args:
            description: Transaction description
            amount: Transaction amount
            date: Transaction date
            user_preferences: User preferences for calculation methods
            
        Returns:
            Enhanced transaction data with multiple carbon estimates
        """
        
        # Step 1: AI-powered transaction parsing
        ai_classification = self.ai_parser.parse_transaction(description, amount, date)
        
        # Step 2: Get multiple carbon estimates
        estimates = await self._get_multiple_estimates(ai_classification, amount, user_preferences)
        
        # Step 3: Calculate final carbon footprint with confidence weighting
        final_estimate = self._calculate_weighted_estimate(estimates, ai_classification)
        
        # Step 4: Generate insights and recommendations
        insights = self._generate_transaction_insights(ai_classification, final_estimate, amount)
        
        return {
            'description': description,
            'amount': amount,
            'date': date or datetime.now().isoformat(),
            
            # AI Classification Results
            'ai_category': ai_classification.category,
            'ai_subcategory': ai_classification.subcategory,
            'ai_confidence': ai_classification.confidence,
            'ai_carbon_intensity': ai_classification.carbon_intensity,
            'ai_merchant_type': ai_classification.merchant_type,
            'ai_location': ai_classification.location,
            
            # Carbon Estimates
            'carbon_estimates': estimates,
            'final_carbon_kg': final_estimate['carbon_kg'],
            'final_confidence': final_estimate['confidence'],
            'calculation_method': final_estimate['method'],
            'methodology_details': final_estimate['details'],
            
            # Insights and Recommendations
            'insights': insights,
            'environmental_impact': self._calculate_environmental_impact(final_estimate['carbon_kg']),
            
            # Metadata
            'processed_at': datetime.now().isoformat(),
            'processing_version': '2.0'
        }
    
    async def _get_multiple_estimates(self, classification: TransactionClassification, 
                                    amount: float, user_preferences: Dict = None) -> Dict:
        """Get carbon estimates from multiple sources"""
        
        estimates = {}
        
        # 1. Local calculation using enhanced factors
        local_estimate = self.base_calculator.calculate_footprint(
            classification.category,
            classification.subcategory,
            amount
        )
        
        estimates['local'] = {
            'carbon_kg': local_estimate,
            'confidence': 0.7,
            'source': 'Local Enhanced Calculator',
            'method': 'EPA/IPCC factors'
        }
        
        # 2. API-based estimates (if classification confidence is high enough)
        if classification.confidence >= self.confidence_thresholds['api_secondary']:
            try:
                # Prepare activity data for APIs
                activity_type = self._map_to_activity_type(classification)
                activity_data = self._prepare_activity_data(classification, amount)
                
                # Get estimates from multiple APIs
                api_tasks = []
                
                # Carbon Interface
                if user_preferences and user_preferences.get('use_carbon_interface', True):
                    api_tasks.append(
                        self.api_integrator.get_carbon_estimate(
                            activity_type, activity_data, CarbonAPIProvider.CARBON_INTERFACE
                        )
                    )
                
                # Climatiq
                if user_preferences and user_preferences.get('use_climatiq', True):
                    api_tasks.append(
                        self.api_integrator.get_carbon_estimate(
                            activity_type, activity_data, CarbonAPIProvider.CLIMATIQ
                        )
                    )
                
                # Execute API calls concurrently
                if api_tasks:
                    api_results = await asyncio.gather(*api_tasks, return_exceptions=True)
                    
                    for i, result in enumerate(api_results):
                        if not isinstance(result, Exception) and result:
                            provider_name = ['carbon_interface', 'climatiq'][i]
                            estimates[f'api_{provider_name}'] = {
                                'carbon_kg': result.carbon_kg,
                                'confidence': result.confidence,
                                'source': result.source,
                                'method': result.methodology,
                                'factors': result.factors_used
                            }
            
            except Exception as e:
                print(f"Error getting API estimates: {e}")
        
        # 3. Industry-specific calculations
        industry_estimate = self._calculate_industry_specific(classification, amount)
        if industry_estimate:
            estimates['industry_specific'] = industry_estimate
        
        return estimates
    
    def _calculate_weighted_estimate(self, estimates: Dict, classification: TransactionClassification) -> Dict:
        """Calculate final estimate using confidence-weighted average"""
        
        if not estimates:
            return {
                'carbon_kg': 0,
                'confidence': 0,
                'method': 'No estimates available',
                'details': {}
            }
        
        # Weight estimates by confidence and source reliability
        source_weights = {
            'api_carbon_interface': 1.0,
            'api_climatiq': 0.95,
            'api_cloverly': 0.9,
            'industry_specific': 0.85,
            'local': 0.8
        }
        
        weighted_sum = 0
        total_weight = 0
        methods_used = []
        
        for source, estimate in estimates.items():
            base_weight = source_weights.get(source, 0.5)
            confidence_weight = estimate['confidence']
            final_weight = base_weight * confidence_weight
            
            weighted_sum += estimate['carbon_kg'] * final_weight
            total_weight += final_weight
            methods_used.append({
                'source': source,
                'carbon_kg': estimate['carbon_kg'],
                'weight': final_weight,
                'confidence': confidence_weight
            })
        
        if total_weight == 0:
            return {
                'carbon_kg': 0,
                'confidence': 0,
                'method': 'No valid estimates',
                'details': {}
            }
        
        final_carbon = weighted_sum / total_weight
        final_confidence = min(total_weight / len(estimates), 1.0)
        
        # Determine primary method
        primary_method = max(methods_used, key=lambda x: x['weight'])
        
        return {
            'carbon_kg': final_carbon,
            'confidence': final_confidence,
            'method': f"Weighted average (primary: {primary_method['source']})",
            'details': {
                'methods_used': methods_used,
                'total_weight': total_weight,
                'primary_source': primary_method['source']
            }
        }
    
    def _map_to_activity_type(self, classification: TransactionClassification) -> str:
        """Map AI classification to API activity type"""
        
        category_mapping = {
            'Transportation': 'transportation',
            'Energy': 'electricity',
            'Food': 'food',
            'Shopping': 'manufacturing'
        }
        
        # Special handling for subcategories
        if classification.category == 'Transportation':
            if 'flight' in classification.subcategory.lower():
                return 'flight'
            elif any(fuel in classification.subcategory.lower() for fuel in ['gas', 'fuel', 'gasoline']):
                return 'fuel'
        
        return category_mapping.get(classification.category, 'other')
    
    def _prepare_activity_data(self, classification: TransactionClassification, amount: float) -> Dict:
        """Prepare activity data for API calls based on classification"""
        
        base_data = {'amount': amount}
        
        if classification.category == 'Transportation':
            if 'gas' in classification.subcategory.lower():
                # Gas purchase
                gallons = amount / 3.50  # Average gas price
                base_data.update({
                    'gallons': gallons,
                    'fuel_type': 'gasoline'
                })
            else:
                # Transportation service
                estimated_miles = amount / 2.5  # Rough estimate
                base_data.update({
                    'distance_miles': estimated_miles,
                    'vehicle_type': 'gasoline_car'
                })
        
        elif classification.category == 'Energy':
            # Estimate kWh from dollar amount
            kwh = amount / 0.12  # Average electricity rate
            base_data.update({
                'kwh': kwh,
                'country': 'us',
                'region': 'us_average'
            })
        
        elif classification.category == 'Food':
            # Estimate food quantity
            if any(meat in classification.subcategory.lower() for meat in ['beef', 'meat', 'burger']):
                kg = amount / 15  # Expensive meat
                food_type = 'beef'
            elif 'chicken' in classification.subcategory.lower():
                kg = amount / 8
                food_type = 'chicken'
            else:
                kg = amount / 6  # Mixed food
                food_type = 'mixed'
            
            base_data.update({
                'kg': kg,
                'food_type': food_type
            })
        
        # Add location if available
        if classification.location:
            base_data['location'] = classification.location
        
        return base_data
    
    def _calculate_industry_specific(self, classification: TransactionClassification, amount: float) -> Optional[Dict]:
        """Calculate using industry-specific methodologies"""
        
        # Industry-specific calculations for high-accuracy scenarios
        industry_factors = {
            'airline': {
                'domestic_flight': 0.255,  # kg CO2 per passenger mile
                'international_flight': 0.195,
                'estimation_method': 'flight_distance_from_cost'
            },
            'utility': {
                'electricity': 0.500,  # kg CO2 per kWh (US average)
                'natural_gas': 0.185,  # kg CO2 per kWh thermal
                'estimation_method': 'energy_from_cost'
            },
            'fuel_station': {
                'gasoline': 8.89,  # kg CO2 per gallon
                'diesel': 10.15,
                'estimation_method': 'fuel_volume_from_cost'
            }
        }
        
        # Determine industry based on classification
        industry = None
        if classification.category == 'Transportation':
            if 'flight' in classification.subcategory.lower():
                industry = 'airline'
            elif any(fuel in classification.subcategory.lower() for fuel in ['gas', 'fuel']):
                industry = 'fuel_station'
        elif classification.category == 'Energy':
            industry = 'utility'
        
        if not industry or industry not in industry_factors:
            return None
        
        # Calculate based on industry
        factors = industry_factors[industry]
        
        if industry == 'airline':
            # Estimate flight distance from cost
            estimated_miles = amount / 0.15  # Rough estimate: $0.15 per mile
            carbon_kg = estimated_miles * factors['domestic_flight']
        
        elif industry == 'utility':
            # Estimate energy consumption from cost
            kwh = amount / 0.12  # Average electricity rate
            carbon_kg = kwh * factors['electricity']
        
        elif industry == 'fuel_station':
            # Estimate fuel volume from cost
            gallons = amount / 3.50  # Average gas price
            carbon_kg = gallons * factors['gasoline']
        
        else:
            return None
        
        return {
            'carbon_kg': carbon_kg,
            'confidence': 0.85,
            'source': f'Industry-specific ({industry})',
            'method': factors['estimation_method'],
            'factors': factors
        }
    
    def _generate_transaction_insights(self, classification: TransactionClassification,
                                     final_estimate: Dict, amount: float) -> Dict:
        """Generate insights and recommendations for the transaction"""
        
        carbon_kg = final_estimate['carbon_kg']
        confidence = final_estimate['confidence']
        
        insights = {
            'carbon_intensity_level': self._categorize_carbon_intensity(carbon_kg, amount),
            'comparison_metrics': self._generate_comparison_metrics(carbon_kg),
            'recommendations': self._generate_recommendations(classification, carbon_kg, amount),
            'confidence_level': self._categorize_confidence(confidence),
            'data_quality': self._assess_data_quality(classification, final_estimate)
        }
        
        return insights
    
    def _categorize_carbon_intensity(self, carbon_kg: float, amount: float) -> Dict:
        """Categorize the carbon intensity of the transaction"""
        
        carbon_per_dollar = carbon_kg / max(amount, 1)
        
        if carbon_per_dollar < 0.1:
            level = 'Very Low'
            color = 'green'
            message = 'Excellent! This transaction has minimal carbon impact.'
        elif carbon_per_dollar < 0.3:
            level = 'Low'
            color = 'light_green'
            message = 'Good choice! Below average carbon intensity.'
        elif carbon_per_dollar < 0.6:
            level = 'Medium'
            color = 'yellow'
            message = 'Moderate carbon impact. Consider alternatives.'
        elif carbon_per_dollar < 1.0:
            level = 'High'
            color = 'orange'
            message = 'High carbon intensity. Look for greener options.'
        else:
            level = 'Very High'
            color = 'red'
            message = 'Very high carbon impact. Strong alternatives recommended.'
        
        return {
            'level': level,
            'carbon_per_dollar': carbon_per_dollar,
            'color': color,
            'message': message
        }
    
    def _generate_comparison_metrics(self, carbon_kg: float) -> Dict:
        """Generate relatable comparison metrics"""
        
        return {
            'equivalent_car_miles': carbon_kg / 0.404,
            'equivalent_tree_months': carbon_kg / (22 / 12),  # Trees absorb 22kg/year
            'equivalent_led_bulb_hours': carbon_kg / 0.00001,  # LED bulb emissions
            'equivalent_smartphone_charges': carbon_kg / 0.008,  # Phone charging
            'percentage_of_daily_average': (carbon_kg / (16000 / 365)) * 100  # US daily average
        }
    
    def _generate_recommendations(self, classification: TransactionClassification, 
                                carbon_kg: float, amount: float) -> List[Dict]:
        """Generate specific recommendations based on transaction"""
        
        recommendations = []
        
        if classification.category == 'Transportation':
            if carbon_kg > 10:  # High carbon transport
                recommendations.extend([
                    {
                        'title': 'Consider Public Transportation',
                        'description': 'Public transit can reduce emissions by up to 95%',
                        'potential_savings_kg': carbon_kg * 0.8,
                        'difficulty': 'Medium',
                        'cost_impact': 'Savings'
                    },
                    {
                        'title': 'Explore Electric Alternatives',
                        'description': 'Electric vehicles produce 60% fewer emissions',
                        'potential_savings_kg': carbon_kg * 0.6,
                        'difficulty': 'Hard',
                        'cost_impact': 'Investment'
                    }
                ])
        
        elif classification.category == 'Food':
            if 'meat' in classification.subcategory.lower() or carbon_kg > 5:
                recommendations.extend([
                    {
                        'title': 'Try Plant-Based Alternatives',
                        'description': 'Plant proteins have 90% lower carbon footprint',
                        'potential_savings_kg': carbon_kg * 0.9,
                        'difficulty': 'Easy',
                        'cost_impact': 'Neutral'
                    },
                    {
                        'title': 'Choose Local and Seasonal',
                        'description': 'Local food reduces transportation emissions',
                        'potential_savings_kg': carbon_kg * 0.2,
                        'difficulty': 'Easy',
                        'cost_impact': 'Slight increase'
                    }
                ])
        
        elif classification.category == 'Energy':
            recommendations.extend([
                {
                    'title': 'Switch to Renewable Energy',
                    'description': 'Renewable energy can eliminate 80% of emissions',
                    'potential_savings_kg': carbon_kg * 0.8,
                    'difficulty': 'Medium',
                    'cost_impact': 'Neutral'
                },
                {
                    'title': 'Improve Energy Efficiency',
                    'description': 'LED bulbs and smart thermostats reduce consumption',
                    'potential_savings_kg': carbon_kg * 0.3,
                    'difficulty': 'Easy',
                    'cost_impact': 'Savings'
                }
            ])
        
        return recommendations[:3]  # Return top 3 recommendations
    
    def _categorize_confidence(self, confidence: float) -> Dict:
        """Categorize the confidence level of the calculation"""
        
        if confidence >= 0.9:
            return {
                'level': 'Very High',
                'description': 'Calculation based on verified API data',
                'reliability': 'Excellent'
            }
        elif confidence >= 0.7:
            return {
                'level': 'High',
                'description': 'Calculation based on industry standards',
                'reliability': 'Good'
            }
        elif confidence >= 0.5:
            return {
                'level': 'Medium',
                'description': 'Calculation based on estimated data',
                'reliability': 'Fair'
            }
        else:
            return {
                'level': 'Low',
                'description': 'Calculation based on general estimates',
                'reliability': 'Limited'
            }
    
    def _assess_data_quality(self, classification: TransactionClassification, 
                           final_estimate: Dict) -> Dict:
        """Assess the quality of data used in calculations"""
        
        quality_factors = []
        
        # AI classification quality
        if classification.confidence > 0.8:
            quality_factors.append('High-confidence AI classification')
        elif classification.confidence > 0.5:
            quality_factors.append('Medium-confidence AI classification')
        else:
            quality_factors.append('Low-confidence AI classification')
        
        # Data source quality
        if 'api_' in final_estimate.get('details', {}).get('primary_source', ''):
            quality_factors.append('External API data used')
        else:
            quality_factors.append('Local calculation factors used')
        
        # Merchant recognition
        if classification.merchant_type == 'known_merchant':
            quality_factors.append('Merchant recognized in database')
        elif classification.merchant_type == 'nlp_extracted':
            quality_factors.append('Merchant extracted via NLP')
        else:
            quality_factors.append('Merchant classification estimated')
        
        return {
            'factors': quality_factors,
            'overall_score': min(classification.confidence + 0.2, 1.0),
            'improvement_suggestions': self._get_data_improvement_suggestions(classification)
        }
    
    def _get_data_improvement_suggestions(self, classification: TransactionClassification) -> List[str]:
        """Suggest ways to improve data quality"""
        
        suggestions = []
        
        if classification.confidence < 0.7:
            suggestions.append('Add more specific transaction descriptions')
        
        if not classification.location:
            suggestions.append('Include location data for more accurate calculations')
        
        if classification.merchant_type == 'keyword_matched':
            suggestions.append('Use more recognizable merchant names')
        
        return suggestions
    
    def _calculate_environmental_impact(self, carbon_kg: float) -> Dict:
        """Calculate broader environmental impact metrics"""
        
        return {
            'trees_to_offset': carbon_kg / 22,  # Trees needed to offset per year
            'car_free_days_equivalent': carbon_kg / (16000 / 365 * 0.3),  # Days of avoiding 30% of transport
            'led_bulb_years': carbon_kg / (10 * 0.00876),  # Years of LED bulb operation
            'water_footprint_liters': carbon_kg * 2.5,  # Approximate water impact
            'land_use_m2': carbon_kg * 0.1,  # Approximate land use impact
            'air_quality_impact': self._calculate_air_quality_impact(carbon_kg)
        }
    
    def _calculate_air_quality_impact(self, carbon_kg: float) -> Dict:
        """Calculate air quality impact beyond CO2"""
        
        # Rough estimates for other pollutants correlated with CO2
        return {
            'nox_grams': carbon_kg * 0.02,  # NOx emissions
            'pm25_grams': carbon_kg * 0.001,  # PM2.5 emissions
            'so2_grams': carbon_kg * 0.005,  # SO2 emissions
            'health_impact_score': min(carbon_kg * 0.1, 10)  # Relative health impact (0-10)
        }
    
    async def batch_process_transactions(self, transactions: List[Dict], 
                                       user_preferences: Dict = None) -> List[Dict]:
        """Process multiple transactions efficiently with AI and API integration"""
        
        # Step 1: Batch AI parsing
        parsed_transactions = self.ai_parser.batch_parse_transactions(transactions)
        
        # Step 2: Batch API processing for high-confidence classifications
        api_enhanced_transactions = await self.api_integrator.batch_estimate_transactions(
            parsed_transactions
        )
        
        # Step 3: Process each transaction with full enhancement
        enhanced_transactions = []
        
        for transaction in api_enhanced_transactions:
            try:
                # Create classification object from parsed data
                classification = TransactionClassification(
                    category=transaction.get('ai_category', 'Other'),
                    subcategory=transaction.get('ai_subcategory', ''),
                    confidence=transaction.get('ai_confidence', 0.5),
                    carbon_intensity=transaction.get('ai_carbon_intensity', 'medium'),
                    merchant_type=transaction.get('ai_merchant_type', 'unknown'),
                    location=transaction.get('ai_location')
                )
                
                # Prepare estimates from API data
                estimates = {'local': {
                    'carbon_kg': transaction.get('carbon_kg', 0),
                    'confidence': 0.7,
                    'source': 'Local Calculator',
                    'method': 'EPA factors'
                }}
                
                # Add API estimates if available
                if transaction.get('api_carbon_kg'):
                    estimates['api_primary'] = {
                        'carbon_kg': transaction['api_carbon_kg'],
                        'confidence': transaction.get('api_confidence', 0.8),
                        'source': transaction.get('api_source', 'API'),
                        'method': transaction.get('api_methodology', 'API')
                    }
                
                # Calculate final estimate
                final_estimate = self._calculate_weighted_estimate(estimates, classification)
                
                # Generate insights
                insights = self._generate_transaction_insights(
                    classification, final_estimate, transaction.get('amount', 0)
                )
                
                # Create enhanced transaction
                enhanced_transaction = transaction.copy()
                enhanced_transaction.update({
                    'final_carbon_kg': final_estimate['carbon_kg'],
                    'final_confidence': final_estimate['confidence'],
                    'calculation_method': final_estimate['method'],
                    'insights': insights,
                    'environmental_impact': self._calculate_environmental_impact(
                        final_estimate['carbon_kg']
                    ),
                    'processed_at': datetime.now().isoformat()
                })
                
                enhanced_transactions.append(enhanced_transaction)
                
            except Exception as e:
                print(f"Error processing transaction: {e}")
                enhanced_transactions.append(transaction)
        
        return enhanced_transactions
    
    def get_processing_statistics(self, processed_transactions: List[Dict]) -> Dict:
        """Get comprehensive statistics about the processing pipeline"""
        
        if not processed_transactions:
            return {}
        
        # AI parsing statistics
        ai_stats = self.ai_parser.get_parsing_statistics(processed_transactions)
        
        # Carbon calculation statistics
        total_carbon = sum(t.get('final_carbon_kg', 0) for t in processed_transactions)
        avg_confidence = sum(t.get('final_confidence', 0) for t in processed_transactions) / len(processed_transactions)
        
        # Method distribution
        method_distribution = {}
        for transaction in processed_transactions:
            method = transaction.get('calculation_method', 'Unknown')
            method_distribution[method] = method_distribution.get(method, 0) + 1
        
        # API usage statistics
        api_usage = {
            'total_api_calls': sum(1 for t in processed_transactions if t.get('api_carbon_kg')),
            'api_success_rate': 0,
            'primary_api_sources': {}
        }
        
        if api_usage['total_api_calls'] > 0:
            api_usage['api_success_rate'] = (api_usage['total_api_calls'] / len(processed_transactions)) * 100
            
            for transaction in processed_transactions:
                if transaction.get('api_source'):
                    source = transaction['api_source']
                    api_usage['primary_api_sources'][source] = api_usage['primary_api_sources'].get(source, 0) + 1
        
        return {
            'total_transactions': len(processed_transactions),
            'total_carbon_kg': total_carbon,
            'average_carbon_per_transaction': total_carbon / len(processed_transactions),
            'average_confidence': avg_confidence,
            'ai_parsing_stats': ai_stats,
            'method_distribution': method_distribution,
            'api_usage_stats': api_usage,
            'environmental_impact_summary': {
                'trees_to_offset': total_carbon / 22,
                'car_miles_equivalent': total_carbon / 0.404,
                'percentage_of_annual_us_average': (total_carbon / 16000) * 100
            }
        }
