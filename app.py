import streamlit as st
from datetime import datetime
import pandas as pd
import sys
import os
import socketio
from flask import Flask, request
from flask_login import LoginManager, UserMixin, login_user, login_required, current_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from typing import Dict, List

# Add the project root directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.database import Database
from backend.transaction_analyzer import TransactionAnalyzer
from backend.carbon_calculator import CarbonCalculator
from backend.recommendation_engine import RecommendationEngine
from backend.auth import AuthService
from backend.socket_service import SocketService
from components.transaction_form import transaction_form
from components.gamified_dashboard import dashboard
from components.leaderboard import leaderboard
from components.auth import login_page, signup_page, profile_page, account_dashboard

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'your-secret-key')

# Initialize Socket.IO
socketio = socketio.Server()
app.wsgi_app = socketio.WSGIApp(socketio, app.wsgi_app)

# Initialize services
db = Database()
analyzer = TransactionAnalyzer()
calculator = CarbonCalculator()
recommender = RecommendationEngine()
auth_service = AuthService(db)
socket_service = SocketService(socketio)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# User loader for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    user_data = db.get_user_by_id(user_id)
    if user_data:
        return User(user_id=user_id, **user_data)
    return None

# Streamlit app
def main():
    st.set_page_config(
        page_title="GreenScore",
        page_icon="🌱",
        layout="wide"
    )

    # Check if user is logged in
    if not current_user.is_authenticated:
        # Show login/signup options
        st.title("Welcome to GreenScore 🌱")
        
        # Login/Signup tabs
        auth_tab = st.tabs(["Login", "Sign Up"])
        
        with auth_tab[0]:
            login_page()
        with auth_tab[1]:
            signup_page()
        
        st.stop()  # Stop rendering if not logged in

    # Sidebar
    st.sidebar.title("GreenScore 🌱")

    # User profile section
    profile = db.get_profile(current_user.id)
    if profile:
        st.sidebar.image(profile.get('avatar_url', 'default-avatar.png'), width=100)
        st.sidebar.markdown(f"**{profile.get('full_name', 'User')}**")
        st.sidebar.markdown(profile.get('bio', ''))

    # Leaderboard position
    rank = db.get_user_rank(current_user.id)
    st.sidebar.markdown(f"**Rank**: #{rank}")

    # Navigation
    page = st.sidebar.radio(
        "Navigation",
        ["Dashboard", "Add Transaction", "Leaderboard", "Profile", "Account", "Logout"],
        index=0
    )

    # Main content
    if page == "Dashboard":
        dashboard(current_user.id)
    elif page == "Add Transaction":
        transaction_form(current_user.id)
    elif page == "Leaderboard":
        leaderboard()
    elif page == "Profile":
        profile_page(current_user.id)
    elif page == "Account":
        account_dashboard(current_user.id)
    elif page == "Logout":
        logout_user()
        st.success("Logged out successfully")
        st.stop()
        
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap');
        body {
            font-family: 'Roboto', sans-serif;
        }
        </style>
        """, unsafe_allow_html=True)
    if page == "Dashboard":
        dashboard()
    elif page == "Add Transaction":
        transaction_form()
    elif page == "Leaderboard":
        leaderboard()
    elif page == "Recommendations":
        show_recommendations()

def show_home():
    st.header("Welcome to GreenScore!")
    st.write("""
    Track your carbon footprint and earn rewards for going green.
    Add your transactions manually to start tracking your environmental impact.
    """)
    
    # Add transaction form
    transaction_form()

def show_transactions():
    if 'connected' not in st.session_state:
        st.warning("Please connect your bank account first!")
        return
    
    st.header("Your Transactions")
    transactions = analyzer.get_recent_transactions()
    
    if transactions:
        fig = px.bar(transactions, x='date', y='carbon_footprint', 
                    color='category', title='Carbon Footprint by Category')
        st.plotly_chart(fig)

def show_recommendations():
    if 'connected' not in st.session_state:
        st.warning("Please connect your bank account first!")
        return
    
    st.header("Eco-Friendly Recommendations")
    recommendations = recommender.get_recommendations()
    for rec in recommendations:
        st.markdown(f"- {rec['description']}")

def show_leaderboard():
    st.header("Leaderboard")
    top_users = db.get_top_users()
    st.dataframe(top_users)

if __name__ == "__main__":
    main()
