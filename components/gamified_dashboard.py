import streamlit as st
import plotly.express as px
import pandas as pd
from backend import Gamification
from datetime import datetime

# Initialize gamification
gamification = Gamification()

def dashboard():
    """
    Display the gamified dashboard with carbon footprint tracking and eco events.
    """
    # Initialize session state
    if 'events' not in st.session_state:
        st.session_state.events = []
    if 'user_data' not in st.session_state:
        st.session_state.user_data = {
            'transport': 0,
            'diet': 'vegetarian',
            'energy': 0,
            'shopping': 0
        }
    if 'points' not in st.session_state:
        st.session_state.points = 0
    if 'carbon_value' not in st.session_state:
        st.session_state.carbon_value = 0.0
    if 'last_event_time' not in st.session_state:
        st.session_state.last_event_time = datetime.now()
    if 'level' not in st.session_state:
        st.session_state.level = 1
    if 'xp' not in st.session_state:
        st.session_state.xp = 0
    if 'next_level' not in st.session_state:
        st.session_state.next_level = 100
    if 'achievements' not in st.session_state:
        st.session_state.achievements = []
    if 'daily_goal' not in st.session_state:
        st.session_state.daily_goal = 100
    if 'daily_progress' not in st.session_state:
        st.session_state.daily_progress = 0
    if 'event_type' not in st.session_state:
        st.session_state.event_type = "Transport"
    if 'impact' not in st.session_state:
        st.session_state.impact = 0.0
    if 'show_tips' not in st.session_state:
        st.session_state.show_tips = True
    if 'tip_index' not in st.session_state:
        st.session_state.tip_index = 0

    # Add dynamic animations and styles
    st.markdown("""
        <style>
            /* Add dynamic animations */
            .floating-card {
                position: relative;
                animation: float 3s ease-in-out infinite;
            }
            @keyframes float {
                0% { transform: translateY(0); }
                50% { transform: translateY(-20px); }
                100% { transform: translateY(0); }
            }
            
            /* Add glowing effects */
            .glow {
                text-shadow: 0 0 10px rgba(255, 255, 255, 0.8);
            }
            
            /* Add rainbow text animation */
            .rainbow-text {
                background: linear-gradient(45deg, #ff6b6b, #4ecdc4, #45b7d1, #96c93d);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                animation: rainbow 2s ease-in-out infinite;
            }
            @keyframes rainbow {
                0% { background-position: 0% 50%; }
                100% { background-position: 100% 50%; }
            }
            
            /* Add pulse animation */
            .pulse-card {
                animation: pulse 2s ease-in-out infinite;
            }
            @keyframes pulse {
                0% { transform: scale(1); }
                50% { transform: scale(1.05); }
                100% { transform: scale(1); }
            }
            
            /* Add sparkle animation */
            .sparkle {
                position: absolute;
                width: 10px;
                height: 10px;
                background: #fff;
                border-radius: 50%;
                animation: sparkle 1s ease-in-out infinite;
            }
            @keyframes sparkle {
                0% { transform: scale(0); opacity: 0; }
                50% { transform: scale(1); opacity: 1; }
                100% { transform: scale(0); opacity: 0; }
            }
            
            /* Add confetti animation */
            .confetti-container {
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                pointer-events: none;
            }
            .confetti-piece {
                position: absolute;
                width: 10px;
                height: 10px;
                background: linear-gradient(45deg, #ff6b6b, #4ecdc4, #45b7d1, #96c93d);
                border-radius: 50%;
                animation: confetti 2s ease-in-out infinite;
            }
            @keyframes confetti {
                0% { transform: translateY(0) rotate(0deg); }
                100% { transform: translateY(100vh) rotate(360deg); }
            }
            
            /* Add tip container styles */
            .tip-container {
                position: fixed;
                bottom: 20px;
                right: 20px;
                background: rgba(255, 255, 255, 0.9);
                padding: 1rem;
                border-radius: 10px;
                box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
                animation: slideIn 0.5s ease-in-out;
            }
            
            .tip-text {
                font-family: 'Crimson Text', serif;
                color: #333;
                margin: 0;
            }
            
            .tip-button {
                background: linear-gradient(135deg, #6c5ce7, #a369ff);
                color: white;
                border: none;
                padding: 0.5rem 1rem;
                border-radius: 20px;
                cursor: pointer;
                font-family: 'Crimson Text', serif;
                transition: transform 0.2s;
            }
            
            .tip-button:hover {
                transform: scale(1.1);
            }
            
            @keyframes slideIn {
                from {
                    transform: translateX(100%);
                    opacity: 0;
                }
                to {
                    transform: translateX(0);
                    opacity: 1;
                }
            }
            
            /* Add level progress bar styles */
            .level-container {
                background: linear-gradient(135deg, #6c5ce7, #a369ff);
                padding: 2rem;
                border-radius: 10px;
                box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
            }
            
            .level-info {
                font-family: 'Crimson Text', serif;
                color: white;
                margin: 0;
            }
            
            .progress-bar {
                width: 100%;
                height: 10px;
                background: #fff;
                border-radius: 10px;
                overflow: hidden;
            }
            
            .progress {
                width: 0%;
                height: 100%;
                background: linear-gradient(135deg, #6c5ce7, #a369ff);
                border-radius: 10px;
            }
        </style>
    """, unsafe_allow_html=True)

    # Add Victorian header
    st.markdown("""
        <div class="victorian-header">
            <h1 class="glow rainbow-text">👑 GreenScore Dashboard</h1>
            <p class="slogan">Track Your Carbon Footprint and Earn Rewards</p>
        </div>
    """, unsafe_allow_html=True)

    # Level Progress Bar
    st.markdown("""
        <div class="level-container">
            <div class="level-info">
                <h3>Level {level}</h3>
                <div class="progress-bar">
                    <div class="progress" style="width: {progress}%"></div>
                </div>
                <span>{xp}/{next_level} XP</span>
            </div>
        </div>
    """.format(
        level=st.session_state.level,
        xp=st.session_state.xp,
        next_level=st.session_state.next_level,
        progress=(st.session_state.xp / st.session_state.next_level) * 100
    ), unsafe_allow_html=True)

    # Carbon Footprint Tracker
    st.markdown("""
        <div class="victorian-tracker floating-card">
            <h2 class="rainbow-text">🎯 Carbon Footprint Tracker</h2>
            <div class="victorian-inputs">
                <div class="victorian-group">
                    <label class="victorian-label">Transport Distance (km)</label>
                    <input type="number" class="victorian-input" 
                           value="{}" 
                           onchange="this.dispatchEvent(new Event('input'))" 
                           oninput="this.value = Math.abs(this.value)" 
                           min="0" 
                           step="0.1" 
                           id="transport">
                </div>
                <div class="victorian-group">
                    <label class="victorian-label">Diet Type</label>
                    <select class="victorian-select" id="diet">
                        <option value="vegetarian">Vegetarian</option>
                        <option value="pescatarian">Pescatarian</option>
                        <option value="omnivore">Omnivore</option>
                    </select>
                </div>
                <div class="victorian-group">
                    <label class="victorian-label">Energy Usage (kWh)</label>
                    <input type="number" class="victorian-input" 
                           value="{}" 
                           onchange="this.dispatchEvent(new Event('input'))" 
                           oninput="this.value = Math.abs(this.value)" 
                           min="0" 
                           step="0.1" 
                           id="energy">
                </div>
                <div class="victorian-group">
                    <label class="victorian-label">Shopping Amount ($)</label>
                    <input type="number" class="victorian-input" 
                           value="{}" 
                           onchange="this.dispatchEvent(new Event('input'))" 
                           oninput="this.value = Math.abs(this.value)" 
                           min="0" 
                           step="0.1" 
                           id="shopping">
                </div>
            </div>
            <div class="victorian-value" id="carbon-value">{:.2f} kg CO₂</div>
        </div>
    """.format(st.session_state.user_data['transport'],
               st.session_state.user_data['diet'],
               st.session_state.user_data['energy'],
               st.session_state.user_data['shopping'],
               st.session_state.carbon_value), unsafe_allow_html=True)

    # Add Event Form
    with st.form("event_form_1"):
        st.markdown("""
            <div class="event-form-container floating-card">
                <h2 class="rainbow-text">➕ Log Eco Event</h2>
                <div class="event-form">
                    <div class="event-type">
                        <label class="victorian-label">Event Type</label>
                        <select class="victorian-select" 
                                name="event_type" 
                                key="event_type_select">
                            <option value="Transport">Transport 🚴‍♂️</option>
                            <option value="Food">Food 🥗</option>
                            <option value="Energy">Energy ⚡</option>
                            <option value="Shopping">Shopping 🛍️</option>
                        </select>
                    </div>
                    <div class="impact-value">
                        <label class="victorian-label">Impact Value</label>
                        <input type="number" 
                               class="victorian-input" 
                               name="impact" 
                               min="0" 
                               step="0.1"
                               key="impact_input">
                    </div>
                    <button type="submit" 
                            class="submit-button pulse-card"
                            key="submit_button">
                        Log Event 🚀
                    </button>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        # Add submit button and handle form submission
        submit_button = st.form_submit_button("Log Event", type="primary")
        if submit_button:
            # Get form values
            event_type = st.session_state.event_type_select
            impact = st.session_state.impact_input
            
            if impact and float(impact) > 0:
                event = {
                    'type': event_type,
                    'impact': float(impact),
                    'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    'points': round(float(impact) * 10)
                }
                st.session_state.events.append(event)
                st.session_state.points += event['points']
                st.session_state.carbon_value += float(impact)
                st.session_state.xp += event['points']
                
                # Level up logic
                if st.session_state.xp >= st.session_state.next_level:
                    st.session_state.level += 1
                    st.session_state.xp = 0
                    st.session_state.next_level = int(st.session_state.next_level * 1.5)
                    st.success(f"Level up! You're now Level {st.session_state.level}!")
                    
                st.balloons()
                st.success(f"Event logged! +{event['points']} Points earned!")
                
                # Reset form values
                st.session_state.event_type_select = "Transport"
                st.session_state.impact_input = 0.0
                
                # Clear the form
                st.experimental_rerun()

    # Events History
    if st.session_state.events:
        st.markdown("""
            <div class="victorian-events floating-card">
                <h2 class="rainbow-text">📜 Recent Eco Events</h2>
                <div class="events-list victorian-list">
        """, unsafe_allow_html=True)

        for event in reversed(st.session_state.events):
            st.markdown("""
                <div class="event-item victorian-item pulse-card">
                    <div class="event-icon victorian-icon">{icon}</div>
                    <div class="event-details victorian-details">
                        <p class="victorian-text">{type} - Saved {impact}kg CO₂</p>
                        <span class="timestamp victorian-timestamp">{time}</span>
                    </div>
                    <div class="event-reward victorian-reward">
                        <span class="victorian-points">+{points} Points</span>
                    </div>
                </div>
            """.format(
                icon={
                    "Transport": "🚴‍♂️",
                    "Food": "🥗",
                    "Energy": "⚡",
                    "Shopping": "🛍️"
                }[event['type']],
                type=event['type'],
                impact=event['impact'],
                time=event['timestamp'],
                points=event['points']
            ), unsafe_allow_html=True)

        st.markdown("""
                </div>
            </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
            <div class="victorian-events floating-card">
                <h2 class="rainbow-text">📜 Recent Eco Events</h2>
                <p class="victorian-text">No events logged yet. Start tracking your eco-impact today!</p>
            </div>
        """, unsafe_allow_html=True)

    # Points Display
    st.markdown("""
        <div class="points-container floating-card">
            <h2 class="rainbow-text">🏆 Your Points</h2>
            <div class="points-value" id="points-value">{points} 🌟</div>
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

    # Add dynamic tip display
    if st.session_state.show_tips:

    # Add CSS for animations
    st.markdown("""
        <style>
            .confetti-container {
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                pointer-events: none;
            }
            
            .confetti-piece {
                position: absolute;
                width: 10px;
                height: 10px;
                background: linear-gradient(45deg, #ff6b6b, #4ecdc4, #45b7d1, #96c93d);
                border-radius: 50%;
                animation: confetti 2s ease-in-out infinite;
            }
            
            @keyframes confetti {
                0% { transform: translateY(0) rotate(0deg); }
                100% { transform: translateY(100vh) rotate(360deg); }
            }
        </style>
    """, unsafe_allow_html=True)
    
if __name__ == "__main__":
    dashboard()
