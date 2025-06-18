import subprocess
import sys
import os

def install_requirements():
    """Install required packages"""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ All requirements installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing requirements: {e}")
        return False

def create_sample_data():
    """Create sample data file"""
    from database import Database
    
    db = Database()
    
    # Add sample user
    sample_user = {
        'user_id': 'elite_user_001',
        'username': 'EcoRoyalty',
        'total_score': 8750,
        'trees_planted': 23,
        'level': 'Carbon Crusader',
        'achievements': ['First Steps', 'Week Warrior', 'Tree Planter', 'Carbon Saver'],
        'streak_days': 15
    }
    
    db.data['users']['elite_user_001'] = sample_user
    db._save_data()
    
    print("✅ Sample data created!")

def main():
    print("🌱 Setting up GreenScore Elite...")
    
    if install_requirements():
        create_sample_data()
        print("\n🎉 Setup complete! Run the app with:")
        print("streamlit run app.py")
    else:
        print("\n❌ Setup failed. Please install requirements manually.")

if __name__ == "__main__":
    main()
