import re
import json
import requests
from typing import Dict, List, Tuple, Optional
import pandas as pd
from datetime import datetime
import spacy
from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
import numpy as np
from dataclasses import dataclass

@dataclass
class TransactionClassification:
    category: str
    subcategory: str
    confidence: float
    carbon_intensity: str  # low, medium, high
    merchant_type: str
    location: Optional[str] = None

class AITransactionParser:
    def __init__(self):
        """Initialize AI-powered transaction parser with multiple models"""
        
        # Load spaCy model for NER
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            print("Warning: spaCy model not found. Install with: python -m spacy download en_core_web_sm")
            self.nlp = None
        
        # Initialize BERT-based classification model
        self.setup_classification_model()
        
        # Merchant and category databases
        self.merchant_database = self.load_merchant_database()
        self.category_keywords = self.load_category_keywords()
        self.carbon_intensity_patterns = self.load_carbon_patterns()
        
        # Location extraction patterns
        self.location_patterns = [
            r'\b([A-Z]{2})\b',  # State codes
            r'\b(\d{5})\b',     # ZIP codes
            r'#(\d+)',          # Store numbers
        ]
    
    def setup_classification_model(self):
        """Setup BERT-based transaction classification model"""
        try:
            # Use a pre-trained model or fine-tuned model for transaction classification
            model_name = "microsoft/DialoGPT-medium"  # Placeholder - would use custom trained model
            self.tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")
            
            # For demo, we'll use a simple classification pipeline
            self.classifier = pipeline(
                "text-classification",
                model="facebook/bart-large-mnli",
                return_all_scores=True
            )
            
            # Define candidate labels for zero-shot classification
            self.category_labels = [
                "transportation and fuel",
                "food and dining",
                "energy and utilities",
                "shopping and retail",
                "entertainment and recreation",
                "healthcare and medical",
                "other services"
            ]
            
        except Exception as e:
            print(f"Warning: Could not load classification model: {e}")
            self.classifier = None
            self.tokenizer = None
    
    def load_merchant_database(self) -> Dict:
        """Load comprehensive merchant database with carbon intensity"""
        return {
            # Gas Stations & Fuel
            'shell': {'category': 'Transportation', 'subcategory': 'gasoline', 'carbon_intensity': 'high'},
            'exxon': {'category': 'Transportation', 'subcategory': 'gasoline', 'carbon_intensity': 'high'},
            'chevron': {'category': 'Transportation', 'subcategory': 'gasoline', 'carbon_intensity': 'high'},
            'bp': {'category': 'Transportation', 'subcategory': 'gasoline', 'carbon_intensity': 'high'},
            'mobil': {'category': 'Transportation', 'subcategory': 'gasoline', 'carbon_intensity': 'high'},
            'arco': {'category': 'Transportation', 'subcategory': 'gasoline', 'carbon_intensity': 'high'},
            'valero': {'category': 'Transportation', 'subcategory': 'gasoline', 'carbon_intensity': 'high'},
            
            # Transportation Services
            'uber': {'category': 'Transportation', 'subcategory': 'rideshare', 'carbon_intensity': 'medium'},
            'lyft': {'category': 'Transportation', 'subcategory': 'rideshare', 'carbon_intensity': 'medium'},
            'taxi': {'category': 'Transportation', 'subcategory': 'taxi', 'carbon_intensity': 'medium'},
            'metro': {'category': 'Transportation', 'subcategory': 'public_transport', 'carbon_intensity': 'low'},
            'mta': {'category': 'Transportation', 'subcategory': 'public_transport', 'carbon_intensity': 'low'},
            'bart': {'category': 'Transportation', 'subcategory': 'public_transport', 'carbon_intensity': 'low'},
            'amtrak': {'category': 'Transportation', 'subcategory': 'train', 'carbon_intensity': 'low'},
            
            # Airlines
            'delta': {'category': 'Transportation', 'subcategory': 'flight', 'carbon_intensity': 'very_high'},
            'united': {'category': 'Transportation', 'subcategory': 'flight', 'carbon_intensity': 'very_high'},
            'american': {'category': 'Transportation', 'subcategory': 'flight', 'carbon_intensity': 'very_high'},
            'southwest': {'category': 'Transportation', 'subcategory': 'flight', 'carbon_intensity': 'very_high'},
            'jetblue': {'category': 'Transportation', 'subcategory': 'flight', 'carbon_intensity': 'very_high'},
            
            # Utilities
            'pge': {'category': 'Energy', 'subcategory': 'electricity', 'carbon_intensity': 'medium'},
            'edison': {'category': 'Energy', 'subcategory': 'electricity', 'carbon_intensity': 'medium'},
            'con ed': {'category': 'Energy', 'subcategory': 'electricity', 'carbon_intensity': 'high'},
            'duke energy': {'category': 'Energy', 'subcategory': 'electricity', 'carbon_intensity': 'high'},
            'national grid': {'category': 'Energy', 'subcategory': 'electricity', 'carbon_intensity': 'medium'},
            'xcel energy': {'category': 'Energy', 'subcategory': 'electricity', 'carbon_intensity': 'medium'},
            
            # Food & Dining
            'mcdonalds': {'category': 'Food', 'subcategory': 'fast_food', 'carbon_intensity': 'high'},
            'burger king': {'category': 'Food', 'subcategory': 'fast_food', 'carbon_intensity': 'high'},
            'kfc': {'category': 'Food', 'subcategory': 'fast_food', 'carbon_intensity': 'high'},
            'taco bell': {'category': 'Food', 'subcategory': 'fast_food', 'carbon_intensity': 'medium'},
            'subway': {'category': 'Food', 'subcategory': 'fast_food', 'carbon_intensity': 'medium'},
            'starbucks': {'category': 'Food', 'subcategory': 'coffee', 'carbon_intensity': 'medium'},
            'dunkin': {'category': 'Food', 'subcategory': 'coffee', 'carbon_intensity': 'medium'},
            'whole foods': {'category': 'Food', 'subcategory': 'organic_grocery', 'carbon_intensity': 'low'},
            'trader joes': {'category': 'Food', 'subcategory': 'grocery', 'carbon_intensity': 'low'},
            'safeway': {'category': 'Food', 'subcategory': 'grocery', 'carbon_intensity': 'medium'},
            'kroger': {'category': 'Food', 'subcategory': 'grocery', 'carbon_intensity': 'medium'},
            'walmart': {'category': 'Food', 'subcategory': 'grocery', 'carbon_intensity': 'medium'},
            
            # Shopping
            'amazon': {'category': 'Shopping', 'subcategory': 'online_retail', 'carbon_intensity': 'medium'},
            'target': {'category': 'Shopping', 'subcategory': 'retail', 'carbon_intensity': 'medium'},
            'costco': {'category': 'Shopping', 'subcategory': 'warehouse', 'carbon_intensity': 'medium'},
            'best buy': {'category': 'Shopping', 'subcategory': 'electronics', 'carbon_intensity': 'high'},
            'apple store': {'category': 'Shopping', 'subcategory': 'electronics', 'carbon_intensity': 'high'},
            'home depot': {'category': 'Shopping', 'subcategory': 'home_improvement', 'carbon_intensity': 'medium'},
            'lowes': {'category': 'Shopping', 'subcategory': 'home_improvement', 'carbon_intensity': 'medium'},
            
            # Entertainment
            'netflix': {'category': 'Entertainment', 'subcategory': 'streaming', 'carbon_intensity': 'low'},
            'spotify': {'category': 'Entertainment', 'subcategory': 'streaming', 'carbon_intensity': 'low'},
            'amc': {'category': 'Entertainment', 'subcategory': 'movies', 'carbon_intensity': 'low'},
            'regal': {'category': 'Entertainment', 'subcategory': 'movies', 'carbon_intensity': 'low'},
        }
    
    def load_category_keywords(self) -> Dict:
        """Load keyword patterns for category classification"""
        return {
            'Transportation': {
                'fuel': ['gas', 'fuel', 'gasoline', 'diesel', 'petrol', 'station'],
                'rideshare': ['uber', 'lyft', 'ride', 'taxi', 'cab'],
                'public_transport': ['metro', 'mta', 'bart', 'bus', 'transit', 'subway'],
                'parking': ['parking', 'meter', 'garage', 'lot'],
                'automotive': ['auto', 'car', 'vehicle', 'repair', 'service', 'oil change'],
                'flight': ['airline', 'flight', 'airport', 'airways', 'air']
            },
            'Energy': {
                'electricity': ['electric', 'power', 'utility', 'pge', 'edison', 'energy'],
                'gas': ['gas company', 'natural gas', 'heating'],
                'renewable': ['solar', 'wind', 'renewable', 'green energy']
            },
            'Food': {
                'restaurant': ['restaurant', 'cafe', 'bistro', 'grill', 'diner', 'eatery'],
                'fast_food': ['mcdonalds', 'burger', 'pizza', 'kfc', 'taco', 'fast'],
                'grocery': ['grocery', 'market', 'supermarket', 'food', 'safeway', 'kroger'],
                'coffee': ['coffee', 'starbucks', 'dunkin', 'cafe', 'espresso'],
                'delivery': ['doordash', 'ubereats', 'grubhub', 'delivery', 'takeout']
            },
            'Shopping': {
                'retail': ['store', 'shop', 'retail', 'mall', 'target', 'walmart'],
                'online': ['amazon', 'ebay', 'online', 'web', 'internet'],
                'electronics': ['best buy', 'apple', 'electronics', 'computer', 'phone'],
                'clothing': ['clothing', 'apparel', 'fashion', 'shoes', 'dress'],
                'home': ['home depot', 'lowes', 'furniture', 'home', 'garden']
            },
            'Entertainment': {
                'streaming': ['netflix', 'spotify', 'hulu', 'disney', 'streaming'],
                'movies': ['movie', 'cinema', 'theater', 'amc', 'regal'],
                'gaming': ['game', 'gaming', 'xbox', 'playstation', 'steam'],
                'sports': ['gym', 'fitness', 'sport', 'recreation', 'club']
            }
        }
    
    def load_carbon_patterns(self) -> Dict:
        """Load patterns that indicate carbon intensity"""
        return {
            'very_high': ['flight', 'airline', 'jet', 'plane', 'airport'],
            'high': ['gas', 'fuel', 'coal', 'beef', 'meat', 'steak', 'burger'],
            'medium': ['car', 'drive', 'restaurant', 'retail', 'shopping'],
            'low': ['bike', 'walk', 'train', 'bus', 'vegetarian', 'organic', 'local'],
            'very_low': ['renewable', 'solar', 'wind', 'electric bike', 'walking']
        }
    
    def parse_transaction(self, description: str, amount: float, date: str = None) -> TransactionClassification:
        """
        Parse transaction using multiple AI techniques
        
        Args:
            description: Transaction description
            amount: Transaction amount
            date: Transaction date
            
        Returns:
            TransactionClassification object
        """
        description_clean = self.clean_description(description)
        
        # Method 1: Merchant database lookup
        merchant_result = self.classify_by_merchant(description_clean)
        
        # Method 2: NLP entity extraction
        nlp_result = self.classify_by_nlp(description_clean)
        
        # Method 3: BERT-based classification
        bert_result = self.classify_by_bert(description_clean)
        
        # Method 4: Keyword pattern matching
        keyword_result = self.classify_by_keywords(description_clean)
        
        # Combine results with confidence weighting
        final_classification = self.combine_classifications([
            merchant_result,
            nlp_result,
            bert_result,
            keyword_result
        ], description_clean, amount)
        
        return final_classification
    
    def clean_description(self, description: str) -> str:
        """Clean and normalize transaction description"""
        # Convert to lowercase
        clean = description.lower().strip()
        
        # Remove common transaction codes and numbers
        clean = re.sub(r'\b\d{4,}\b', '', clean)  # Remove long numbers
        clean = re.sub(r'#\d+', '', clean)        # Remove reference numbers
        clean = re.sub(r'\*+', '', clean)         # Remove asterisks
        clean = re.sub(r'\s+', ' ', clean)        # Normalize whitespace
        
        # Remove common prefixes/suffixes
        prefixes = ['pos', 'purchase', 'payment', 'debit', 'credit']
        for prefix in prefixes:
            clean = re.sub(f'^{prefix}\\s+', '', clean)
        
        return clean.strip()
    
    def classify_by_merchant(self, description: str) -> Optional[TransactionClassification]:
        """Classify using merchant database"""
        for merchant, info in self.merchant_database.items():
            if merchant in description:
                return TransactionClassification(
                    category=info['category'],
                    subcategory=info['subcategory'],
                    confidence=0.95,
                    carbon_intensity=info['carbon_intensity'],
                    merchant_type='known_merchant'
                )
        return None
    
    def classify_by_nlp(self, description: str) -> Optional[TransactionClassification]:
        """Classify using spaCy NLP"""
        if not self.nlp:
            return None
        
        doc = self.nlp(description)
        
        # Extract organizations and locations
        organizations = [ent.text.lower() for ent in doc.ents if ent.label_ == "ORG"]
        locations = [ent.text for ent in doc.ents if ent.label_ in ["GPE", "LOC"]]
        
        # Check if any organizations match our merchant database
        for org in organizations:
            if org in self.merchant_database:
                info = self.merchant_database[org]
                return TransactionClassification(
                    category=info['category'],
                    subcategory=info['subcategory'],
                    confidence=0.85,
                    carbon_intensity=info['carbon_intensity'],
                    merchant_type='nlp_extracted',
                    location=locations[0] if locations else None
                )
        
        return None
    
    def classify_by_bert(self, description: str) -> Optional[TransactionClassification]:
        """Classify using BERT-based model"""
        if not self.classifier:
            return None
        
        try:
            # Use zero-shot classification
            result = self.classifier(description, self.category_labels)
            
            if result and len(result) > 0:
                best_result = max(result, key=lambda x: x['score'])
                
                if best_result['score'] > 0.5:  # Confidence threshold
                    # Map label to our category system
                    category_mapping = {
                        'transportation and fuel': 'Transportation',
                        'food and dining': 'Food',
                        'energy and utilities': 'Energy',
                        'shopping and retail': 'Shopping',
                        'entertainment and recreation': 'Entertainment',
                        'healthcare and medical': 'Healthcare',
                        'other services': 'Other'
                    }
                    
                    category = category_mapping.get(best_result['label'], 'Other')
                    
                    # Determine carbon intensity based on category
                    carbon_intensity_map = {
                        'Transportation': 'high',
                        'Energy': 'medium',
                        'Food': 'medium',
                        'Shopping': 'medium',
                        'Entertainment': 'low',
                        'Healthcare': 'low',
                        'Other': 'low'
                    }
                    
                    return TransactionClassification(
                        category=category,
                        subcategory='bert_classified',
                        confidence=best_result['score'],
                        carbon_intensity=carbon_intensity_map.get(category, 'medium'),
                        merchant_type='ai_classified'
                    )
        
        except Exception as e:
            print(f"BERT classification error: {e}")
        
        return None
    
    def classify_by_keywords(self, description: str) -> Optional[TransactionClassification]:
        """Classify using keyword patterns"""
        best_match = None
        best_score = 0
        
        for category, subcategories in self.category_keywords.items():
            for subcategory, keywords in subcategories.items():
                score = 0
                matched_keywords = []
                
                for keyword in keywords:
                    if keyword in description:
                        score += 1
                        matched_keywords.append(keyword)
                
                # Normalize score by number of keywords
                normalized_score = score / len(keywords) if keywords else 0
                
                if normalized_score > best_score:
                    best_score = normalized_score
                    
                    # Determine carbon intensity
                    carbon_intensity = self.determine_carbon_intensity(description, category, subcategory)
                    
                    best_match = TransactionClassification(
                        category=category,
                        subcategory=subcategory,
                        confidence=min(normalized_score, 0.8),  # Cap at 0.8 for keyword matching
                        carbon_intensity=carbon_intensity,
                        merchant_type='keyword_matched'
                    )
        
        return best_match if best_score > 0.1 else None
    
    def determine_carbon_intensity(self, description: str, category: str, subcategory: str) -> str:
        """Determine carbon intensity based on patterns and category"""
        
        # Check for explicit carbon intensity patterns
        for intensity, patterns in self.carbon_intensity_patterns.items():
            for pattern in patterns:
                if pattern in description:
                    return intensity
        
        # Default intensities by category and subcategory
        intensity_defaults = {
            'Transportation': {
                'fuel': 'high',
                'flight': 'very_high',
                'rideshare': 'medium',
                'public_transport': 'low',
                'default': 'medium'
            },
            'Energy': {
                'electricity': 'medium',
                'gas': 'high',
                'renewable': 'very_low',
                'default': 'medium'
            },
            'Food': {
                'fast_food': 'high',
                'restaurant': 'medium',
                'grocery': 'medium',
                'organic_grocery': 'low',
                'default': 'medium'
            },
            'Shopping': {
                'electronics': 'high',
                'online_retail': 'medium',
                'retail': 'medium',
                'default': 'medium'
            },
            'Entertainment': {
                'streaming': 'low',
                'movies': 'low',
                'default': 'low'
            }
        }
        
        category_defaults = intensity_defaults.get(category, {'default': 'medium'})
        return category_defaults.get(subcategory, category_defaults['default'])
    
    def combine_classifications(self, results: List[Optional[TransactionClassification]], 
                              description: str, amount: float) -> TransactionClassification:
        """Combine multiple classification results with confidence weighting"""
        
        # Filter out None results
        valid_results = [r for r in results if r is not None]
        
        if not valid_results:
            # Fallback classification
            return TransactionClassification(
                category='Other',
                subcategory='unclassified',
                confidence=0.1,
                carbon_intensity='medium',
                merchant_type='fallback'
            )
        
        # Weight results by confidence and method reliability
        method_weights = {
            'known_merchant': 1.0,
            'nlp_extracted': 0.8,
            'ai_classified': 0.7,
            'keyword_matched': 0.6,
            'fallback': 0.1
        }
        
        # Calculate weighted scores for each category
        category_scores = {}
        
        for result in valid_results:
            weight = method_weights.get(result.merchant_type, 0.5)
            weighted_confidence = result.confidence * weight
            
            if result.category not in category_scores:
                category_scores[result.category] = {
                    'total_weight': 0,
                    'subcategories': {},
                    'carbon_intensities': {},
                    'best_result': None
                }
            
            category_scores[result.category]['total_weight'] += weighted_confidence
            
            # Track subcategories and carbon intensities
            if result.subcategory not in category_scores[result.category]['subcategories']:
                category_scores[result.category]['subcategories'][result.subcategory] = 0
            category_scores[result.category]['subcategories'][result.subcategory] += weighted_confidence
            
            if result.carbon_intensity not in category_scores[result.category]['carbon_intensities']:
                category_scores[result.category]['carbon_intensities'][result.carbon_intensity] = 0
            category_scores[result.category]['carbon_intensities'][result.carbon_intensity] += weighted_confidence
            
            # Keep track of best individual result
            if (category_scores[result.category]['best_result'] is None or 
                weighted_confidence > category_scores[result.category]['best_result'].confidence):
                category_scores[result.category]['best_result'] = result
        
        # Select best category
        best_category = max(category_scores.keys(), key=lambda k: category_scores[k]['total_weight'])
        best_category_data = category_scores[best_category]
        
        # Select best subcategory and carbon intensity
        best_subcategory = max(best_category_data['subcategories'].keys(), 
                              key=lambda k: best_category_data['subcategories'][k])
        best_carbon_intensity = max(best_category_data['carbon_intensities'].keys(),
                                   key=lambda k: best_category_data['carbon_intensities'][k])
        
        # Calculate final confidence
        final_confidence = min(best_category_data['total_weight'], 1.0)
        
        return TransactionClassification(
            category=best_category,
            subcategory=best_subcategory,
            confidence=final_confidence,
            carbon_intensity=best_carbon_intensity,
            merchant_type='combined_ai',
            location=best_category_data['best_result'].location if best_category_data['best_result'] else None
        )
    
    def batch_parse_transactions(self, transactions: List[Dict]) -> List[Dict]:
        """Parse multiple transactions efficiently"""
        results = []
        
        for transaction in transactions:
            description = transaction.get('description', '')
            amount = transaction.get('amount', 0)
            date = transaction.get('date', '')
            
            classification = self.parse_transaction(description, amount, date)
            
            # Add classification results to transaction
            enhanced_transaction = transaction.copy()
            enhanced_transaction.update({
                'ai_category': classification.category,
                'ai_subcategory': classification.subcategory,
                'ai_confidence': classification.confidence,
                'ai_carbon_intensity': classification.carbon_intensity,
                'ai_merchant_type': classification.merchant_type,
                'ai_location': classification.location
            })
            
            results.append(enhanced_transaction)
        
        return results
    
    def get_parsing_statistics(self, parsed_transactions: List[Dict]) -> Dict:
        """Get statistics about parsing accuracy and coverage"""
        total = len(parsed_transactions)
        if total == 0:
            return {}
        
        high_confidence = sum(1 for t in parsed_transactions if t.get('ai_confidence', 0) > 0.8)
        medium_confidence = sum(1 for t in parsed_transactions if 0.5 < t.get('ai_confidence', 0) <= 0.8)
        low_confidence = sum(1 for t in parsed_transactions if t.get('ai_confidence', 0) <= 0.5)
        
        category_distribution = {}
        for transaction in parsed_transactions:
            category = transaction.get('ai_category', 'Unknown')
            category_distribution[category] = category_distribution.get(category, 0) + 1
        
        return {
            'total_transactions': total,
            'high_confidence_count': high_confidence,
            'medium_confidence_count': medium_confidence,
            'low_confidence_count': low_confidence,
            'high_confidence_percentage': (high_confidence / total) * 100,
            'category_distribution': category_distribution,
            'average_confidence': sum(t.get('ai_confidence', 0) for t in parsed_transactions) / total
        }
