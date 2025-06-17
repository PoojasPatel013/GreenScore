import streamlit as st
from datetime import datetime
import pandas as pd
import streamlit as st
import sys
import os

# Add the project root directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend import TransactionAnalyzer, CarbonCalculator, RecommendationEngine, Database
from components.transaction_form import transaction_form
from components.gamified_dashboard import dashboard
from components.leaderboard import leaderboard

# Initialize database and components
db = Database()
analyzer = TransactionAnalyzer()
calculator = CarbonCalculator()
recommender = RecommendationEngine()

def main():
    st.set_page_config(
        page_title="GreenScore",
        page_icon="🌱",
        layout="wide"
    )
    
    # Sidebar
    st.sidebar.title("GreenScore 🌱")
    st.sidebar.markdown("---")
    
    # User Dashboard
    col1, col2 = st.sidebar.columns(2)
    with col1:
        st.metric("Your Score", "1200")
    with col2:
        st.metric("Trees Planted", "3")
    
    # Navigation
    page = st.sidebar.radio(
        "Navigation",
        ["Dashboard", "Add Transaction", "Leaderboard", "Recommendations"],
        index=0
    )
    
    # Main content
    if page == "Dashboard":
        dashboard()
    elif page == "Add Transaction":
        show_transactions()
    elif page == "Leaderboard":
        show_leaderboard()
    elif page == "Recommendations":
        show_recommendations()
    
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
