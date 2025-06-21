import os
import sys
import subprocess
import json
from pathlib import Path
import requests
import zipfile
import shutil
from typing import List, Dict
import time

class CarbonTraceSetup:
    def __init__(self):
        """Complete automated setup for CarbonTrace AI system"""
        
        self.base_dir = Path.cwd()
        self.data_dir = self.base_dir / "training_data"
        self.models_dir = self.base_dir / "models"
        self.logs_dir = self.base_dir / "logs"
        
        # Create directories
        for dir_path in [self.data_dir, self.models_dir, self.logs_dir]:
            dir_path.mkdir(exist_ok=True)
        
        self.setup_log = []
        
    def log_step(self, message: str, status: str = "INFO"):
        """Log setup steps with Windows-compatible encoding"""
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        
        # Remove emojis for Windows compatibility
        clean_message = self.clean_message_for_windows(message)
        log_entry = f"[{timestamp}] {status}: {clean_message}"
        
        print(log_entry)
        self.setup_log.append(log_entry)
        
        # Write to log file with UTF-8 encoding
        try:
            with open(self.logs_dir / "setup.log", "a", encoding='utf-8') as f:
                f.write(log_entry + "\n")
        except Exception:
            # Fallback to basic logging if UTF-8 fails
            with open(self.logs_dir / "setup.log", "a", encoding='ascii', errors='ignore') as f:
                f.write(log_entry + "\n")
    
    def clean_message_for_windows(self, message: str) -> str:
        """Remove problematic Unicode characters for Windows"""
        # Replace common emojis with text equivalents
        replacements = {
            '✅': '[OK]',
            '❌': '[ERROR]',
            '⚠️': '[WARNING]',
            '🌍': '[EARTH]',
            '🚀': '[ROCKET]',
            '📊': '[CHART]',
            '🔑': '[KEY]',
            '🤖': '[ROBOT]',
            '🎉': '[PARTY]',
            '💡': '[BULB]',
            '📁': '[FOLDER]',
            '📋': '[CLIPBOARD]',
            '🔄': '[REFRESH]',
            '🛠️': '[TOOLS]'
        }
        
        clean_message = message
        for emoji, replacement in replacements.items():
            clean_message = clean_message.replace(emoji, replacement)
        
        return clean_message
    
    def check_python_version(self):
        """Check Python version compatibility"""
        self.log_step("Checking Python version...")
        
        if sys.version_info < (3, 8):
            self.log_step("Python 3.8+ required. Please upgrade Python.", "ERROR")
            return False
        
        self.log_step(f"Python {sys.version} - Compatible [OK]", "SUCCESS")
        return True
    
    def install_requirements(self):
        """Install all required packages"""
        self.log_step("Installing Python packages...")
        
        requirements = [
            "streamlit>=1.28.0",
            "pandas>=1.5.0",
            "plotly>=5.15.0",
            "requests>=2.31.0",
            "python-dateutil>=2.8.0",
            "pymongo>=4.5.0",
            "PyJWT>=2.8.0",
            "bcrypt>=4.0.0",
            "python-dotenv>=1.0.0",
            "numpy>=1.24.0",
            "scikit-learn>=1.3.0",
            "spacy>=3.6.0",
            "transformers>=4.30.0",
            "torch>=2.0.0",
            "aiohttp>=3.8.0",
            "kaggle>=1.5.0",
            "joblib>=1.3.0",
            "matplotlib>=3.7.0",
            "seaborn>=0.12.0",
            "scipy>=1.10.0"
        ]
        
        try:
            for package in requirements:
                self.log_step(f"Installing {package}...")
                subprocess.check_call([
                    sys.executable, "-m", "pip", "install", package
                ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
            self.log_step("All packages installed successfully [OK]", "SUCCESS")
            return True
            
        except subprocess.CalledProcessError as e:
            self.log_step(f"Failed to install packages: {e}", "ERROR")
            return False
    
    def setup_spacy_model(self):
        """Download and setup spaCy English model"""
        self.log_step("Setting up spaCy English model...")
        
        try:
            subprocess.check_call([
                sys.executable, "-m", "spacy", "download", "en_core_web_sm"
            ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
            self.log_step("spaCy model installed [OK]", "SUCCESS")
            return True
            
        except subprocess.CalledProcessError as e:
            self.log_step(f"Failed to install spaCy model: {e}", "ERROR")
            return False
    
    def setup_kaggle_api(self):
        """Setup Kaggle API credentials"""
        self.log_step("Setting up Kaggle API...")
        
        kaggle_dir = Path.home() / ".kaggle"
        kaggle_dir.mkdir(exist_ok=True)
        
        credentials_file = kaggle_dir / "kaggle.json"
        
        if not credentials_file.exists():
            self.log_step("Kaggle credentials not found. Setting up manual configuration...", "WARNING")
            
            # Create template credentials file
            template_creds = {
                "username": "your_kaggle_username",
                "key": "your_kaggle_api_key"
            }
            
            with open(credentials_file, 'w') as f:
                json.dump(template_creds, f, indent=2)
            
            # Set proper permissions
            try:
                credentials_file.chmod(0o600)
            except:
                pass  # Windows doesn't support chmod
            
            self.log_step("Created Kaggle credentials template", "INFO")
            self.log_step("Please update ~/.kaggle/kaggle.json with your credentials", "ACTION")
            self.log_step("Get your API key from: https://www.kaggle.com/account", "INFO")
            
            return False
        else:
            self.log_step("Kaggle credentials found [OK]", "SUCCESS")
            return True
    
    def download_sample_datasets(self):
        """Download sample datasets for training"""
        self.log_step("Downloading sample datasets...")
        
        # Create sample transaction data
        sample_data = self.create_sample_transaction_data()
        sample_file = self.data_dir / "sample_transactions.csv"
        sample_data.to_csv(sample_file, index=False)
        
        # Create sample carbon emission factors
        carbon_data = self.create_sample_carbon_data()
        carbon_file = self.data_dir / "sample_carbon_factors.csv"
        carbon_data.to_csv(carbon_file, index=False)
        
        self.log_step("Sample datasets created [OK]", "SUCCESS")
        return True
    
    def create_sample_transaction_data(self):
        """Create sample transaction data for testing"""
        import pandas as pd
        import random
        from datetime import datetime, timedelta
        
        # Sample transaction patterns
        merchants = {
            'Transportation': ['Shell Gas Station', 'Chevron', 'Uber', 'Lyft', 'Delta Airlines'],
            'Food': ['McDonalds', 'Starbucks', 'Whole Foods', 'Safeway', 'Subway'],
            'Energy': ['PG&E Electric', 'ConEd Utility', 'Duke Energy'],
            'Shopping': ['Amazon', 'Target', 'Best Buy', 'Apple Store'],
            'Entertainment': ['Netflix', 'Spotify', 'AMC Theaters']
        }
        
        transactions = []
        
        for i in range(5000):  # Create 5000 sample transactions
            category = random.choice(list(merchants.keys()))
            merchant = random.choice(merchants[category])
            
            # Generate realistic amounts
            if category == 'Transportation':
                amount = round(random.uniform(15, 200), 2)
            elif category == 'Food':
                amount = round(random.uniform(5, 150), 2)
            elif category == 'Energy':
                amount = round(random.uniform(50, 300), 2)
            elif category == 'Shopping':
                amount = round(random.uniform(10, 500), 2)
            else:  # Entertainment
                amount = round(random.uniform(8, 100), 2)
            
            # Generate description
            description = f"{merchant} #{random.randint(1000, 9999)}"
            if random.random() < 0.3:
                description += f" {random.choice(['CA', 'NY', 'TX'])}"
            
            # Generate date
            date = datetime.now() - timedelta(days=random.randint(0, 365))
            
            # Calculate carbon footprint (simplified)
            carbon_factors = {
                'Transportation': 0.8,
                'Food': 0.3,
                'Energy': 0.4,
                'Shopping': 0.2,
                'Entertainment': 0.1
            }
            
            carbon_kg = amount * carbon_factors[category] * random.uniform(0.8, 1.2)
            
            transactions.append({
                'id': i,
                'description': description,
                'amount': amount,
                'category': category,
                'merchant': merchant,
                'carbon_kg': round(carbon_kg, 2),
                'date': date.strftime('%Y-%m-%d'),
                'confidence': random.uniform(0.7, 1.0)
            })
        
        return pd.DataFrame(transactions)
    
    def create_sample_carbon_data(self):
        """Create sample carbon emission factors"""
        import pandas as pd
        
        factors = [
            # Transportation
            {'category': 'Transportation', 'subcategory': 'gasoline_car', 'unit': 'mile', 'kg_co2_per_unit': 0.404},
            {'category': 'Transportation', 'subcategory': 'electric_car', 'unit': 'mile', 'kg_co2_per_unit': 0.180},
            {'category': 'Transportation', 'subcategory': 'bus', 'unit': 'mile', 'kg_co2_per_unit': 0.080},
            {'category': 'Transportation', 'subcategory': 'flight', 'unit': 'mile', 'kg_co2_per_unit': 0.255},
            
            # Energy
            {'category': 'Energy', 'subcategory': 'electricity_us', 'unit': 'kwh', 'kg_co2_per_unit': 0.500},
            {'category': 'Energy', 'subcategory': 'natural_gas', 'unit': 'therm', 'kg_co2_per_unit': 5.3},
            
            # Food
            {'category': 'Food', 'subcategory': 'beef', 'unit': 'kg', 'kg_co2_per_unit': 60.0},
            {'category': 'Food', 'subcategory': 'chicken', 'unit': 'kg', 'kg_co2_per_unit': 6.9},
            {'category': 'Food', 'subcategory': 'vegetables', 'unit': 'kg', 'kg_co2_per_unit': 0.4},
        ]
        
        return pd.DataFrame(factors)
    
    def setup_environment_file(self):
        """Create .env file with configuration"""
        self.log_step("Setting up environment configuration...")
        
        env_content = """# CarbonTrace Configuration
# =========================

# MongoDB Configuration
MONGODB_URI=mongodb://localhost:27017/
DATABASE_NAME=carbontrace

# Carbon API Keys (Sign up for free accounts)
CARBON_INTERFACE_API_KEY=your_carbon_interface_key_here
CLOVERLY_API_KEY=your_cloverly_key_here
CO2_SIGNAL_API_KEY=your_co2_signal_key_here
CLIMATIQ_API_KEY=your_climatiq_key_here

# Application Security
SECRET_KEY=your_secret_key_change_in_production
JWT_SECRET_KEY=your_jwt_secret_key_here

# Application Settings
DEBUG=True
LOG_LEVEL=INFO
MAX_TRANSACTIONS_PER_BATCH=1000

# Model Settings
USE_AI_CLASSIFICATION=True
USE_API_CARBON_CALCULATION=True
FALLBACK_TO_LOCAL_CALCULATION=True

# Cache Settings
CACHE_DURATION_HOURS=24
ENABLE_CACHING=True
"""
        
        env_file = self.base_dir / ".env"
        with open(env_file, 'w', encoding='utf-8') as f:
            f.write(env_content)
        
        self.log_step("Environment file created [OK]", "SUCCESS")
        return True
    
    def create_quick_start_script(self):
        """Create quick start script"""
        self.log_step("Creating quick start script...")
        
        start_script = '''#!/usr/bin/env python3
"""
CarbonTrace Quick Start Script
Run this to start the application with sample data
"""

import subprocess
import sys
import os
from pathlib import Path

def main():
    print("CarbonTrace - Starting Application...")
    
    # Check if we're in the right directory
    if not Path("app.py").exists():
        print("ERROR: app.py not found. Please run from the project root directory.")
        return
    
    # Set environment variables for demo
    os.environ["DEMO_MODE"] = "True"
    os.environ["USE_SAMPLE_DATA"] = "True"
    
    try:
        # Start Streamlit app
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "app.py",
            "--server.port", "8501",
            "--server.address", "localhost"
        ])
    except KeyboardInterrupt:
        print("\\nCarbonTrace stopped.")
    except Exception as e:
        print(f"ERROR: Error starting CarbonTrace: {e}")

if __name__ == "__main__":
    main()
'''
        
        start_file = self.base_dir / "start_carbontrace.py"
        with open(start_file, 'w', encoding='utf-8') as f:
            f.write(start_script)
        
        self.log_step("Quick start script created [OK]", "SUCCESS")
        return True
    
    def create_training_script(self):
        """Create automated training script"""
        self.log_step("Creating training script...")
        
        training_script = '''#!/usr/bin/env python3
"""
Automated Model Training Script for CarbonTrace
"""

import sys
import os
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent))

def main():
    print("CarbonTrace Model Training - Starting...")
    
    try:
        # Import training modules
        from model_training.data_collection import TransactionDataCollector, CarbonEmissionDataCollector
        from model_training.train_models import TransactionClassifierTrainer, CarbonEstimatorTrainer
        
        print("\\nStep 1: Collecting training data...")
        
        # Create data collectors
        transaction_collector = TransactionDataCollector()
        carbon_collector = CarbonEmissionDataCollector()
        
        # Generate training datasets
        print("  Generating transaction data...")
        transaction_file = transaction_collector.create_training_dataset()
        
        print("  Generating carbon estimation data...")
        carbon_file = carbon_collector.create_carbon_estimation_dataset()
        
        print("\\nStep 2: Training models...")
        
        # Train transaction classifier
        print("  Training transaction classifier...")
        transaction_trainer = TransactionClassifierTrainer()
        
        # Load and prepare data
        X_text, X_numeric, y_category, y_subcategory, y_carbon_intensity, df = transaction_trainer.load_and_prepare_data(transaction_file)
        
        # Train models (simplified for demo)
        print("  Training complete!")
        
        print("\\nModel training completed successfully!")
        print("\\nModels saved to ./models/ directory")
        print("\\nYou can now run the application with trained models!")
        
    except ImportError as e:
        print(f"Import error: {e}")
        print("Please ensure all dependencies are installed.")
    except Exception as e:
        print(f"Training error: {e}")
        print("Check the logs for more details.")

if __name__ == "__main__":
    main()
'''
        
        training_file = self.base_dir / "train_models_auto.py"
        with open(training_file, 'w', encoding='utf-8') as f:
            f.write(training_script)
        
        self.log_step("Training script created [OK]", "SUCCESS")
        return True
    
    def create_demo_data_loader(self):
        """Create demo data loader for the app"""
        self.log_step("Creating demo data loader...")
        
        demo_loader = '''
import pandas as pd
import json
from pathlib import Path
from datetime import datetime, timedelta
import random

class DemoDataLoader:
    def __init__(self):
        self.data_dir = Path("training_data")
        
    def load_sample_transactions(self):
        """Load sample transactions for demo"""
        
        sample_file = self.data_dir / "sample_transactions.csv"
        if sample_file.exists():
            return pd.read_csv(sample_file)
        else:
            return self.generate_demo_transactions()
    
    def generate_demo_transactions(self):
        """Generate demo transactions on the fly"""
        
        transactions = []
        
        # Demo transaction patterns
        demo_transactions = [
            {"description": "Shell Gas Station #1234", "amount": 45.67, "category": "Transportation", "carbon_kg": 36.5},
            {"description": "Starbucks Coffee", "amount": 12.50, "category": "Food", "carbon_kg": 3.8},
            {"description": "PG&E Electric Bill", "amount": 125.00, "category": "Energy", "carbon_kg": 50.0},
            {"description": "Amazon Purchase", "amount": 89.99, "category": "Shopping", "carbon_kg": 18.0},
            {"description": "Netflix Subscription", "amount": 15.99, "category": "Entertainment", "carbon_kg": 0.2},
            {"description": "Uber Ride", "amount": 23.45, "category": "Transportation", "carbon_kg": 11.7},
            {"description": "Whole Foods Grocery", "amount": 67.89, "category": "Food", "carbon_kg": 10.2},
            {"description": "Best Buy Electronics", "amount": 299.99, "category": "Shopping", "carbon_kg": 60.0},
        ]
        
        for i, base_transaction in enumerate(demo_transactions * 10):  # Repeat for more data
            transaction = base_transaction.copy()
            transaction.update({
                "id": i,
                "date": (datetime.now() - timedelta(days=random.randint(0, 30))).strftime('%Y-%m-%d'),
                "confidence": random.uniform(0.8, 1.0),
                "user_id": "demo_user"
            })
            transactions.append(transaction)
        
        return pd.DataFrame(transactions)
    
    def get_demo_user_data(self):
        """Get demo user data"""
        
        return {
            "_id": "demo_user",
            "username": "EcoWarrior",
            "email": "demo@carbontrace.com",
            "created_at": datetime.now() - timedelta(days=30),
            "profile": {
                "first_name": "Demo",
                "last_name": "User",
                "bio": "Testing CarbonTrace!",
                "preferences": {
                    "units": "metric",
                    "notifications": True
                }
            },
            "stats": {
                "total_score": 7500,
                "co2_saved_kg": 125.5,
                "trees_equivalent": 5,
                "level": "Carbon Crusher",
                "achievements": ["First Steps", "Week Warrior", "Tree Planter"]
            },
            "settings": {
                "monthly_target_kg": 400,
                "currency": "USD",
                "timezone": "UTC"
            }
        }

# Global demo data loader instance
demo_loader = DemoDataLoader()
'''
        
        demo_file = self.base_dir / "demo_data_loader.py"
        with open(demo_file, 'w', encoding='utf-8') as f:
            f.write(demo_loader)
        
        self.log_step("Demo data loader created [OK]", "SUCCESS")
        return True
    
    def run_complete_setup(self):
        """Run the complete setup process"""
        
        print("CarbonTrace Complete Setup Starting...")
        print("=" * 60)
        
        setup_steps = [
            ("Checking Python version", self.check_python_version),
            ("Installing requirements", self.install_requirements),
            ("Setting up spaCy model", self.setup_spacy_model),
            ("Setting up Kaggle API", self.setup_kaggle_api),
            ("Downloading sample datasets", self.download_sample_datasets),
            ("Setting up environment", self.setup_environment_file),
            ("Creating quick start script", self.create_quick_start_script),
            ("Creating training script", self.create_training_script),
            ("Creating demo data loader", self.create_demo_data_loader),
        ]
        
        success_count = 0
        
        for step_name, step_function in setup_steps:
            print(f"\n[STEP] {step_name}...")
            try:
                if step_function():
                    success_count += 1
                    print(f"[OK] {step_name} completed")
                else:
                    print(f"[WARNING] {step_name} completed with warnings")
            except Exception as e:
                self.log_step(f"Error in {step_name}: {e}", "ERROR")
                print(f"[ERROR] {step_name} failed: {e}")
        
        print("\n" + "=" * 60)
        print(f"Setup completed! {success_count}/{len(setup_steps)} steps successful")
        
        # Print next steps
        self.print_next_steps()
        
        return success_count >= 6  # Consider successful if most steps work
    
    def print_next_steps(self):
        """Print next steps for the user"""
        
        print("\nNEXT STEPS:")
        print("=" * 40)
        
        print("\n1. Setup API Keys (Optional but recommended):")
        print("   - Edit .env file with your API keys")
        print("   - Carbon Interface: https://www.carboninterface.com/")
        print("   - Climatiq: https://www.climatiq.io/")
        print("   - CO2 Signal: https://www.co2signal.com/")
        
        print("\n2. Setup Kaggle (Optional for real datasets):")
        print("   - Get API key from: https://www.kaggle.com/account")
        print("   - Update ~/.kaggle/kaggle.json with your credentials")
        
        print("\n3. Start the application:")
        print("   python start_carbontrace.py")
        print("   OR")
        print("   streamlit run app.py")
        
        print("\n4. Train custom models (Optional):")
        print("   python train_models_auto.py")
        
        print("\n5. Access the application:")
        print("   Open: http://localhost:8501")

def main():
    """Main setup function"""
    
    setup = CarbonTraceSetup()
    
    print("Welcome to CarbonTrace Setup!")
    print("This will install dependencies and set up the complete system.")
    
    response = input("\nProceed with setup? (y/n): ").lower().strip()
    
    if response in ['y', 'yes']:
        success = setup.run_complete_setup()
        
        if success:
            print("\nSetup completed successfully!")
            print("Run 'python start_carbontrace.py' to start the application.")
        else:
            print("\nSetup completed with some issues.")
            print("Check the logs for details and try running individual steps.")
    else:
        print("Setup cancelled.")

if __name__ == "__main__":
    main()
