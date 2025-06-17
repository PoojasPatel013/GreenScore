import streamlit as st
import plotly.express as px
import pandas as pd
from backend import Gamification
from streamlit_lottie import st_lottie
import json
import requests
from datetime import datetime

# Load Lottie animations
def load_lottieurl(url: str):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

# Load animations
eco_avatar = load_lottieurl("https://assets9.lottiefiles.com/packages/lf20_9f9d9f9d.json")
achievement_anim = load_lottieurl("https://assets9.lottiefiles.com/packages/lf20_9f9d9f9d.json")

def dashboard():
    """Main gamified dashboard component"""
    # Initialize gamification
    gamification = Gamification()

    # Session state for progress and achievements
    if 'progress' not in st.session_state:
        st.session_state.progress = 0
    if 'achievements' not in st.session_state:
        st.session_state.achievements = []
    if 'avatar_level' not in st.session_state:
        st.session_state.avatar_level = 1

    # Add external CSS
    with open("static/gamified_styles.css", "r") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

    # Header with Avatar and Level
    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        st.markdown("""
        <div style="text-align: center;">
            <h2>🌱</h2>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div style="text-align: center;">
            <h3>Level {level} Eco Warrior</h3>
            <p>{points} Points • {badges} Badges</p>
        </div>
        """.format(
            level=st.session_state.avatar_level,
            points=st.session_state.progress,
            badges=len(st.session_state.achievements)
        ), unsafe_allow_html=True)
    with col3:
        st.markdown("""
        <div style="text-align: center;">
            <h2>🏆</h2>
        </div>
        """, unsafe_allow_html=True)
        st.button("Claim Rewards", on_click=lambda: st.balloons())

    # Weekly Goal Panel
    st.markdown("""
        <div class="goal-panel">
            <h3>🎯 Weekly Goal</h3>
            <div class="progress-container">
                <div class="progress-bar">
                    <div class="progress-fill" style="width: {progress}%"></div>
                </div>
                <div class="progress-text">
                    <span>{progress}% Complete</span>
                    <span>{points} / 1000 Points</span>
                </div>
            </div>
            <div class="reward-preview">
                <h4>🎁 Next Reward: Level {next_level} Avatar</h4>
            </div>
        </div>
        """.format(
            progress=st.session_state.progress,
            points=st.session_state.progress,
            next_level=st.session_state.avatar_level + 1
        ), unsafe_allow_html=True)

    # Active Challenge
    st.markdown("""
        <div class="challenge-panel">
            <h3>🎯 Active Challenge</h3>
            <div class="challenge-card">
                <div class="challenge-icon">🚴‍♂️</div>
                <div class="challenge-details">
                    <h4>Bike to Work 5x This Week</h4>
                    <p>Progress: {current}/{target} days</p>
                    <div class="challenge-progress">
                        <div class="progress-bar">
                            <div class="progress-fill" style="width: {progress}%"></div>
                        </div>
                    </div>
                </div>
                <div class="challenge-reward">
                    <h4>Reward: +200 Points</h4>
                </div>
            </div>
        </div>
        """.format(
            current=3,
            target=5,
            progress=(3/5)*100
        ), unsafe_allow_html=True)

    # Achievement Grid
    st.markdown("""
        <div class="achievements-panel">
            <h3>🏆 Achievements</h3>
            <div class="achievements-grid">
                <div class="achievement-card">
                    <div class="achievement-icon">🌱</div>
                    <div class="achievement-details">
                        <h4>Green Newbie</h4>
                        <p>Completed first week</p>
                    </div>
                </div>
                <div class="achievement-card">
                    <div class="achievement-icon">🚴‍♂️</div>
                    <div class="achievement-details">
                        <h4>Cycle Champion</h4>
                        <p>Biked 10+ times</p>
                    </div>
                </div>
                <div class="achievement-card locked">
                    <div class="achievement-icon">🌳</div>
                    <div class="achievement-details">
                        <h4>Tree Planter</h4>
                        <p>Plant 5 trees</p>
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Carbon Footprint Chart
    data = {
        'Category': ['Transport', 'Food', 'Utilities', 'Shopping', 'Other'],
        'Carbon Footprint': [150, 100, 50, 75, 25],
        'Color': ['#4CAF50', '#8BC34A', '#C5E1A5', '#A5D6A7', '#B2DFDB']
    }
    df = pd.DataFrame(data)

    fig = px.pie(df, values='Carbon Footprint', names='Category', 
                title='Carbon Footprint Distribution',
                color_discrete_sequence=df['Color'])

    st.plotly_chart(fig)

    # Log Event
    if st.button("Log Event"):
        event_type = st.selectbox("Event Type", ["Transport", "Food", "Energy", "Shopping"])
        impact = st.number_input("Impact (kg CO₂)", min_value=0.0, value=0.0)
        if impact > 0:
            event = {
                'type': event_type,
                'impact': impact,
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M")
            }
            st.session_state.events.append(event)
            st.session_state.user_data['carbon_footprint'] += impact

    # Recent Events
    if st.session_state.events:
        st.markdown("""
            <div class="events-panel">
                <h3>📅 Recent Events</h3>
                <div class="events-list">
        """, unsafe_allow_html=True)
        
        for event in reversed(st.session_state.events):
            st.markdown("""
                <div class="event-item">
                    <div class="event-icon">{icon}</div>
                    <div class="event-details">
                        <p>{type} - Saved {impact}kg CO₂</p>
                        <span class="timestamp">{time}</span>
                    </div>
                    <div class="event-reward">
                        <span>+{points} Points</span>
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
                points=round(event['impact'] * 10)
            ), unsafe_allow_html=True)
        
        st.markdown("""
                </div>
            </div>
        """, unsafe_allow_html=True)

if __name__ == "__main__":
    dashboard()
