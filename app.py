import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import time
import random
import json
from auth import check_authentication
from database import Database

# Configure page
st.set_page_config(
    page_title="CarbonTrace | Footprint Tracker",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize Streamlit session state
if 'initialized' not in st.session_state:
    st.session_state.initialized = True
    st.session_state.user = None

# Load CSS
def load_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Global dark theme */
    .stApp {
        background-color: #0a0a0a;
        color: #ffffff;
    }
    
    .main .block-container {
        padding-top: 2rem;
        max-width: 1200px;
    }
    
    /* Hide Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Custom button styling */
    .stButton > button {
        background: linear-gradient(45deg, #00d4ff, #0099cc);
        border: none;
        border-radius: 8px;
        color: #000000;
        font-weight: 600;
        padding: 0.6rem 1.2rem;
        width: 100%;
        margin-bottom: 0.5rem;
    }
    
    .stButton > button:hover {
        background: linear-gradient(45deg, #0099cc, #00d4ff);
        transform: translateY(-1px);
    }
    
    /* Feature cards */
    .feature-card {
        background: #1a1a1a;
        border: 1px solid #333;
        border-radius: 12px;
        padding: 2rem;
        text-align: center;
        height: 280px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        transition: all 0.3s ease;
    }
    
    .feature-card:hover {
        border-color: #00d4ff;
        box-shadow: 0 0 15px rgba(0, 212, 255, 0.2);
        transform: translateY(-5px);
    }
    
    .feature-icon {
        font-size: 3rem;
        margin-bottom: 1rem;
    }
    
    .feature-title {
        font-size: 1.3rem;
        font-weight: 600;
        color: #00d4ff;
        margin-bottom: 1rem;
    }
    
    .feature-description {
        color: #b0b0b0;
        line-height: 1.5;
    }
    
    /* Stats cards */
    .stats-card {
        background: linear-gradient(135deg, #1a1a1a 0%, #2a2a2a 100%);
        border: 1px solid #00d4ff;
        border-radius: 12px;
        padding: 1.5rem;
        text-align: center;
        margin-bottom: 1rem;
    }
    
    .stats-number {
        font-size: 2.5rem;
        font-weight: 700;
        color: #00d4ff;
        margin-bottom: 0.5rem;
    }
    
    .stats-label {
        color: #b0b0b0;
        font-size: 0.9rem;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    </style>
    """, unsafe_allow_html=True)

def show_navigation():
    """Show navigation sidebar"""
    with st.sidebar:
        st.markdown("""
        <div style="
            text-align: center;
            padding: 1rem;
            margin-bottom: 2rem;
            border-bottom: 1px solid #333;
        ">
            <h2 style="color: #00d4ff; margin: 0;">🌍 CarbonTrace</h2>
            <p style="color: #888; font-size: 0.9rem; margin: 0.5rem 0 0 0;">
                Personal Carbon Tracker
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.session_state.get('authenticated', False):
            user_data = st.session_state.user_data
            
            # User info card
            st.markdown(f"""
            <div style="
                background: #1a1a1a;
                border: 1px solid #00d4ff;
                border-radius: 10px;
                padding: 1rem;
                margin-bottom: 1rem;
                text-align: center;
            ">
                <div style="
                    width: 60px;
                    height: 60px;
                    border-radius: 50%;
                    background: linear-gradient(135deg, #00d4ff, #0099cc);
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    font-size: 1.5rem;
                    color: white;
                    margin: 0 auto 1rem auto;
                ">
                    {user_data.get('username', 'U')[0].upper()}
                </div>
                <h4 style="color: #00d4ff; margin: 0;">
                    {user_data.get('username', 'User')}
                </h4>
                <p style="color: #888; margin: 0.5rem 0 0 0; font-size: 0.9rem;">
                    {user_data.get('stats', {}).get('level', 'Eco Newbie')}
                </p>
                <p style="color: #00d4ff; margin: 0.5rem 0 0 0; font-size: 0.8rem;">
                    {user_data.get('stats', {}).get('total_score', 1000):,} points
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            # Navigation buttons
            st.markdown("### 📱 Navigation")
            
            if st.button("🏠 Dashboard", use_container_width=True):
                st.switch_page("pages/dashboard.py")
            
            if st.button("👤 Profile", use_container_width=True):
                st.switch_page("pages/profile.py")
            
            st.markdown("---")
            
            # Quick stats
            st.markdown("### 📊 Quick Stats")
            db = Database()
            monthly_stats = db.get_user_monthly_stats(str(user_data['_id']))
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("This Month", f"{monthly_stats['total_carbon']:.1f} kg CO₂")
            with col2:
                st.metric("Transactions", monthly_stats['transaction_count'])
            
            st.markdown("---")
            
            # Logout button
            if st.button("🚪 Logout", type="secondary", use_container_width=True):
                from auth import AuthManager
                db = Database()
                auth = AuthManager(db)
                auth.logout_user()
                st.rerun()
        else:
            st.markdown("### 🔐 Get Started")
            
            if st.button("🔑 Login / Sign Up", use_container_width=True, type="primary"):
                st.switch_page("pages/login.py")
            
            st.markdown("---")
            
            # Demo stats
            st.markdown("### 🌍 Global Impact")
            
            # Simulated global stats
            st.markdown("""
            <div class="stats-card">
                <div class="stats-number">2.4M</div>
                <div class="stats-label">kg CO₂ Tracked</div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("""
            <div class="stats-card">
                <div class="stats-number">15.7K</div>
                <div class="stats-label">Active Users</div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("""
            <div class="stats-card">
                <div class="stats-number">108</div>
                <div class="stats-label">Trees Saved</div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("---")
            
            st.markdown("### ℹ️ About")
            st.markdown("""
            **CarbonTrace** helps you understand and reduce your environmental impact through:
            
            - 📊 **Accurate Tracking**: Real-time carbon footprint calculation
            - 🎯 **Smart Goals**: Personalized reduction targets
            - 🏆 **Gamification**: Achievements and challenges
            - 📈 **Analytics**: Detailed insights and trends
            - 🌍 **Community**: Join the sustainability movement
            """)

def show_landing_page():
    """Show landing page for non-authenticated users"""
    
    # Hero section
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, #1a1a1a 0%, #2a2a2a 100%);
        border: 2px solid #00d4ff;
        border-radius: 15px;
        padding: 3rem;
        margin-bottom: 3rem;
        text-align: center;
        box-shadow: 0 0 20px rgba(0, 212, 255, 0.3);
    ">
        <h1 style="
            font-size: 4rem;
            font-weight: 700;
            color: #00d4ff;
            margin-bottom: 1rem;
            text-shadow: 0 0 10px rgba(0, 212, 255, 0.5);
        ">🌍 CarbonTrace</h1>
        <h2 style="
            font-size: 1.8rem;
            color: #b0b0b0;
            margin-bottom: 2rem;
            font-weight: 300;
        ">Your Personal Carbon Footprint Tracker</h2>
        <p style="
            font-size: 1.2rem;
            color: #ffffff;
            line-height: 1.6;
            max-width: 700px;
            margin: 0 auto 2rem auto;
        ">
            Take control of your environmental impact. Track your carbon footprint with scientific accuracy, 
            set meaningful reduction goals, and join a global community working towards a sustainable future.
        </p>
        <div style="margin-top: 2rem;">
            <a href="#features" style="
                background: linear-gradient(45deg, #00d4ff, #0099cc);
                color: #000000;
                padding: 1rem 2rem;
                border-radius: 8px;
                text-decoration: none;
                font-weight: 600;
                font-size: 1.1rem;
                margin-right: 1rem;
                display: inline-block;
                transition: all 0.3s ease;
            ">🚀 Get Started</a>
            <a href="#learn-more" style="
                border: 2px solid #00d4ff;
                color: #00d4ff;
                padding: 1rem 2rem;
                border-radius: 8px;
                text-decoration: none;
                font-weight: 600;
                font-size: 1.1rem;
                display: inline-block;
                transition: all 0.3s ease;
            ">📖 Learn More</a>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Features section
    st.markdown('<div id="features"></div>', unsafe_allow_html=True)
    st.markdown("## ✨ Why Choose CarbonTrace?")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">📊</div>
            <div class="feature-title">Accurate Tracking</div>
            <div class="feature-description">
                Scientific carbon calculations based on EPA and IPCC standards. 
                Track transportation, energy, food, and shopping with precision.
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">🎯</div>
            <div class="feature-title">Smart Goals</div>
            <div class="feature-description">
                AI-powered goal recommendations based on your lifestyle. 
                Set achievable targets and track your progress in real-time.
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">🏆</div>
            <div class="feature-title">Gamified Experience</div>
            <div class="feature-description">
                Earn achievements, complete challenges, and compete with friends. 
                Make sustainability fun and engaging.
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Impact section
    st.markdown("## 🌍 Real Environmental Impact")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="stats-card">
            <div class="stats-number">2.4M</div>
            <div class="stats-label">kg CO₂ Tracked</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="stats-card">
            <div class="stats-number">15.7K</div>
            <div class="stats-label">Active Users</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="stats-card">
            <div class="stats-number">108</div>
            <div class="stats-label">Trees Equivalent</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class="stats-card">
            <div class="stats-number">34%</div>
            <div class="stats-label">Avg. Reduction</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # How it works section
    st.markdown('<div id="learn-more"></div>', unsafe_allow_html=True)
    st.markdown("## 🔄 How It Works")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        ### 1️⃣ Track Your Activities
        Log your daily activities - transportation, energy use, food consumption, and purchases. 
        Our AI automatically calculates the carbon footprint using scientific data.
        """)
    
    with col2:
        st.markdown("""
        ### 2️⃣ Set Reduction Goals
        Get personalized recommendations for reducing your carbon footprint. 
        Set monthly targets and track your progress with detailed analytics.
        """)
    
    with col3:
        st.markdown("""
        ### 3️⃣ Make an Impact
        See your real-world environmental impact. Earn achievements, complete challenges, 
        and inspire others to join the sustainability movement.
        """)
    
    st.markdown("---")
    
    # Carbon footprint calculator preview
    st.markdown("## 🧮 Try Our Carbon Calculator")
    
    with st.container():
        st.markdown("### Quick Carbon Footprint Estimate")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("**🚗 Transportation**")
            miles_per_week = st.slider("Miles driven per week", 0, 500, 100)
            transport_co2 = miles_per_week * 0.404  # kg CO2 per mile (EPA average)
            st.metric("Weekly CO₂", f"{transport_co2:.1f} kg")
        
        with col2:
            st.markdown("**⚡ Energy**")
            kwh_per_month = st.slider("kWh used per month", 0, 2000, 877)  # US average
            energy_co2 = (kwh_per_month / 4.33) * 0.5  # Weekly average, kg CO2 per kWh
            st.metric("Weekly CO₂", f"{energy_co2:.1f} kg")
        
        with col3:
            st.markdown("**🍔 Food**")
            meat_meals_per_week = st.slider("Meat meals per week", 0, 21, 10)
            food_co2 = meat_meals_per_week * 2.5  # kg CO2 per meat meal
            st.metric("Weekly CO₂", f"{food_co2:.1f} kg")
        
        # Total calculation
        total_weekly = transport_co2 + energy_co2 + food_co2
        total_annual = total_weekly * 52
        
        st.markdown("---")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                "Weekly Total",
                f"{total_weekly:.1f} kg CO₂",
                f"Annual: {total_annual:.0f} kg"
            )
        
        with col2:
            # Compare to US average (16 tons per year)
            us_average = 16000  # kg per year
            percentage = (total_annual / us_average) * 100
            st.metric(
                "vs US Average",
                f"{percentage:.0f}%",
                f"US avg: 16,000 kg/year"
            )
        
        with col3:
            trees_needed = total_annual / 22  # Trees needed to offset (22kg CO2 per tree per year)
            st.metric(
                "Trees to Offset",
                f"{trees_needed:.0f} trees",
                "Per year"
            )
        
        # Feedback based on footprint
        if total_annual < 8000:
            st.success("🌟 Excellent! Your carbon footprint is well below average.")
        elif total_annual < 12000:
            st.info("👍 Good job! Your footprint is below the US average.")
        elif total_annual < 20000:
            st.warning("⚠️ Your footprint is around average. There's room for improvement.")
        else:
            st.error("🚨 Your carbon footprint is significantly above average. Consider making changes.")
    
    st.markdown("---")
    
    # Call to action
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, #1a1a1a 0%, #2a2a2a 100%);
        border: 2px solid #00d4ff;
        border-radius: 15px;
        padding: 2rem;
        text-align: center;
        margin: 2rem 0;
    ">
        <h2 style="color: #00d4ff; margin-bottom: 1rem;">
            Ready to Make a Difference? 🌱
        </h2>
        <p style="color: #b0b0b0; margin-bottom: 2rem; font-size: 1.1rem;">
            Join thousands of users who are already reducing their carbon footprint with CarbonTrace.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Get started button
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("🚀 Start Tracking Now", use_container_width=True, type="primary"):
            st.switch_page("pages/login.py")

def main():
    load_css()
    
    # Check authentication
    is_authenticated = check_authentication()
    
    # Show navigation
    show_navigation()
    
    # Show appropriate page
    if is_authenticated:
        # Redirect authenticated users to dashboard
        st.switch_page("pages/dashboard.py")
    else:
        # Show landing page for non-authenticated users
        show_landing_page()

if __name__ == "__main__":
    main()
