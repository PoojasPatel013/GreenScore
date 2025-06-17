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
    
    # Initialize form state
    if 'event_type' not in st.session_state:
        st.session_state.event_type = "Transport"
    if 'impact' not in st.session_state:
        st.session_state.impact = 0.0

    # Add innovative animations
    st.markdown("""
        <style>
            .floating-card {
                position: relative;
                animation: float 3s ease-in-out infinite;
            }
            @keyframes float {
                0% { transform: translateY(0); }
                50% { transform: translateY(-20px); }
                100% { transform: translateY(0); }
            }
            
            .glow {
                text-shadow: 0 0 10px rgba(255, 255, 255, 0.8);
            }
            
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
            
            .pulse-card {
                animation: pulse 2s ease-in-out infinite;
            }
            @keyframes pulse {
                0% { transform: scale(1); }
                50% { transform: scale(1.05); }
                100% { transform: scale(1); }
            }
            
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
        </style>
    """, unsafe_allow_html=True)

    # Victorian Header with enhanced animation
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

    # Carbon Footprint Tracker with enhanced UI
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

    # Add Event Form with enhanced UI
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

    # Victorian Events History with enhanced UI
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

    # Points Display with enhanced UI
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

    # Add confetti and sparkle animations
    if st.session_state.events:
        st.markdown("""
            <div class="confetti">
                <div class="confetti-item" style="left: 20%; top: 20%;"></div>
                <div class="confetti-item" style="left: 40%; top: 40%;"></div>
                <div class="confetti-item" style="left: 60%; top: 60%;"></div>
                <div class="confetti-item" style="left: 80%; top: 80%;"></div>
            </div>
            <div class="sparkle" style="left: 50%; top: 50%;"></div>
        """, unsafe_allow_html=True)

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

    # Add gamified animations
    st.markdown("""
        <style>
            .confetti {
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                pointer-events: none;
                z-index: 1000;
            }
            .confetti-item {
                position: absolute;
                width: 10px;
                height: 10px;
                background: #4CAF50;
                border-radius: 50%;
                animation: confetti 2s linear forwards;
            }
            @keyframes confetti {
                0% {
                    transform: translate(0, 0) rotate(0deg);
                    opacity: 1;
                }
                100% {
                    transform: translate(100vw, 100vh) rotate(360deg);
                    opacity: 0;
                }
            }
            .sparkle {
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                pointer-events: none;
                z-index: 1000;
            }
            .sparkle-item {
                position: absolute;
                width: 20px;
                height: 20px;
                background: #FFD700;
                border-radius: 50%;
                animation: sparkle 1s ease-in-out infinite;
            }
            @keyframes sparkle {
                0% {
                    transform: scale(0);
                    opacity: 0;
                }
                50% {
                    transform: scale(1);
                    opacity: 1;
                }
                100% {
                    transform: scale(0);
                    opacity: 0;
                }
            }
        </style>
    """, unsafe_allow_html=True)

    # Victorian Header with animation
    st.markdown("""
        <div class="victorian-header">
            <h1 style="animation: fadeIn 2s ease-in-out;">👑 GreenScore Dashboard</h1>
            <p class="slogan" style="animation: fadeIn 2s ease-in-out 0.5s;">Track Your Carbon Footprint and Earn Rewards</p>
        </div>
    """, unsafe_allow_html=True)

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
            <div class="victorian-grid">
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

    # Carbon Footprint Tracker with animation
    st.markdown("""
        <div class="victorian-tracker" style="animation: slideIn 1s ease-out 1s 1;">
            <h2>🎯 Carbon Footprint Tracker</h2>
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
    with st.form("event_form"):
        st.markdown("""
            <h2>➕ Log Eco Event</h2>
        """, unsafe_allow_html=True)
        
        event_type = st.selectbox("Event Type", ["Transport", "Food", "Energy", "Shopping"])
        impact = st.number_input("Impact Value", min_value=0.0, step=0.1)
        
        if st.form_submit_button("Log Event"):
            if impact > 0:
                event = {
                    'type': event_type,
                    'impact': impact,
                    'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    'points': round(impact * 10)
                }
                st.session_state.events.append(event)
                st.session_state.points += event['points']
                st.session_state.carbon_value += impact
                st.balloons()
                st.success(f"Event logged! +{event['points']} Points earned!")

    # Victorian Events History with animation
    if st.session_state.events:
        st.markdown("""
            <div class="victorian-events" style="animation: fadeIn 1s ease-in-out 1.5s;">
                <h2>📜 Recent Eco Events</h2>
                <div class="events-list victorian-list">
        """, unsafe_allow_html=True)

        for event in reversed(st.session_state.events):
            st.markdown("""
                <div class="event-item victorian-item" style="animation: slideIn 0.5s ease-out;">
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
            <div class="victorian-events" style="animation: fadeIn 1s ease-in-out 1.5s;">
                <h2>📜 Recent Eco Events</h2>
                <p class="victorian-text">No events logged yet. Start tracking your eco-impact today!</p>
            </div>
        """, unsafe_allow_html=True)

    # Points Display with animation
    st.markdown("""
        <div class="victorian-section" style="animation: fadeIn 1s ease-in-out 2s;">
            <h2>🏆 Your Points</h2>
            <div class="victorian-value" id="points-value">{points} 🌟</div>
        </div>
    """.format(points=st.session_state.points), unsafe_allow_html=True)

    # Add CSS animations
    st.markdown("""
        <style>
            @keyframes fadeIn {
                from { opacity: 0; }
                to { opacity: 1; }
            }
            @keyframes slideIn {
                from { transform: translateX(-100%); }
                to { transform: translateX(0); }
            }
        </style>
    """, unsafe_allow_html=True)

    # Add confetti animation when logging events
    if st.session_state.events:
        st.markdown("""
            <div class="confetti">
                <div class="confetti-item" style="left: 20%; top: 20%;"></div>
                <div class="confetti-item" style="left: 40%; top: 40%;"></div>
                <div class="confetti-item" style="left: 60%; top: 60%;"></div>
                <div class="confetti-item" style="left: 80%; top: 80%;"></div>
            </div>
        """, unsafe_allow_html=True)

    # Add sparkle animation
    st.markdown("""
        <div class="sparkle">
            <div class="sparkle-item" style="left: 50%; top: 50%;"></div>
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

    # Victorian Event Logging
    if st.button("📜 Log Eco Event"):
        event_type = st.selectbox("📜 Event Type", ["Transport", "Food", "Energy", "Shopping"])
        impact = st.number_input("🔮 Impact (kg CO₂)", min_value=0.0, value=0.0)
        if impact > 0:
            event = {
                'type': event_type,
                'impact': impact,
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M")
            }
            st.session_state.events.append(event)
            st.session_state.user_data['carbon_footprint'] += impact
            st.balloons()  # Add visual feedback

    # Victorian Events History
    if st.session_state.events:
        st.markdown("""
            <div class="victorian-events">
                <h2>📜 Recent Eco Events</h2>
                <div class="events-list victorian-list">
        """, unsafe_allow_html=True)

        for event in reversed(st.session_state.events):
            st.markdown("""
                <div class="event-item victorian-item">
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
                points=round(event['impact'] * 10)
            ), unsafe_allow_html=True)

        st.markdown("""
                </div>
            </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
            <div class="victorian-events">
                <h2>📜 Recent Eco Events</h2>
                <p class="victorian-text">No events logged yet. Start tracking your eco-impact today!</p>
            </div>
        """, unsafe_allow_html=True)

if __name__ == "__main__":
    dashboard()
