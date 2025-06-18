import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json
import time
import random
from pathlib import Path

# Configure page
st.set_page_config(
    page_title="🌱 GreenScore Elite",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for regal and modern styling
def load_custom_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;700&family=Inter:wght@300;400;500;600;700&display=swap');
    
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        min-height: 100vh;
    }
    
    .stApp {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    }
    
    .metric-card {
        background: linear-gradient(145deg, #ffffff 0%, #f8f9ff 100%);
        border-radius: 20px;
        padding: 25px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        border: 1px solid rgba(255,255,255,0.2);
        backdrop-filter: blur(10px);
        transition: all 0.3s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 20px 40px rgba(0,0,0,0.15);
    }
    
    .royal-title {
        font-family: 'Playfair Display', serif;
        font-size: 3.5rem;
        font-weight: 700;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 10px;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }
    
    .subtitle {
        font-family: 'Inter', sans-serif;
        font-size: 1.2rem;
        color: #6c757d;
        text-align: center;
        margin-bottom: 30px;
    }
    
    .achievement-badge {
        background: linear-gradient(135deg, #ffd700 0%, #ffed4e 100%);
        border-radius: 50px;
        padding: 10px 20px;
        color: #333;
        font-weight: 600;
        display: inline-block;
        margin: 5px;
        box-shadow: 0 5px 15px rgba(255,215,0,0.3);
        animation: pulse 2s infinite;
    }
    
    @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.05); }
        100% { transform: scale(1); }
    }
    
    .level-badge {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 15px 25px;
        border-radius: 25px;
        font-weight: 600;
        text-align: center;
        box-shadow: 0 8px 25px rgba(102,126,234,0.3);
    }
    
    .challenge-card {
        background: linear-gradient(145deg, #ffffff 0%, #f8f9ff 100%);
        border-radius: 15px;
        padding: 20px;
        margin: 10px 0;
        border-left: 5px solid #667eea;
        box-shadow: 0 5px 15px rgba(0,0,0,0.08);
        transition: all 0.3s ease;
    }
    
    .challenge-card:hover {
        transform: translateX(5px);
        box-shadow: 0 8px 25px rgba(0,0,0,0.12);
    }
    
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 25px;
        padding: 12px 30px;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 5px 15px rgba(102,126,234,0.3);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(102,126,234,0.4);
    }
    
    .progress-bar {
        background: #f8f9fa;
        border-radius: 10px;
        height: 8px;
        overflow: hidden;
    }
    
    .progress-fill {
        height: 100%;
        border-radius: 10px;
        transition: width 1s ease-in-out;
    }
    </style>
    """, unsafe_allow_html=True)

# Initialize session state
def init_session_state():
    if 'user_data' not in st.session_state:
        st.session_state.user_data = {
            'user_id': 'elite_user_001',
            'username': 'EcoRoyalty',
            'level': 'Carbon Crusader',
            'score': 8750,
            'trees_planted': 23,
            'co2_saved': 1247.5,
            'streak_days': 15,
            'achievements': ['First Steps', 'Week Warrior', 'Tree Planter', 'Carbon Saver'],
            'rank': 3
        }
    
    if 'transactions' not in st.session_state:
        st.session_state.transactions = generate_sample_transactions()
    
    if 'challenges' not in st.session_state:
        st.session_state.challenges = generate_challenges()

def generate_sample_transactions():
    """Generate realistic sample transactions"""
    categories = {
        'Transportation': {
            'items': ['Uber ride downtown', 'Gas station fill-up', 'Metro card refill', 'Taxi to airport', 'Bus pass'],
            'carbon_range': (5, 45),
            'amount_range': (15, 120)
        },
        'Food': {
            'items': ['Whole Foods grocery', 'Local farmers market', 'Restaurant dinner', 'Coffee shop', 'Organic produce'],
            'carbon_range': (3, 25),
            'amount_range': (8, 150)
        },
        'Energy': {
            'items': ['Electricity bill', 'Gas utility bill', 'Solar panel payment', 'Energy efficient appliance'],
            'carbon_range': (20, 80),
            'amount_range': (50, 300)
        },
        'Shopping': {
            'items': ['Amazon electronics', 'Local bookstore', 'Sustainable clothing', 'Refurbished laptop'],
            'carbon_range': (8, 35),
            'amount_range': (25, 500)
        }
    }
    
    transactions = []
    for i in range(30):
        category = random.choice(list(categories.keys()))
        item_data = categories[category]
        
        transaction = {
            'id': i + 1,
            'date': (datetime.now() - timedelta(days=random.randint(0, 30))).strftime('%Y-%m-%d'),
            'description': random.choice(item_data['items']),
            'category': category,
            'amount': round(random.uniform(*item_data['amount_range']), 2),
            'carbon_kg': round(random.uniform(*item_data['carbon_range']), 1),
            'eco_score': random.randint(1, 10)
        }
        transactions.append(transaction)
    
    return sorted(transactions, key=lambda x: x['date'], reverse=True)

def generate_challenges():
    """Generate weekly challenges"""
    return [
        {
            'id': 1,
            'title': '🚌 Public Transport Champion',
            'description': 'Use public transportation 5 times this week',
            'progress': 60,
            'target': 5,
            'current': 3,
            'reward': '500 EcoPoints + Transport Badge',
            'difficulty': 'Medium',
            'expires': '3 days'
        },
        {
            'id': 2,
            'title': '🌱 Plant-Based Pioneer',
            'description': 'Choose 8 plant-based meals this week',
            'progress': 75,
            'target': 8,
            'current': 6,
            'reward': '750 EcoPoints + Veggie Crown',
            'difficulty': 'Easy',
            'expires': '5 days'
        },
        {
            'id': 3,
            'title': '⚡ Energy Efficiency Expert',
            'description': 'Reduce energy consumption by 25%',
            'progress': 40,
            'target': 25,
            'current': 10,
            'reward': '1000 EcoPoints + Energy Master Badge',
            'difficulty': 'Hard',
            'expires': '6 days'
        },
        {
            'id': 4,
            'title': '🛒 Local Shopping Hero',
            'description': 'Make 4 purchases from local businesses',
            'progress': 25,
            'target': 4,
            'current': 1,
            'reward': '400 EcoPoints + Community Champion',
            'difficulty': 'Medium',
            'expires': '4 days'
        }
    ]

def create_animated_metric(title, value, delta, icon, color):
    """Create animated metric cards"""
    st.markdown(f"""
    <div class="metric-card">
        <div style="display: flex; align-items: center; margin-bottom: 10px;">
            <span style="font-size: 2rem; margin-right: 15px;">{icon}</span>
            <span style="font-family: 'Inter', sans-serif; font-weight: 600; color: #6c757d;">{title}</span>
        </div>
        <div style="font-size: 2.5rem; font-weight: 700; color: {color}; margin-bottom: 5px;">
            {value}
        </div>
        <div style="font-size: 0.9rem; color: #28a745; font-weight: 500;">
            {delta}
        </div>
    </div>
    """, unsafe_allow_html=True)

def create_progress_ring(percentage, size=120, color="#667eea"):
    """Create animated circular progress ring"""
    circumference = 2 * 3.14159 * (size/2 - 10)
    stroke_dasharray = circumference
    stroke_dashoffset = circumference - (percentage / 100) * circumference
    
    return f"""
    <div style="display: flex; justify-content: center; align-items: center;">
        <svg width="{size}" height="{size}" style="transform: rotate(-90deg);">
            <circle cx="{size/2}" cy="{size/2}" r="{size/2 - 10}" 
                    fill="transparent" stroke="#e6e6e6" stroke-width="8"/>
            <circle cx="{size/2}" cy="{size/2}" r="{size/2 - 10}" 
                    fill="transparent" stroke="{color}" stroke-width="8"
                    stroke-dasharray="{stroke_dasharray}"
                    stroke-dashoffset="{stroke_dashoffset}"
                    style="transition: stroke-dashoffset 2s ease-in-out;"/>
            <text x="{size/2}" y="{size/2 + 5}" text-anchor="middle" 
                  style="font-size: 1.2rem; font-weight: 600; fill: {color}; transform: rotate(90deg); transform-origin: {size/2}px {size/2}px;">
                {percentage:.0f}%
            </text>
        </svg>
    </div>
    """

def main():
    load_custom_css()
    init_session_state()
    
    # Header
    st.markdown('<h1 class="royal-title">🌱 GreenScore Elite</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Your Royal Path to Carbon Neutrality</p>', unsafe_allow_html=True)
    
    # User level and achievements
    user_data = st.session_state.user_data
    
    col1, col2, col3 = st.columns([2, 3, 2])
    with col2:
        st.markdown(f"""
        <div class="level-badge">
            👑 {user_data['level']} - Rank #{user_data['rank']}
            <br>
            <small>Streak: {user_data['streak_days']} days 🔥</small>
        </div>
        """, unsafe_allow_html=True)
    
    # Achievement badges
    st.markdown("### 🏆 Your Royal Achievements")
    achievement_html = ""
    for achievement in user_data['achievements']:
        achievement_html += f'<span class="achievement-badge">🏅 {achievement}</span>'
    st.markdown(achievement_html, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Navigation
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🏰 Royal Dashboard", 
        "💳 Transaction Vault", 
        "🎯 Noble Quests", 
        "👑 Leaderboard", 
        "🎁 Royal Rewards"
    ])
    
    with tab1:
        show_royal_dashboard()
    
    with tab2:
        show_transaction_vault()
    
    with tab3:
        show_noble_quests()
    
    with tab4:
        show_leaderboard()
    
    with tab5:
        show_royal_rewards()

def show_royal_dashboard():
    st.markdown("## 🏰 Your Royal Environmental Kingdom")
    
    user_data = st.session_state.user_data
    
    # Key metrics with animations
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        create_animated_metric(
            "Royal Score", 
            f"{user_data['score']:,}", 
            "+125 this week", 
            "👑", 
            "#667eea"
        )
    
    with col2:
        create_animated_metric(
            "CO₂ Saved", 
            f"{user_data['co2_saved']:.1f} kg", 
            "+23.5 kg this week", 
            "🌍", 
            "#28a745"
        )
    
    with col3:
        create_animated_metric(
            "Trees Planted", 
            str(user_data['trees_planted']), 
            "+2 this month", 
            "🌳", 
            "#20c997"
        )
    
    with col4:
        create_animated_metric(
            "Eco Impact", 
            "Excellent", 
            "Top 5% globally", 
            "⭐", 
            "#ffc107"
        )
    
    st.markdown("---")
    
    # Progress rings and charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📊 Weekly Progress Rings")
        
        subcol1, subcol2, subcol3 = st.columns(3)
        
        with subcol1:
            st.markdown("**Transport**")
            st.markdown(create_progress_ring(75, 100, "#667eea"), unsafe_allow_html=True)
        
        with subcol2:
            st.markdown("**Energy**")
            st.markdown(create_progress_ring(60, 100, "#28a745"), unsafe_allow_html=True)
        
        with subcol3:
            st.markdown("**Food**")
            st.markdown(create_progress_ring(85, 100, "#20c997"), unsafe_allow_html=True)
    
    with col2:
        st.markdown("### 📈 Carbon Footprint Trend")
        
        # Generate trend data
        dates = [(datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d') for i in range(30, 0, -1)]
        carbon_values = [random.uniform(15, 45) for _ in dates]
        
        df_trend = pd.DataFrame({
            'Date': dates,
            'Carbon (kg)': carbon_values
        })
        
        fig = px.line(df_trend, x='Date', y='Carbon (kg)', 
                     title="Daily Carbon Footprint",
                     color_discrete_sequence=['#667eea'])
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(family="Inter, sans-serif")
        )
        st.plotly_chart(fig, use_container_width=True)

def show_transaction_vault():
    st.markdown("## 💳 Royal Transaction Vault")
    
    # Add new transaction form
    with st.expander("➕ Add New Royal Transaction", expanded=False):
        col1, col2 = st.columns(2)
        
        with col1:
            description = st.text_input("Description", placeholder="Royal grocery shopping")
            amount = st.number_input("Amount ($)", min_value=0.0, step=0.01)
            category = st.selectbox("Category", 
                ["Transportation", "Food", "Energy", "Shopping", "Entertainment"])
        
        with col2:
            date = st.date_input("Date", datetime.now())
            eco_friendly = st.checkbox("Eco-friendly choice")
            
        if st.button("🏰 Add to Royal Vault"):
            if description and amount > 0:
                # Calculate carbon footprint (simplified)
                carbon_factors = {
                    "Transportation": 0.4,
                    "Food": 0.3,
                    "Energy": 0.6,
                    "Shopping": 0.2,
                    "Entertainment": 0.1
                }
                
                carbon_kg = amount * carbon_factors.get(category, 0.3)
                if eco_friendly:
                    carbon_kg *= 0.5  # 50% reduction for eco-friendly choices
                
                new_transaction = {
                    'id': len(st.session_state.transactions) + 1,
                    'date': date.strftime('%Y-%m-%d'),
                    'description': description,
                    'category': category,
                    'amount': amount,
                    'carbon_kg': round(carbon_kg, 1),
                    'eco_score': 9 if eco_friendly else random.randint(3, 7)
                }
                
                st.session_state.transactions.insert(0, new_transaction)
                st.success(f"✨ Transaction added! Carbon footprint: {carbon_kg:.1f} kg CO₂")
                time.sleep(1)
                st.rerun()
    
    # Recent transactions
    st.markdown("### 📋 Recent Royal Transactions")
    
    transactions = st.session_state.transactions[:10]
    
    for transaction in transactions:
        eco_color = "#28a745" if transaction['eco_score'] >= 7 else "#ffc107" if transaction['eco_score'] >= 4 else "#dc3545"
        
        with st.container():
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.write(f"**{transaction['description']}**")
                st.write(f"*{transaction['date']} • {transaction['category']}*")
            
            with col2:
                st.write(f"**${transaction['amount']:.2f}**")
                st.write(f"🌍 {transaction['carbon_kg']} kg CO₂")
                st.markdown(f"<span style='color: {eco_color}'>Eco Score: {transaction['eco_score']}/10</span>", 
                           unsafe_allow_html=True)
            
            st.markdown("---")

def show_noble_quests():
    st.markdown("## 🎯 Noble Environmental Quests")
    
    challenges = st.session_state.challenges
    
    # Challenge statistics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        active_challenges = len([c for c in challenges if c['progress'] < 100])
        create_animated_metric("Active Quests", str(active_challenges), "4 new this week", "⚔️", "#667eea")
    
    with col2:
        completed = len([c for c in challenges if c['progress'] >= 100])
        create_animated_metric("Completed", str(completed), "+2 this week", "✅", "#28a745")
    
    with col3:
        total_rewards = sum([500, 750, 1000, 400])  # Sample rewards
        create_animated_metric("Total Rewards", f"{total_rewards:,}", "EcoPoints earned", "💎", "#ffc107")
    
    with col4:
        avg_progress = sum([c['progress'] for c in challenges]) / len(challenges)
        create_animated_metric("Avg Progress", f"{avg_progress:.0f}%", "Excellent pace", "📈", "#20c997")
    
    st.markdown("---")
    
    # Challenge cards using Streamlit components
    for challenge in challenges:
        difficulty_colors = {
            'Easy': '#28a745',
            'Medium': '#ffc107', 
            'Hard': '#dc3545'
        }
        
        difficulty_color = difficulty_colors.get(challenge['difficulty'], '#6c757d')
        progress_color = "#28a745" if challenge['progress'] >= 75 else "#ffc107" if challenge['progress'] >= 50 else "#dc3545"
        
        with st.container():
            # Challenge header
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.markdown(f"### {challenge['title']}")
                st.write(challenge['description'])
                
                # Difficulty and expiry badges
                col_a, col_b = st.columns(2)
                with col_a:
                    st.markdown(f"<span style='background: {difficulty_color}; color: white; padding: 4px 12px; border-radius: 15px; font-size: 0.8rem; font-weight: 600;'>{challenge['difficulty']}</span>", 
                               unsafe_allow_html=True)
                with col_b:
                    st.write(f"⏰ Expires in {challenge['expires']}")
            
            with col2:
                st.metric("Progress", f"{challenge['progress']}%", f"{challenge['current']}/{challenge['target']}")
            
            # Progress bar
            progress_width = challenge['progress']
            st.markdown(f"""
            <div class="progress-bar">
                <div class="progress-fill" style="width: {progress_width}%; background: linear-gradient(90deg, {progress_color}, {progress_color}aa);"></div>
            </div>
            """, unsafe_allow_html=True)
            
            # Reward and action
            col1, col2 = st.columns([2, 1])
            with col1:
                st.write(f"🎁 **Reward:** {challenge['reward']}")
            
            with col2:
                if challenge['progress'] >= 100:
                    if st.button("🏆 Claim Reward", key=f"claim_{challenge['id']}"):
                        st.success("Reward claimed! 🎉")
                else:
                    if st.button("⚡ Continue Quest", key=f"continue_{challenge['id']}"):
                        st.info("Keep up the great work! 💪")
            
            st.markdown("---")

def show_leaderboard():
    st.markdown("## 👑 Royal Leaderboard")
    
    # Generate leaderboard data
    leaderboard_data = [
        {'rank': 1, 'username': 'EcoEmperor', 'score': 12450, 'level': 'Planet Protector', 'streak': 45, 'country': '🇺🇸'},
        {'rank': 2, 'username': 'GreenGoddess', 'score': 11800, 'level': 'Carbon Crusher', 'streak': 38, 'country': '🇨🇦'},
        {'rank': 3, 'username': 'EcoRoyalty', 'score': 8750, 'level': 'Carbon Crusader', 'streak': 15, 'country': '🇺🇸'},  # User
        {'rank': 4, 'username': 'SustainabilityKing', 'score': 8200, 'level': 'Green Warrior', 'streak': 22, 'country': '🇬🇧'},
        {'rank': 5, 'username': 'ClimateChampion', 'score': 7950, 'level': 'Green Warrior', 'streak': 31, 'country': '🇩🇪'},
    ]
    
    # Leaderboard stats
    col1, col2, col3 = st.columns(3)
    
    with col1:
        create_animated_metric("Your Rank", "#3", "↑2 this week", "👑", "#667eea")
    
    with col2:
        create_animated_metric("Global Players", "50,247", "+1,234 today", "🌍", "#28a745")
    
    with col3:
        create_animated_metric("Your Percentile", "Top 6%", "Elite status", "⭐", "#ffc107")
    
    st.markdown("---")
    
    # Leaderboard display
    for player in leaderboard_data:
        is_user = player['username'] == 'EcoRoyalty'
        
        crown_emoji = "👑" if player['rank'] == 1 else "🥈" if player['rank'] == 2 else "🥉" if player['rank'] == 3 else "🏅"
        
        with st.container():
            col1, col2, col3 = st.columns([1, 3, 1])
            
            with col1:
                st.markdown(f"## {crown_emoji}")
                st.markdown(f"**#{player['rank']}**")
            
            with col2:
                if is_user:
                    st.markdown(f"### {player['country']} {player['username']} 👑 (You)")
                else:
                    st.markdown(f"### {player['country']} {player['username']}")
                st.write(f"🏆 {player['level']} • 🔥 {player['streak']} day streak")
            
            with col3:
                st.metric("EcoPoints", f"{player['score']:,}")
            
            if is_user:
                st.markdown("---")
            else:
                st.markdown("---")

def show_royal_rewards():
    st.markdown("## 🎁 Royal Rewards Treasury")
    
    user_data = st.session_state.user_data
    
    # Available points
    col1, col2, col3 = st.columns(3)
    
    with col1:
        create_animated_metric("EcoPoints", f"{user_data['score']:,}", "Available to spend", "💎", "#667eea")
    
    with col2:
        create_animated_metric("Trees Planted", str(user_data['trees_planted']), "Real impact made", "🌳", "#28a745")
    
    with col3:
        create_animated_metric("Rewards Claimed", "7", "This month", "🏆", "#ffc107")
    
    st.markdown("---")
    
    # Reward categories
    st.markdown("### 🌱 Environmental Impact")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("#### 🌳 Plant a Tree")
        st.write("Plant a real tree in partnership with One Tree Planted")
        st.write("**Cost:** 💎 500 EcoPoints")
        if st.button("🛒 Claim Tree", key="tree"):
            if user_data['score'] >= 500:
                st.success("Tree planted! 🌳")
            else:
                st.error("Need more EcoPoints!")
    
    with col2:
        st.markdown("#### 🌍 Carbon Offset")
        st.write("Offset 1 ton of CO₂ through verified projects")
        st.write("**Cost:** 💎 1,000 EcoPoints")
        if st.button("🛒 Claim Offset", key="offset"):
            if user_data['score'] >= 1000:
                st.success("Carbon offset purchased! 🌍")
            else:
                st.error("Need more EcoPoints!")
    
    with col3:
        st.markdown("#### 🐠 Coral Reef Protection")
        st.write("Support coral reef conservation efforts")
        st.write("**Cost:** 💎 2,000 EcoPoints")
        if st.button("🛒 Claim Protection", key="coral"):
            if user_data['score'] >= 2000:
                st.success("Coral reef protected! 🐠")
            else:
                st.error("Need more EcoPoints!")
    
    st.markdown("---")
    
    st.markdown("### 🛍️ Eco-Friendly Products")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("#### 🥢 Bamboo Utensil Set")
        st.write("Sustainable bamboo cutlery set")
        st.write("**Cost:** 💎 300 EcoPoints")
        if st.button("🛒 Claim Utensils", key="utensils"):
            if user_data['score'] >= 300:
                st.success("Bamboo utensils ordered! 🥢")
            else:
                st.error("Need more EcoPoints!")
    
    with col2:
        st.markdown("#### 💧 Reusable Water Bottle")
        st.write("Premium stainless steel water bottle")
        st.write("**Cost:** 💎 400 EcoPoints")
        if st.button("🛒 Claim Bottle", key="bottle"):
            if user_data['score'] >= 400:
                st.success("Water bottle ordered! 💧")
            else:
                st.error("Need more EcoPoints!")
    
    with col3:
        st.markdown("#### ☀️ Solar Power Bank")
        st.write("Portable solar-powered device charger")
        st.write("**Cost:** 💎 800 EcoPoints")
        if st.button("🛒 Claim Power Bank", key="solar"):
            if user_data['score'] >= 800:
                st.success("Solar power bank ordered! ☀️")
            else:
                st.error("Need more EcoPoints!")

if __name__ == "__main__":
    main()
