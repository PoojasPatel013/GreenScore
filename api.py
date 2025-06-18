from flask import Flask, request, jsonify
from flask_cors import CORS
from database import Database
from carbon_calculator import CarbonCalculator
from ai_parser import TransactionParser
from gamification import GamificationEngine
import pandas as pd

app = Flask(__name__)
CORS(app)

# Initialize components
db = Database()
calculator = CarbonCalculator()
parser = TransactionParser()
game_engine = GamificationEngine()

@app.route('/api/user/<user_id>/dashboard', methods=['GET'])
def get_dashboard(user_id):
    """Get user dashboard data"""
    try:
        user_data = db.get_user_data(user_id)
        transactions = db.get_user_transactions(user_id, days=30)
        
        total_footprint = sum(t['carbon_kg'] for t in transactions)
        score = game_engine.calculate_score(user_id, transactions)
        level = game_engine.get_user_level(score)
        
        return jsonify({
            'user_data': user_data,
            'total_footprint': total_footprint,
            'score': score,
            'level': level,
            'transactions': transactions[:10]  # Recent transactions
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/user/<user_id>/transactions', methods=['POST'])
def add_transaction(user_id):
    """Add a new transaction"""
    try:
        data = request.json
        
        # Calculate carbon footprint
        carbon_kg = calculator.calculate_footprint(
            data['category'], 
            data.get('subcategory', ''), 
            data['amount']
        )
        
        transaction = {
            'user_id': user_id,
            'date': data['date'],
            'description': data['description'],
            'amount': data['amount'],
            'category': data['category'],
            'subcategory': data.get('subcategory', ''),
            'carbon_kg': carbon_kg
        }
        
        result = db.add_transaction(transaction)
        
        return jsonify({
            'success': True,
            'transaction_id': str(result.inserted_id),
            'carbon_kg': carbon_kg
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/user/<user_id>/recommendations', methods=['GET'])
def get_recommendations(user_id):
    """Get personalized recommendations"""
    try:
        transactions = db.get_user_transactions(user_id, days=30)
        recommendations = calculator.get_recommendations(transactions)
        
        return jsonify({'recommendations': recommendations})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/leaderboard', methods=['GET'])
def get_leaderboard():
    """Get global leaderboard"""
    try:
        leaderboard = game_engine.get_global_leaderboard()
        return jsonify({'leaderboard': leaderboard})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/challenges', methods=['GET'])
def get_challenges():
    """Get weekly challenges"""
    try:
        challenges = game_engine.get_weekly_challenges()
        return jsonify({'challenges': challenges})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
