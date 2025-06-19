import pandas as pd
import numpy as np
import requests
import json
from typing import List, Dict, Tuple
import kaggle
from pathlib import Path
import sqlite3
from datetime import datetime, timedelta
import random
import re

class TransactionDataCollector:
    def __init__(self):
        """Initialize data collector for transaction classification training"""
        
        # Kaggle datasets for transaction classification
        self.kaggle_datasets = {
            'transaction_classification': [
                'ealaxi/paysim1',  # Mobile money transactions
                'mlg-ulb/creditcardfraud',  # Credit card transactions
                'aabhinavbhat/bank-account-transactions',  # Bank transactions
                'shashwatwork/financial-transactions',  # Financial data
                'mrcsw/financial-transactions',  # Transactional data
                'uciml/bank-marketing',  # Banking data
                'bennykas/bank-transactions',  # Personal bank transactions
                'ahmadshaikhha/financial-transactions',  # Financial patterns
            ],
            'merchant_classification': [
                'bansalkanav/restaurant-recommendation-system',  # Restaurant data
                'yelp-dataset/yelp-dataset',  # Business categories
                'retailrocket/ecommerce-dataset',  # E-commerce transactions
                'carrie1/ecommerce-data',  # Online retail
                'olistbr/brazilian-ecommerce',  # Brazilian e-commerce
                'nicapotato/womens-ecommerce-clothing-reviews',  # Retail
            ],
            'carbon_emissions': [
                'sovitrath/carbon-emissions',  # Carbon emissions data
                'venkat2709/co2-emissions-dataset',  # CO2 emissions
                'ulrikthygepedersen/co2-emissions-by-country',  # Country emissions
                'cityofLA/los-angeles-international-airport',  # Transportation
                'epa/greenhouse-gas-reporting-program',  # EPA emissions
                'berkeleyearth/climate-change-earth-surface-temperature',  # Climate
                'census/population-estimates',  # Demographics for scaling
            ],
            'energy_consumption': [
                'robikscube/hourly-energy-consumption',  # Energy patterns
                'fedesoriano/renewable-energy-world-wide',  # Renewable energy
                'berkeleyearth/electricity-generation',  # Power generation
                'uciml/electric-power-consumption',  # Power consumption
            ]
        }
        
        # Alternative data sources
        self.alternative_sources = {
            'openstreetmap': 'https://overpass-api.de/api/interpreter',
            'foursquare': 'https://api.foursquare.com/v3/places/search',
            'yelp': 'https://api.yelp.com/v3/businesses/search',
            'epa_api': 'https://www.epa.gov/enviro/web-services',
            'world_bank': 'https://api.worldbank.org/v2'
        }
    
    def download_kaggle_datasets(self, output_dir: str = "training_data") -> Dict[str, List[str]]:
        """Download relevant datasets from Kaggle"""
        
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        downloaded_files = {}
        
        for category, datasets in self.kaggle_datasets.items():
            category_path = output_path / category
            category_path.mkdir(exist_ok=True)
            
            downloaded_files[category] = []
            
            for dataset in datasets:
                try:
                    print(f"Downloading {dataset}...")
                    kaggle.api.dataset_download_files(
                        dataset, 
                        path=str(category_path),
                        unzip=True
                    )
                    downloaded_files[category].append(dataset)
                    print(f"✅ Downloaded {dataset}")
                    
                except Exception as e:
                    print(f"❌ Failed to download {dataset}: {e}")
        
        return downloaded_files
    
    def generate_synthetic_transactions(self, num_transactions: int = 10000) -> pd.DataFrame:
        """Generate synthetic transaction data for training"""
        
        # Merchant categories with typical spending patterns
        merchant_patterns = {
            'Transportation': {
                'merchants': ['Shell', 'Chevron', 'Exxon', 'BP', 'Uber', 'Lyft', 'Metro', 'Delta', 'United'],
                'amount_range': (15, 200),
                'carbon_intensity': {'low': 0.1, 'medium': 0.3, 'high': 0.6},
                'keywords': ['gas', 'fuel', 'station', 'ride', 'flight', 'airline', 'parking']
            },
            'Food': {
                'merchants': ['McDonalds', 'Starbucks', 'Whole Foods', 'Safeway', 'Subway', 'Pizza Hut'],
                'amount_range': (5, 150),
                'carbon_intensity': {'low': 0.2, 'medium': 0.5, 'high': 0.3},
                'keywords': ['restaurant', 'cafe', 'grocery', 'food', 'market', 'deli']
            },
            'Energy': {
                'merchants': ['PG&E', 'Con Edison', 'Duke Energy', 'Southern Company', 'National Grid'],
                'amount_range': (50, 300),
                'carbon_intensity': {'low': 0.1, 'medium': 0.4, 'high': 0.5},
                'keywords': ['electric', 'utility', 'power', 'energy', 'gas company']
            },
            'Shopping': {
                'merchants': ['Amazon', 'Target', 'Walmart', 'Best Buy', 'Apple Store', 'Home Depot'],
                'amount_range': (10, 500),
                'carbon_intensity': {'low': 0.3, 'medium': 0.5, 'high': 0.2},
                'keywords': ['store', 'shop', 'retail', 'mall', 'online', 'purchase']
            },
            'Entertainment': {
                'merchants': ['Netflix', 'Spotify', 'AMC Theaters', 'Gym', 'Steam', 'PlayStation'],
                'amount_range': (8, 100),
                'carbon_intensity': {'low': 0.7, 'medium': 0.2, 'high': 0.1},
                'keywords': ['entertainment', 'streaming', 'game', 'movie', 'gym', 'fitness']
            }
        }
        
        transactions = []
        
        for i in range(num_transactions):
            # Select random category
            category = random.choice(list(merchant_patterns.keys()))
            pattern = merchant_patterns[category]
            
            # Generate transaction details
            merchant = random.choice(pattern['merchants'])
            amount = round(random.uniform(*pattern['amount_range']), 2)
            
            # Generate realistic description
            description = self._generate_transaction_description(merchant, pattern['keywords'])
            
            # Calculate carbon footprint based on category and amount
            carbon_kg = self._calculate_synthetic_carbon(category, amount, merchant)
            
            # Add some noise and variations
            confidence = random.uniform(0.7, 1.0)
            date = datetime.now() - timedelta(days=random.randint(0, 365))
            
            transaction = {
                'id': i,
                'description': description,
                'amount': amount,
                'category': category,
                'merchant': merchant,
                'carbon_kg': carbon_kg,
                'date': date.strftime('%Y-%m-%d'),
                'confidence': confidence,
                'subcategory': self._get_subcategory(category, merchant),
                'location': self._generate_location(),
                'carbon_intensity': self._categorize_carbon_intensity(carbon_kg, amount)
            }
            
            transactions.append(transaction)
        
        return pd.DataFrame(transactions)
    
    def _generate_transaction_description(self, merchant: str, keywords: List[str]) -> str:
        """Generate realistic transaction descriptions"""
        
        templates = [
            f"{merchant}",
            f"{merchant} #{random.randint(1000, 9999)}",
            f"POS {merchant}",
            f"{merchant} Store #{random.randint(100, 999)}",
            f"{merchant.upper()} {random.choice(keywords).upper()}",
            f"PURCHASE {merchant}",
            f"{merchant} - {random.choice(keywords)}",
            f"DEBIT {merchant}",
            f"{merchant} PAYMENT",
            f"CARD PURCHASE {merchant}"
        ]
        
        base_description = random.choice(templates)
        
        # Add location codes sometimes
        if random.random() < 0.3:
            base_description += f" {random.choice(['CA', 'NY', 'TX', 'FL', 'WA'])}"
        
        # Add reference numbers sometimes
        if random.random() < 0.4:
            base_description += f" *{random.randint(1000, 9999)}"
        
        return base_description
    
    def _calculate_synthetic_carbon(self, category: str, amount: float, merchant: str) -> float:
        """Calculate synthetic carbon footprint with realistic patterns"""
        
        # Base emission factors per dollar spent
        base_factors = {
            'Transportation': 0.8,  # High carbon per dollar
            'Energy': 0.4,          # Medium carbon per dollar
            'Food': 0.3,            # Variable carbon per dollar
            'Shopping': 0.2,        # Lower carbon per dollar
            'Entertainment': 0.1    # Low carbon per dollar
        }
        
        base_carbon = amount * base_factors.get(category, 0.3)
        
        # Merchant-specific multipliers
        high_carbon_merchants = ['Shell', 'Chevron', 'McDonalds', 'Delta', 'United']
        low_carbon_merchants = ['Netflix', 'Spotify', 'Whole Foods', 'Metro']
        
        if merchant in high_carbon_merchants:
            multiplier = random.uniform(1.5, 2.5)
        elif merchant in low_carbon_merchants:
            multiplier = random.uniform(0.3, 0.8)
        else:
            multiplier = random.uniform(0.8, 1.5)
        
        # Add some randomness
        noise = random.uniform(0.8, 1.2)
        
        return round(base_carbon * multiplier * noise, 2)
    
    def _get_subcategory(self, category: str, merchant: str) -> str:
        """Get subcategory based on merchant"""
        
        subcategory_mapping = {
            'Transportation': {
                'Shell': 'gasoline', 'Chevron': 'gasoline', 'Exxon': 'gasoline',
                'Uber': 'rideshare', 'Lyft': 'rideshare', 'Metro': 'public_transport',
                'Delta': 'flight', 'United': 'flight'
            },
            'Food': {
                'McDonalds': 'fast_food', 'Starbucks': 'coffee',
                'Whole Foods': 'organic_grocery', 'Safeway': 'grocery'
            },
            'Energy': {
                'PG&E': 'electricity', 'Con Edison': 'electricity'
            },
            'Shopping': {
                'Amazon': 'online_retail', 'Best Buy': 'electronics'
            },
            'Entertainment': {
                'Netflix': 'streaming', 'AMC Theaters': 'movies'
            }
        }
        
        return subcategory_mapping.get(category, {}).get(merchant, 'general')
    
    def _generate_location(self) -> str:
        """Generate random location data"""
        
        locations = [
            'San Francisco, CA', 'New York, NY', 'Los Angeles, CA',
            'Chicago, IL', 'Houston, TX', 'Phoenix, AZ', 'Philadelphia, PA',
            'San Antonio, TX', 'San Diego, CA', 'Dallas, TX', 'San Jose, CA',
            'Austin, TX', 'Jacksonville, FL', 'Fort Worth, TX', 'Columbus, OH'
        ]
        
        return random.choice(locations) if random.random() < 0.6 else None
    
    def _categorize_carbon_intensity(self, carbon_kg: float, amount: float) -> str:
        """Categorize carbon intensity"""
        
        carbon_per_dollar = carbon_kg / max(amount, 1)
        
        if carbon_per_dollar < 0.1:
            return 'very_low'
        elif carbon_per_dollar < 0.3:
            return 'low'
        elif carbon_per_dollar < 0.6:
            return 'medium'
        elif carbon_per_dollar < 1.0:
            return 'high'
        else:
            return 'very_high'
    
    def collect_real_merchant_data(self) -> pd.DataFrame:
        """Collect real merchant data from various sources"""
        
        merchants_data = []
        
        # Common merchant chains with categories
        merchant_database = {
            # Transportation
            'Shell': {'category': 'Transportation', 'subcategory': 'gasoline', 'carbon_factor': 0.8},
            'Chevron': {'category': 'Transportation', 'subcategory': 'gasoline', 'carbon_factor': 0.8},
            'ExxonMobil': {'category': 'Transportation', 'subcategory': 'gasoline', 'carbon_factor': 0.85},
            'BP': {'category': 'Transportation', 'subcategory': 'gasoline', 'carbon_factor': 0.75},
            'Uber': {'category': 'Transportation', 'subcategory': 'rideshare', 'carbon_factor': 0.5},
            'Lyft': {'category': 'Transportation', 'subcategory': 'rideshare', 'carbon_factor': 0.5},
            'Delta Air Lines': {'category': 'Transportation', 'subcategory': 'flight', 'carbon_factor': 2.5},
            'United Airlines': {'category': 'Transportation', 'subcategory': 'flight', 'carbon_factor': 2.4},
            'American Airlines': {'category': 'Transportation', 'subcategory': 'flight', 'carbon_factor': 2.6},
            
            # Food & Dining
            'McDonalds': {'category': 'Food', 'subcategory': 'fast_food', 'carbon_factor': 0.4},
            'Burger King': {'category': 'Food', 'subcategory': 'fast_food', 'carbon_factor': 0.45},
            'KFC': {'category': 'Food', 'subcategory': 'fast_food', 'carbon_factor': 0.5},
            'Starbucks': {'category': 'Food', 'subcategory': 'coffee', 'carbon_factor': 0.2},
            'Dunkin': {'category': 'Food', 'subcategory': 'coffee', 'carbon_factor': 0.25},
            'Subway': {'category': 'Food', 'subcategory': 'fast_food', 'carbon_factor': 0.3},
            'Whole Foods': {'category': 'Food', 'subcategory': 'organic_grocery', 'carbon_factor': 0.15},
            'Safeway': {'category': 'Food', 'subcategory': 'grocery', 'carbon_factor': 0.25},
            'Kroger': {'category': 'Food', 'subcategory': 'grocery', 'carbon_factor': 0.28},
            'Trader Joes': {'category': 'Food', 'subcategory': 'grocery', 'carbon_factor': 0.2},
            
            # Energy & Utilities
            'PG&E': {'category': 'Energy', 'subcategory': 'electricity', 'carbon_factor': 0.3},
            'ConEd': {'category': 'Energy', 'subcategory': 'electricity', 'carbon_factor': 0.4},
            'Duke Energy': {'category': 'Energy', 'subcategory': 'electricity', 'carbon_factor': 0.5},
            'Southern Company': {'category': 'Energy', 'subcategory': 'electricity', 'carbon_factor': 0.6},
            
            # Shopping & Retail
            'Amazon': {'category': 'Shopping', 'subcategory': 'online_retail', 'carbon_factor': 0.2},
            'Target': {'category': 'Shopping', 'subcategory': 'retail', 'carbon_factor': 0.25},
            'Walmart': {'category': 'Shopping', 'subcategory': 'retail', 'carbon_factor': 0.3},
            'Best Buy': {'category': 'Shopping', 'subcategory': 'electronics', 'carbon_factor': 0.4},
            'Apple Store': {'category': 'Shopping', 'subcategory': 'electronics', 'carbon_factor': 0.35},
            'Home Depot': {'category': 'Shopping', 'subcategory': 'home_improvement', 'carbon_factor': 0.3},
            'Lowes': {'category': 'Shopping', 'subcategory': 'home_improvement', 'carbon_factor': 0.32},
            
            # Entertainment
            'Netflix': {'category': 'Entertainment', 'subcategory': 'streaming', 'carbon_factor': 0.01},
            'Spotify': {'category': 'Entertainment', 'subcategory': 'streaming', 'carbon_factor': 0.005},
            'AMC Theaters': {'category': 'Entertainment', 'subcategory': 'movies', 'carbon_factor': 0.1},
            'Planet Fitness': {'category': 'Entertainment', 'subcategory': 'fitness', 'carbon_factor': 0.05},
        }
        
        for merchant, data in merchant_database.items():
            merchants_data.append({
                'merchant_name': merchant,
                'category': data['category'],
                'subcategory': data['subcategory'],
                'carbon_factor_per_dollar': data['carbon_factor'],
                'data_source': 'manual_compilation'
            })
        
        return pd.DataFrame(merchants_data)
    
    def create_training_dataset(self, output_file: str = "transaction_training_data.csv") -> str:
        """Create comprehensive training dataset"""
        
        print("🔄 Generating synthetic transactions...")
        synthetic_data = self.generate_synthetic_transactions(10000)
        
        print("🔄 Collecting merchant data...")
        merchant_data = self.collect_real_merchant_data()
        
        # Enhance synthetic data with merchant information
        enhanced_data = self.enhance_with_merchant_data(synthetic_data, merchant_data)
        
        # Add features for model training
        final_data = self.add_training_features(enhanced_data)
        
        # Save to file
        final_data.to_csv(output_file, index=False)
        print(f"✅ Training dataset saved to {output_file}")
        print(f"📊 Dataset contains {len(final_data)} transactions")
        
        return output_file
    
    def enhance_with_merchant_data(self, transactions: pd.DataFrame, merchants: pd.DataFrame) -> pd.DataFrame:
        """Enhance transaction data with merchant information"""
        
        # Create merchant lookup
        merchant_lookup = merchants.set_index('merchant_name').to_dict('index')
        
        # Add merchant-specific carbon factors
        def get_merchant_carbon_factor(merchant):
            return merchant_lookup.get(merchant, {}).get('carbon_factor_per_dollar', 0.3)
        
        transactions['merchant_carbon_factor'] = transactions['merchant'].apply(get_merchant_carbon_factor)
        
        return transactions
    
    def add_training_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """Add features for model training"""
        
        # Text features from description
        data['description_length'] = data['description'].str.len()
        data['description_word_count'] = data['description'].str.split().str.len()
        data['has_numbers'] = data['description'].str.contains(r'\d').astype(int)
        data['has_special_chars'] = data['description'].str.contains(r'[*#&]').astype(int)
        
        # Amount features
        data['amount_log'] = np.log1p(data['amount'])
        data['amount_squared'] = data['amount'] ** 2
        data['amount_category'] = pd.cut(data['amount'], bins=5, labels=['very_low', 'low', 'medium', 'high', 'very_high'])
        
        # Date features
        data['date'] = pd.to_datetime(data['date'])
        data['day_of_week'] = data['date'].dt.dayofweek
        data['month'] = data['date'].dt.month
        data['is_weekend'] = (data['day_of_week'] >= 5).astype(int)
        
        # Carbon features
        data['carbon_per_dollar'] = data['carbon_kg'] / data['amount']
        data['carbon_category'] = pd.cut(data['carbon_per_dollar'], 
                                       bins=[0, 0.1, 0.3, 0.6, 1.0, float('inf')],
                                       labels=['very_low', 'low', 'medium', 'high', 'very_high'])
        
        return data

class CarbonEmissionDataCollector:
    def __init__(self):
        """Collect carbon emission data for training carbon estimation models"""
        
        self.emission_factor_sources = {
            'epa_egrid': 'https://www.epa.gov/egrid/download-data',
            'ipcc_factors': 'https://www.ipcc-nggip.iges.or.jp/public/2006gl/',
            'defra_factors': 'https://www.gov.uk/government/collections/government-conversion-factors-for-company-reporting',
            'carbonfund': 'https://carbonfund.org/calculation-methods/',
        }
    
    def collect_emission_factors(self) -> pd.DataFrame:
        """Collect comprehensive emission factors"""
        
        # Comprehensive emission factors database
        emission_factors = [
            # Transportation
            {'category': 'Transportation', 'subcategory': 'gasoline_car', 'unit': 'mile', 'kg_co2_per_unit': 0.404, 'source': 'EPA'},
            {'category': 'Transportation', 'subcategory': 'diesel_car', 'unit': 'mile', 'kg_co2_per_unit': 0.463, 'source': 'EPA'},
            {'category': 'Transportation', 'subcategory': 'hybrid_car', 'unit': 'mile', 'kg_co2_per_unit': 0.200, 'source': 'EPA'},
            {'category': 'Transportation', 'subcategory': 'electric_car', 'unit': 'mile', 'kg_co2_per_unit': 0.180, 'source': 'EPA'},
            {'category': 'Transportation', 'subcategory': 'motorcycle', 'unit': 'mile', 'kg_co2_per_unit': 0.280, 'source': 'EPA'},
            {'category': 'Transportation', 'subcategory': 'bus', 'unit': 'passenger_mile', 'kg_co2_per_unit': 0.080, 'source': 'EPA'},
            {'category': 'Transportation', 'subcategory': 'train', 'unit': 'passenger_mile', 'kg_co2_per_unit': 0.060, 'source': 'EPA'},
            {'category': 'Transportation', 'subcategory': 'subway', 'unit': 'passenger_mile', 'kg_co2_per_unit': 0.040, 'source': 'EPA'},
            {'category': 'Transportation', 'subcategory': 'flight_domestic', 'unit': 'passenger_mile', 'kg_co2_per_unit': 0.255, 'source': 'EPA'},
            {'category': 'Transportation', 'subcategory': 'flight_international', 'unit': 'passenger_mile', 'kg_co2_per_unit': 0.195, 'source': 'EPA'},
            
            # Energy
            {'category': 'Energy', 'subcategory': 'electricity_us_avg', 'unit': 'kwh', 'kg_co2_per_unit': 0.500, 'source': 'EPA_eGRID'},
            {'category': 'Energy', 'subcategory': 'electricity_coal', 'unit': 'kwh', 'kg_co2_per_unit': 0.820, 'source': 'IPCC'},
            {'category': 'Energy', 'subcategory': 'electricity_natural_gas', 'unit': 'kwh', 'kg_co2_per_unit': 0.350, 'source': 'IPCC'},
            {'category': 'Energy', 'subcategory': 'electricity_renewable', 'unit': 'kwh', 'kg_co2_per_unit': 0.020, 'source': 'IPCC'},
            {'category': 'Energy', 'subcategory': 'natural_gas_heating', 'unit': 'therm', 'kg_co2_per_unit': 5.3, 'source': 'EPA'},
            {'category': 'Energy', 'subcategory': 'heating_oil', 'unit': 'gallon', 'kg_co2_per_unit': 10.15, 'source': 'EPA'},
            {'category': 'Energy', 'subcategory': 'propane', 'unit': 'gallon', 'kg_co2_per_unit': 5.75, 'source': 'EPA'},
            
            # Food
            {'category': 'Food', 'subcategory': 'beef', 'unit': 'kg', 'kg_co2_per_unit': 60.0, 'source': 'Poore_Nemecek_2018'},
            {'category': 'Food', 'subcategory': 'lamb', 'unit': 'kg', 'kg_co2_per_unit': 39.2, 'source': 'Poore_Nemecek_2018'},
            {'category': 'Food', 'subcategory': 'pork', 'unit': 'kg', 'kg_co2_per_unit': 12.1, 'source': 'Poore_Nemecek_2018'},
            {'category': 'Food', 'subcategory': 'chicken', 'unit': 'kg', 'kg_co2_per_unit': 6.9, 'source': 'Poore_Nemecek_2018'},
            {'category': 'Food', 'subcategory': 'fish_farmed', 'unit': 'kg', 'kg_co2_per_unit': 5.4, 'source': 'Poore_Nemecek_2018'},
            {'category': 'Food', 'subcategory': 'fish_wild', 'unit': 'kg', 'kg_co2_per_unit': 2.9, 'source': 'Poore_Nemecek_2018'},
            {'category': 'Food', 'subcategory': 'dairy_milk', 'unit': 'liter', 'kg_co2_per_unit': 3.2, 'source': 'Poore_Nemecek_2018'},
            {'category': 'Food', 'subcategory': 'cheese', 'unit': 'kg', 'kg_co2_per_unit': 13.5, 'source': 'Poore_Nemecek_2018'},
            {'category': 'Food', 'subcategory': 'eggs', 'unit': 'dozen', 'kg_co2_per_unit': 4.2, 'source': 'Poore_Nemecek_2018'},
            {'category': 'Food', 'subcategory': 'rice', 'unit': 'kg', 'kg_co2_per_unit': 2.7, 'source': 'Poore_Nemecek_2018'},
            {'category': 'Food', 'subcategory': 'wheat_bread', 'unit': 'kg', 'kg_co2_per_unit': 0.9, 'source': 'Poore_Nemecek_2018'},
            {'category': 'Food', 'subcategory': 'vegetables_avg', 'unit': 'kg', 'kg_co2_per_unit': 0.4, 'source': 'Poore_Nemecek_2018'},
            {'category': 'Food', 'subcategory': 'fruits_avg', 'unit': 'kg', 'kg_co2_per_unit': 0.3, 'source': 'Poore_Nemecek_2018'},
            
            # Manufacturing & Materials
            {'category': 'Manufacturing', 'subcategory': 'steel', 'unit': 'kg', 'kg_co2_per_unit': 2.3, 'source': 'IPCC'},
            {'category': 'Manufacturing', 'subcategory': 'aluminum', 'unit': 'kg', 'kg_co2_per_unit': 8.2, 'source': 'IPCC'},
            {'category': 'Manufacturing', 'subcategory': 'cement', 'unit': 'kg', 'kg_co2_per_unit': 0.9, 'source': 'IPCC'},
            {'category': 'Manufacturing', 'subcategory': 'plastic', 'unit': 'kg', 'kg_co2_per_unit': 2.0, 'source': 'IPCC'},
            {'category': 'Manufacturing', 'subcategory': 'paper', 'unit': 'kg', 'kg_co2_per_unit': 1.3, 'source': 'IPCC'},
            {'category': 'Manufacturing', 'subcategory': 'glass', 'unit': 'kg', 'kg_co2_per_unit': 0.5, 'source': 'IPCC'},
            
            # Regional electricity factors (US states)
            {'category': 'Energy', 'subcategory': 'electricity_california', 'unit': 'kwh', 'kg_co2_per_unit': 0.200, 'source': 'EPA_eGRID_2021'},
            {'category': 'Energy', 'subcategory': 'electricity_texas', 'unit': 'kwh', 'kg_co2_per_unit': 0.450, 'source': 'EPA_eGRID_2021'},
            {'category': 'Energy', 'subcategory': 'electricity_new_york', 'unit': 'kwh', 'kg_co2_per_unit': 0.280, 'source': 'EPA_eGRID_2021'},
            {'category': 'Energy', 'subcategory': 'electricity_florida', 'unit': 'kwh', 'kg_co2_per_unit': 0.520, 'source': 'EPA_eGRID_2021'},
            {'category': 'Energy', 'subcategory': 'electricity_washington', 'unit': 'kwh', 'kg_co2_per_unit': 0.110, 'source': 'EPA_eGRID_2021'},
            {'category': 'Energy', 'subcategory': 'electricity_west_virginia', 'unit': 'kwh', 'kg_co2_per_unit': 0.720, 'source': 'EPA_eGRID_2021'},
        ]
        
        return pd.DataFrame(emission_factors)
    
    def create_carbon_estimation_dataset(self, output_file: str = "carbon_estimation_training.csv") -> str:
        """Create dataset for training carbon estimation models"""
        
        # Get emission factors
        emission_factors = self.collect_emission_factors()
        
        # Generate training examples
        training_data = []
        
        for _, factor in emission_factors.iterrows():
            # Generate multiple training examples per emission factor
            for i in range(100):  # 100 examples per factor
                # Generate realistic activity amounts
                if factor['unit'] == 'mile':
                    amount = random.uniform(10, 500)  # miles
                elif factor['unit'] == 'kwh':
                    amount = random.uniform(100, 2000)  # kWh
                elif factor['unit'] == 'gallon':
                    amount = random.uniform(5, 30)  # gallons
                elif factor['unit'] == 'kg':
                    amount = random.uniform(0.5, 5)  # kg
                elif factor['unit'] == 'therm':
                    amount = random.uniform(50, 200)  # therms
                else:
                    amount = random.uniform(1, 10)
                
                # Calculate carbon emissions
                carbon_kg = amount * factor['kg_co2_per_unit']
                
                # Add some realistic noise (±10%)
                noise_factor = random.uniform(0.9, 1.1)
                carbon_kg_noisy = carbon_kg * noise_factor
                
                training_example = {
                    'category': factor['category'],
                    'subcategory': factor['subcategory'],
                    'activity_amount': amount,
                    'activity_unit': factor['unit'],
                    'true_emission_factor': factor['kg_co2_per_unit'],
                    'calculated_carbon_kg': carbon_kg,
                    'noisy_carbon_kg': carbon_kg_noisy,
                    'data_source': factor['source'],
                    'uncertainty': abs(carbon_kg_noisy - carbon_kg) / carbon_kg * 100
                }
                
                training_data.append(training_example)
        
        # Convert to DataFrame and save
        df = pd.DataFrame(training_data)
        df.to_csv(output_file, index=False)
        
        print(f"✅ Carbon estimation dataset saved to {output_file}")
        print(f"📊 Dataset contains {len(df)} training examples")
        
        return output_file

def main():
    """Main function to collect all training data"""
    
    print("🚀 Starting data collection for model training...")
    
    # Initialize collectors
    transaction_collector = TransactionDataCollector()
    carbon_collector = CarbonEmissionDataCollector()
    
    # Create output directory
    Path("training_data").mkdir(exist_ok=True)
    
    # Collect transaction classification data
    print("\n1. Creating transaction classification dataset...")
    transaction_file = transaction_collector.create_training_dataset("training_data/transaction_training_data.csv")
    
    # Collect carbon estimation data
    print("\n2. Creating carbon estimation dataset...")
    carbon_file = carbon_collector.create_carbon_estimation_dataset("training_data/carbon_estimation_training.csv")
    
    print("\n🎉 Data collection complete!")
    print(f"\n📁 Files created:")
    print(f"   - {transaction_file}")
    print(f"   - {carbon_file}")
    
    print(f"\n📋 Next steps:")
    print(f"   1. Review the generated datasets")
    print(f"   2. Download additional Kaggle datasets")
    print(f"   3. Train the models using train_models.py")

if __name__ == "__main__":
    main()
