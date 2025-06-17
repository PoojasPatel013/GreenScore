import streamlit as st
import plotly.express as px
import pandas as pd
from backend import Gamification
from datetime import datetime

# Initialize gamification
gamification = Gamification()

def dashboard(user_id):
    """
    Display the gamified dashboard with carbon footprint tracking and eco events.
    """
    # Initialize session state
    state_defaults = {
        'user_id': user_id,
        'events': [],
        'user_data': {
            'transport': 0,
            'diet': 'vegetarian',
            'energy': 0,
            'shopping': 0
        },
        'points': 0,
        'carbon_value': 0.0,
        'last_event_time': datetime.now(),
        'level': 1,
        'xp': 0,
        'next_level': 100,
        'achievements': [],
        'daily_goal': 100,
        'daily_progress': 0,
        'event_type': "Transport",
        'impact': 0.0,
        'show_tips': True,
        'tip_index': 0
    }

    for key, value in state_defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

    # Custom CSS styles for modern UI
    st.markdown("""
        <style>
        .main { background-color: #f4f9f4; padding: 20px; }
        .victorian-header h1 { font-size: 2.5em; font-family: 'Trebuchet MS'; color: #2e8b57; text-align: center; }
        .slogan { text-align: center; font-size: 1.2em; margin-top: -10px; color: #555; }
        .floating-card { background-color: white; padding: 20px; border-radius: 15px; box-shadow: 0 4px 8px rgba(0,0,0,0.1); margin-top: 20px; }
        .rainbow-text { background: linear-gradient(to right, #56ab2f, #a8e063); -webkit-background-clip: text; color: transparent; font-weight: bold; }
        .progress-bar { background-color: #ddd; border-radius: 10px; width: 100%; height: 20px; overflow: hidden; }
        .progress { background-color: #2e8b57; height: 100%; border-radius: 10px; transition: width 0.4s ease-in-out; }
        .victorian-inputs .victorian-group { margin-bottom: 10px; }
        .victorian-label { font-weight: bold; display: block; margin-bottom: 5px; }
        .points-value { font-size: 2em; text-align: center; font-weight: bold; color: #228B22; }
        .breakdown-item { display: flex; justify-content: space-between; padding: 4px 0; font-size: 1em; }
        </style>
    """, unsafe_allow_html=True)

    # Header
    st.markdown("""
        <div class="victorian-header">
            <h1 class="rainbow-text">👑 GreenScore Dashboard</h1>
            <p class="slogan">Track Your Carbon Footprint and Earn Rewards</p>
        </div>
    """, unsafe_allow_html=True)

    # Level Progress Bar
    st.markdown("""
        <div class="floating-card">
            <h3>🌿 Level {level}</h3>
            <div class="progress-bar">
                <div class="progress" style="width: {progress}%"></div>
            </div>
            <p style="text-align: center;">{xp}/{next_level} XP</p>
        </div>
    """.format(
        level=st.session_state.level,
        xp=st.session_state.xp,
        next_level=st.session_state.next_level,
        progress=(st.session_state.xp / st.session_state.next_level) * 100
    ), unsafe_allow_html=True)

    # Carbon Footprint Tracker
    with st.expander("🎯 Carbon Footprint Tracker", expanded=True):
        transport = st.slider(
            "🚗 Transport Distance (km)", 
            0, 100, 
            value=st.session_state.user_data['transport'],
            key=f'transport_slider_{st.session_state.user_id}'
        )
        
        diet = st.selectbox(
            "🥗 Diet Type", 
            options=["vegetarian", "pescatarian", "omnivore"],
            index=["vegetarian", "pescatarian", "omnivore"].index(st.session_state.user_data['diet']),
            key=f'diet_select_{st.session_state.user_id}'
        )
        
        energy = st.slider(
            "⚡ Energy Usage (kWh)", 
            0, 100, 
            value=st.session_state.user_data['energy'],
            key=f'energy_slider_{st.session_state.user_id}'
        )
        
        shopping = st.slider(
            "🛍️ Shopping Amount ($)", 
            0, 500, 
            value=st.session_state.user_data['shopping'],
            key=f'shopping_slider_{st.session_state.user_id}'
        )
        
        # Update user data when any input changes
        if st.session_state.user_data['transport'] != transport or \
           st.session_state.user_data['diet'] != diet or \
           st.session_state.user_data['energy'] != energy or \
           st.session_state.user_data['shopping'] != shopping:
            
            # Calculate carbon impact
            carbon_impact = gamification.calculate_carbon_impact(
                transport=transport,
                diet=diet,
                energy=energy,
                shopping=shopping
            )
            
            # Update user data and session state
            st.session_state.user_data = {
                'transport': transport,
                'diet': diet,
                'energy': energy,
                'shopping': shopping
            }
            st.session_state.carbon_value = carbon_impact
            
            # Log eco event
            event = {
                'event_type': 'carbon_tracking',
                'impact': carbon_impact,
                'points': gamification.calculate_points(carbon_impact),
                'timestamp': datetime.now(),
                'description': f"Tracked carbon footprint: {carbon_impact:.2f} kg CO₂"
            }
            
            # Update points and progress
            st.session_state.points += event['points']
            st.session_state.xp += event['points']
            
            # Check for level up
            if st.session_state.xp >= st.session_state.next_level:
                st.session_state.level += 1
                st.session_state.xp = 0
                st.session_state.next_level = st.session_state.level * 100
                
                # Show level up notification
                st.success(f"Congratulations! You've reached Level {st.session_state.level}!")
            
            # Update progress percentage
            st.session_state.progress = (st.session_state.xp / st.session_state.next_level) * 100
            
            # Add event to history
            st.session_state.events.append(event)
            
            # Update UI immediately
            st.experimental_rerun()
        
        st.markdown(f"**Estimated CO₂:** `{st.session_state.carbon_value:.2f} kg`")

    # Points and Levels Display
    st.markdown("""
        <div class="points-container floating-card">
            <h2 class="rainbow-text">🏆 Your Points</h2>
            <div class="points-value">{points} 🌟</div>
            <div class="points-breakdown">
                <div class="breakdown-item">
                    <span class="label">Total Points:</span>
                    <span class="value">{points}</span>
                </div>
                <div class="breakdown-item">
                    <span class="label">Level:</span>
                    <span class="value">{level}</span>
                </div>
                <div class="breakdown-item">
                    <span class="label">XP:</span>
                    <span class="value">{xp}/{next_level}</span>
                </div>
            </div>
        </div>
    """.format(
        points=st.session_state.points,
        level=st.session_state.level,
        xp=st.session_state.xp,
        next_level=st.session_state.next_level
    ), unsafe_allow_html=True)

if __name__ == "__main__":
    dashboard()
