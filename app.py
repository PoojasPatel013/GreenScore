import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import time
import random
import json

# Configure page
st.set_page_config(
    page_title="CarbonTrace | Footprint Tracker",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Simplified CSS with blue neon theme that works with Streamlit
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
    
    /* Header styling */
    .carbon-header {
        background: linear-gradient(135deg, #1a1a1a 0%, #2a2a2a 100%);
        border: 2px solid #00d4ff;
        border-radius: 15px;
        padding: 2rem;
        margin-bottom: 2rem;
        text-align: center;
        box-shadow: 0 0 20px rgba(0, 212, 255, 0.3);
    }
    
    .app-title {
        font-size: 3rem;
        font-weight: 700;
        color: #00d4ff;
        margin-bottom: 0.5rem;
        text-shadow: 0 0 10px rgba(0, 212, 255, 0.5);
    }
    
    .app-subtitle {
        font-size: 1.2rem;
        color: #b0b0b0;
        margin: 0;
    }
    
    /* Metric cards */
    .metric-card {
        background: linear-gradient(135deg, #1a1a1a 0%, #2a2a2a 100%);
        border: 1px solid #333;
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        transition: all 0.3s ease;
    }
    
    .metric-card:hover {
        border-color: #00d4ff;
        box-shadow: 0 0 15px rgba(0, 212, 255, 0.2);
        transform: translateY(-2px);
    }
    
    .metric-card-blue {
        border-color: #00d4ff;
        box-shadow: 0 0 10px rgba(0, 212, 255, 0.1);
    }
    
    .metric-card-red {
        border-color: #ff4757;
        box-shadow: 0 0 10px rgba(255, 71, 87, 0.1);
    }
    
    .metric-card-orange {
        border-color: #ffa502;
        box-shadow: 0 0 10px rgba(255, 165, 2, 0.1);
    }
    
    .metric-title {
        font-size: 0.9rem;
        color: #888;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 0.5rem;
    }
    
    .metric-value {
        font-size: 2.5rem;
        font-weight: 700;
        margin: 0.5rem 0;
    }
    
    .metric-value-blue { color: #00d4ff; }
    .metric-value-red { color: #ff4757; }
    .metric-value-orange { color: #ffa502; }
    .metric-value-green { color: #2ed573; }
    
    .metric-subtitle {
        font-size: 0.85rem;
        color: #666;
    }
    
    /* Activity cards */
    .activity-card {
        background: #1a1a1a;
        border: 1px solid #333;
        border-radius: 10px;
        padding: 1rem;
        margin-bottom: 0.8rem;
        transition: all 0.3s ease;
    }
    
    .activity-card:hover {
        border-color: #00d4ff;
        box-shadow: 0 0 10px rgba(0, 212, 255, 0.1);
    }
    
    .activity-title {
        font-size: 1.1rem;
        font-weight: 600;
        color: #ffffff;
        margin-bottom: 0.3rem;
    }
    
    .activity-meta {
        font-size: 0.85rem;
        color: #888;
        margin-bottom: 0.5rem;
    }
    
    .activity-values {
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    
    .activity-amount {
        font-size: 1.2rem;
        font-weight: 600;
        color: #00d4ff;
    }
    
    .activity-carbon {
        font-size: 1rem;
        font-weight: 600;
        color: #ff4757;
    }
    
    /* Badges */
    .badge {
        display: inline-block;
        padding: 0.2rem 0.6rem;
        border-radius: 12px;
        font-size: 0.75rem;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .badge-blue {
        background: rgba(0, 212, 255, 0.2);
        color: #00d4ff;
        border: 1px solid #00d4ff;
    }
    
    .badge-red {
        background: rgba(255, 71, 87, 0.2);
        color: #ff4757;
        border: 1px solid #ff4757;
    }
    
    .badge-orange {
        background: rgba(255, 165, 2, 0.2);
        color: #ffa502;
        border: 1px solid #ffa502;
    }
    
    .badge-green {
        background: rgba(46, 213, 115, 0.2);
        color: #2ed573;
        border: 1px solid #2ed573;
    }
    
    /* Progress bars */
    .progress-container {
        background: #333;
        border-radius: 8px;
        height: 8px;
        margin: 1rem 0;
        overflow: hidden;
    }
    
    .progress-bar {
        height: 100%;
        background: linear-gradient(90deg, #00d4ff, #0099cc);
        border-radius: 8px;
        transition: width 1s ease;
    }
    
    /* Challenge cards */
    .challenge-card {
        background: #1a1a1a;
        border: 1px solid #00d4ff;
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 0 15px rgba(0, 212, 255, 0.1);
    }
    
    .challenge-title {
        font-size: 1.3rem;
        font-weight: 600;
        color: #ffffff;
        margin-bottom: 0.5rem;
    }
    
    .challenge-description {
        color: #b0b0b0;
        margin-bottom: 1rem;
        line-height: 1.5;
    }
    
    .challenge-progress {
        font-size: 1.5rem;
        font-weight: 700;
        color: #00d4ff;
        text-align: right;
    }
    
    .challenge-reward {
        color: #00d4ff;
        font-weight: 500;
        margin-top: 1rem;
    }
    
    /* Leaderboard */
    .leaderboard-card {
        background: #1a1a1a;
        border: 1px solid #333;
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        display: flex;
        align-items: center;
        gap: 1.5rem;
        transition: all 0.3s ease;
    }
    
    .leaderboard-card:hover {
        border-color: #00d4ff;
        box-shadow: 0 0 15px rgba(0, 212, 255, 0.1);
    }
    
    .leaderboard-card.user-card {
        border-color: #00d4ff;
        box-shadow: 0 0 20px rgba(0, 212, 255, 0.2);
    }
    
    .rank-number {
        font-size: 2rem;
        font-weight: 700;
        color: #00d4ff;
        min-width: 60px;
        text-align: center;
    }
    
    .user-info {
        flex: 1;
    }
    
    .username {
        font-size: 1.3rem;
        font-weight: 600;
        color: #ffffff;
        margin-bottom: 0.3rem;
    }
    
    .user-stats {
        color: #888;
        font-size: 0.9rem;
    }
    
    .user-score {
        font-size: 1.8rem;
        font-weight: 700;
        color: #00d4ff;
        text-align: right;
        min-width: 120px;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 1rem;
        background: #1a1a1a;
        border-radius: 10px;
        padding: 0.5rem;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: transparent;
        border-radius: 8px;
        color: #888;
        border: none;
    }
    
    .stTabs [aria-selected="true"] {
        background: #00d4ff !important;
        color: #000000 !important;
    }
    
    /* Buttons */
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
    
    /* Hide Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# Initialize session state
def init_session_state():
    if 'user_data' not in st.session_state:
        st.session_state.user_data = {
            'user_id': 'carbon_tracker_001',
            'username': 'EcoWarrior',
            'level': 'Carbon Conscious',
            'score': 8750,
            'co2_saved': 1247.8,
            'trees_equivalent': 56,
            'streak_days': 23,
            'rank': 3,
            'monthly_target': 500,
            'current_month': 347.2
        }

    if 'transactions' not in st.session_state:
        st.session_state.transactions = generate_sample_transactions()

    if 'challenges' not in st.session_state:
        st.session_state.challenges = generate_challenges()

def generate_sample_transactions():
    """Generate sample carbon footprint transactions"""
    categories = {
        'Transportation': {
            'items': ['Uber ride downtown', 'Gas station fill-up', 'Flight to NYC', 'Metro card refill', 'Electric scooter rental'],
            'carbon_range': (2, 85),
            'amount_range': (5, 450)
        },
        'Energy': {
            'items': ['Electricity bill', 'Gas heating', 'Solar panel credit', 'Smart thermostat savings'],
            'carbon_range': (15, 120),
            'amount_range': (80, 350)
        },
        'Food': {
            'items': ['Grocery shopping', 'Restaurant dinner', 'Local farmers market', 'Meal delivery', 'Coffee shop'],
            'carbon_range': (1, 35),
            'amount_range': (8, 120)
        },
        'Shopping': {
            'items': ['Online purchase', 'Electronics store', 'Clothing retail', 'Local bookstore', 'Hardware store'],
            'carbon_range': (3, 45),
            'amount_range': (15, 300)
        }
    }

    transactions = []
    for i in range(25):
        category = random.choice(list(categories.keys()))
        item_data = categories[category]
        
        transaction = {
            'id': i + 1,
            'date': (datetime.now() - timedelta(days=random.randint(0, 30))).strftime('%Y-%m-%d'),
            'description': random.choice(item_data['items']),
            'category': category,
            'amount': round(random.uniform(*item_data['amount_range']), 2),
            'carbon_kg': round(random.uniform(*item_data['carbon_range']), 1),
            'impact_level': random.choice(['Low', 'Medium', 'High'])
        }
        transactions.append(transaction)

    return sorted(transactions, key=lambda x: x['date'], reverse=True)

def generate_challenges():
    """Generate carbon reduction challenges"""
    return [
        {
            'id': 1,
            'title': '🚗 Zero Emission Week',
            'description': 'Use only public transport, walking, or cycling for 7 days',
            'progress': 71,
            'target': 7,
            'current': 5,
            'reward': '500 EcoPoints + Green Commuter Badge',
            'difficulty': 'Medium',
            'expires': '4 days left'
        },
        {
            'id': 2,
            'title': '🌱 Plant-Based Power',
            'description': 'Eat 10 plant-based meals this week',
            'progress': 60,
            'target': 10,
            'current': 6,
            'reward': '300 EcoPoints + Herbivore Hero Badge',
            'difficulty': 'Easy',
            'expires': '6 days left'
        },
        {
            'id': 3,
            'title': '⚡ Energy Efficiency Master',
            'description': 'Reduce home energy consumption by 25%',
            'progress': 45,
            'target': 25,
            'current': 11,
            'reward': '750 EcoPoints + Energy Saver Title',
            'difficulty': 'Hard',
            'expires': '2 weeks left'
        }
    ]

def create_metric_card(title, value, subtitle, color, icon):
    """Create metric cards with proper styling"""
    st.markdown(f"""
    <div class="metric-card metric-card-{color}">
        <div class="metric-title">
            {icon} {title}
        </div>
        <div class="metric-value metric-value-{color}">
            {value}
        </div>
        <div class="metric-subtitle">
            {subtitle}
        </div>
    </div>
    """, unsafe_allow_html=True)

def create_progress_circle(percentage, title, color="blue"):
    """Create simple progress circles using Plotly"""
    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = percentage,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': title, 'font': {'color': '#ffffff', 'size': 16}},
        number = {'font': {'color': '#00d4ff', 'size': 24}},
        gauge = {
            'axis': {'range': [None, 100], 'tickcolor': '#666'},
            'bar': {'color': '#00d4ff'},
            'bgcolor': '#1a1a1a',
            'borderwidth': 2,
            'bordercolor': '#333',
            'steps': [{'range': [0, 100], 'color': '#333'}],
            'threshold': {
                'line': {'color': '#00d4ff', 'width': 4},
                'thickness': 0.75,
                'value': percentage
            }
        }
    ))
    
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font={'color': '#ffffff'},
        height=200,
        margin=dict(l=20, r=20, t=40, b=20)
    )
    
    return fig

def main():
    load_css()
    init_session_state()

    # Header
    st.markdown("""
    <div class="carbon-header">
        <h1 class="app-title">🌍 CARBONTRACE</h1>
        <p class="app-subtitle">Track • Reduce • Impact • Transform</p>
    </div>
    """, unsafe_allow_html=True)

    user_data = st.session_state.user_data

    # Main metrics
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        create_metric_card(
            "Carbon Footprint", 
            f"{user_data['current_month']:.1f} kg", 
            f"Target: {user_data['monthly_target']} kg/month", 
            "red", 
            "🔥"
        )

    with col2:
        create_metric_card(
            "CO₂ Saved", 
            f"{user_data['co2_saved']:.1f} kg", 
            "↗ +89.3 kg this month", 
            "green", 
            "🌱"
        )

    with col3:
        create_metric_card(
            "EcoScore", 
            f"{user_data['score']:,}", 
            f"Rank #{user_data['rank']} globally", 
            "blue", 
            "⭐"
        )

    with col4:
        create_metric_card(
            "Tree Equivalent", 
            str(user_data['trees_equivalent']), 
            f"{user_data['streak_days']} day streak", 
            "orange", 
            "🌳"
        )

    st.markdown("---")

    # Navigation tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "🏠 Dashboard", 
        "📊 Analytics", 
        "🎯 Challenges", 
        "🌍 Eco Impact"
    ])

    with tab1:
        show_dashboard()

    with tab2:
        show_analytics()

    with tab3:
        show_challenges()

    with tab4:
        show_eco_impact()

def show_dashboard():
    st.markdown("## 🏠 Carbon Footprint Dashboard")

    user_data = st.session_state.user_data

    # Progress circles
    col1, col2, col3 = st.columns(3)

    with col1:
        monthly_progress = (user_data['current_month'] / user_data['monthly_target']) * 100
        fig1 = create_progress_circle(min(monthly_progress, 100), "Monthly Target")
        st.plotly_chart(fig1, use_container_width=True)

    with col2:
        reduction_progress = 78
        fig2 = create_progress_circle(reduction_progress, "Reduction Goal")
        st.plotly_chart(fig2, use_container_width=True)

    with col3:
        efficiency_score = 85
        fig3 = create_progress_circle(efficiency_score, "Efficiency Score")
        st.plotly_chart(fig3, use_container_width=True)

    st.markdown("---")

    # Recent transactions and quick actions
    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown("### 📋 Recent Carbon Activities")
        
        transactions = st.session_state.transactions[:8]
        
        for transaction in transactions:
            impact_colors = {'Low': 'green', 'Medium': 'orange', 'High': 'red'}
            color = impact_colors.get(transaction['impact_level'], 'blue')
            
            st.markdown(f"""
            <div class="activity-card">
                <div class="activity-title">{transaction['description']}</div>
                <div class="activity-meta">
                    📅 {transaction['date']} • 📂 {transaction['category']}
                </div>
                <div class="activity-values">
                    <div>
                        <span class="badge badge-{color}">{transaction['impact_level']} Impact</span>
                    </div>
                    <div>
                        <div class="activity-amount">${transaction['amount']:.2f}</div>
                        <div class="activity-carbon">{transaction['carbon_kg']} kg CO₂</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

    with col2:
        st.markdown("### 🎯 Quick Actions")
        
        if st.button("📱 Log New Activity"):
            st.success("🎉 Activity logging opened!")
        
        if st.button("📊 Generate Report"):
            st.info("📈 Generating your carbon report...")
        
        if st.button("🌱 Offset Carbon"):
            st.success("🌍 Carbon offset marketplace opened!")
        
        if st.button("🏆 View Achievements"):
            st.info("🏅 Achievement gallery loaded!")

        st.markdown("---")
        
        st.markdown("### 💡 AI Insights")
        
        insights = [
            {
                'icon': '🚗',
                'title': 'Transportation Alert',
                'message': 'Your transport emissions are 23% above average. Consider carpooling or public transit.',
                'color': 'red'
            },
            {
                'icon': '⚡',
                'title': 'Energy Efficiency',
                'message': 'Great job! Your energy usage is 15% below target this month.',
                'color': 'green'
            },
            {
                'icon': '🍃',
                'title': 'Eco Tip',
                'message': 'Switching to LED bulbs could save 45kg CO₂ annually.',
                'color': 'blue'
            }
        ]
        
        for insight in insights:
            st.markdown(f"""
            <div class="activity-card">
                <div style="display: flex; align-items: center; gap: 1rem;">
                    <span style="font-size: 2rem;">{insight['icon']}</span>
                    <div>
                        <div class="activity-title">{insight['title']}</div>
                        <div style="color: #b0b0b0; font-size: 0.9rem; line-height: 1.4;">
                            {insight['message']}
                        </div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

def show_analytics():
    st.markdown("## 📊 Carbon Analytics")

    # Generate sample data for charts
    dates = [(datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d') for i in range(30, 0, -1)]
    carbon_values = [random.uniform(8, 25) for _ in dates]
    
    # Carbon trend chart
    fig_trend = go.Figure()
    
    fig_trend.add_trace(go.Scatter(
        x=dates,
        y=carbon_values,
        mode='lines+markers',
        name='Daily Carbon Footprint',
        line=dict(color='#00d4ff', width=3),
        marker=dict(color='#00d4ff', size=6),
        fill='tonexty',
        fillcolor='rgba(0, 212, 255, 0.1)'
    ))
    
    fig_trend.update_layout(
        title='Daily Carbon Footprint Trend',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color="#ffffff"),
        title_font=dict(size=18, color="#00d4ff"),
        xaxis=dict(gridcolor='#333'),
        yaxis=dict(gridcolor='#333', title='CO₂ (kg)'),
        height=400
    )
    
    st.plotly_chart(fig_trend, use_container_width=True)

    # Category breakdown
    col1, col2 = st.columns(2)
    
    with col1:
        categories = ['Transportation', 'Energy', 'Food', 'Shopping']
        values = [45, 30, 15, 10]
        colors = ['#ff4757', '#ffa502', '#2ed573', '#00d4ff']
        
        fig_pie = go.Figure(data=[go.Pie(
            labels=categories,
            values=values,
            hole=0.4,
            marker=dict(colors=colors, line=dict(color='#000000', width=2))
        )])
        
        fig_pie.update_layout(
            title='Carbon Footprint by Category',
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color="#ffffff"),
            title_font=dict(size=16, color="#00d4ff"),
            height=350
        )
        
        st.plotly_chart(fig_pie, use_container_width=True)
    
    with col2:
        months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']
        emissions = [420, 380, 350, 320, 290, 347]
        
        fig_bar = go.Figure(data=[go.Bar(
            x=months,
            y=emissions,
            marker=dict(
                color='#00d4ff',
                line=dict(color='#ffffff', width=1)
            )
        )])
        
        fig_bar.update_layout(
            title='Monthly Carbon Emissions',
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color="#ffffff"),
            title_font=dict(size=16, color="#00d4ff"),
            xaxis=dict(gridcolor='#333'),
            yaxis=dict(gridcolor='#333', title='CO₂ (kg)'),
            height=350
        )
        
        st.plotly_chart(fig_bar, use_container_width=True)

def show_challenges():
    st.markdown("## 🎯 Carbon Reduction Challenges")

    challenges = st.session_state.challenges

    for challenge in challenges:
        # Create columns for better layout
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.markdown(f"""
            <div style="
                background: linear-gradient(135deg, #1a1a1a 0%, #2a2a2a 100%);
                border: 1px solid #00d4ff;
                border-radius: 12px;
                padding: 1.5rem;
                margin-bottom: 1rem;
                box-shadow: 0 0 15px rgba(0, 212, 255, 0.1);
            ">
                <h3 style="color: #ffffff; margin: 0 0 0.5rem 0; font-size: 1.3rem;">
                    {challenge['title']}
                </h3>
                <p style="color: #b0b0b0; margin: 0 0 1rem 0; line-height: 1.5;">
                    {challenge['description']}
                </p>
                <div style="display: flex; gap: 1rem; margin-bottom: 1rem;">
                    <span style="
                        background: rgba(0, 212, 255, 0.2);
                        color: #00d4ff;
                        border: 1px solid #00d4ff;
                        padding: 0.2rem 0.6rem;
                        border-radius: 12px;
                        font-size: 0.75rem;
                        font-weight: 500;
                        text-transform: uppercase;
                    ">{challenge['difficulty']}</span>
                    <span style="color: #888; font-size: 0.9rem;">⏰ {challenge['expires']}</span>
                </div>
                <div style="
                    background: #333;
                    border-radius: 8px;
                    height: 8px;
                    margin: 1rem 0;
                    overflow: hidden;
                ">
                    <div style="
                        height: 100%;
                        background: linear-gradient(90deg, #00d4ff, #0099cc);
                        border-radius: 8px;
                        width: {challenge['progress']}%;
                        transition: width 1s ease;
                    "></div>
                </div>
                <div style="color: #00d4ff; font-weight: 500;">
                    🎁 Reward: {challenge['reward']}
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div style="
                background: #1a1a1a;
                border: 1px solid #333;
                border-radius: 12px;
                padding: 1.5rem;
                text-align: center;
                margin-bottom: 1rem;
                height: fit-content;
            ">
                <div style="
                    font-size: 2.5rem;
                    font-weight: 700;
                    color: #00d4ff;
                    margin-bottom: 0.5rem;
                ">{challenge['progress']}%</div>
                <div style="color: #888; font-size: 0.9rem; margin-bottom: 1rem;">
                    {challenge['current']}/{challenge['target']} completed
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            if challenge['progress'] >= 100:
                if st.button("🏆 Claim Reward", key=f"claim_{challenge['id']}", use_container_width=True):
                    st.success("🎉 Reward claimed successfully!")
            else:
                if st.button("⚡ Continue", key=f"continue_{challenge['id']}", use_container_width=True):
                    st.info("💪 Keep up the great work!")

def show_eco_impact():
    st.markdown("## 🌍 Your Eco Impact & Achievements")
    
    # Achievement badges section
    st.markdown("### 🏅 Achievement Gallery")
    
    achievements = [
        {'name': 'First Steps', 'icon': '👶', 'description': 'Started your carbon tracking journey', 'earned': True, 'rarity': 'Common'},
        {'name': 'Week Warrior', 'icon': '⚡', 'description': 'Completed 7 days of tracking', 'earned': True, 'rarity': 'Common'},
        {'name': 'Carbon Crusher', 'icon': '💪', 'description': 'Reduced emissions by 25%', 'earned': True, 'rarity': 'Rare'},
        {'name': 'Tree Hugger', 'icon': '🌳', 'description': 'Offset equivalent to 50 trees', 'earned': True, 'rarity': 'Epic'},
        {'name': 'Green Machine', 'icon': '🤖', 'description': 'Automated 10 eco-friendly habits', 'earned': False, 'rarity': 'Legendary'},
        {'name': 'Planet Protector', 'icon': '🛡️', 'description': 'Saved 1000kg of CO₂', 'earned': False, 'rarity': 'Legendary'},
    ]
    
    # Display achievements in a grid using columns
    cols = st.columns(3)
    for i, achievement in enumerate(achievements):
        with cols[i % 3]:
            if achievement['earned']:
                st.success(f"{achievement['icon']} **{achievement['name']}**")
                st.caption(f"{achievement['description']} • {achievement['rarity']}")
            else:
                st.info(f"🔒 **{achievement['name']}**")
                st.caption(f"{achievement['description']} • {achievement['rarity']}")
    
    st.markdown("---")
    
    # Environmental impact visualization using Streamlit metrics
    st.markdown("### 🌱 Your Environmental Impact")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 🌍 Real-World Impact")
        
        # Use Streamlit metrics for clean display
        st.metric(
            label="🚗 Car Miles Saved",
            value="3,247 miles",
            help="Equivalent to driving from NYC to Los Angeles"
        )
        
        st.metric(
            label="🌳 Trees Planted Equivalent",
            value="56 trees",
            help="Equal to a small forest grove"
        )
        
        st.metric(
            label="⚡ Energy Saved",
            value="2,847 kWh",
            help="Enough to power a home for 3 months"
        )
        
        st.metric(
            label="🐧 Polar Ice Saved",
            value="12.4 m²",
            help="Size of a small room"
        )
    
    with col2:
        st.markdown("#### 📊 How You Compare")
        
        # Create comparison chart using Plotly
        categories = ['You', 'City Average', 'National Average']
        values = [347, 523, 1247]
        colors = ['#2ed573', '#ffa502', '#ff4757']
        
        fig = go.Figure(data=[go.Bar(
            x=categories,
            y=values,
            marker=dict(color=colors),
            text=[f'{v} kg CO₂' for v in values],
            textposition='auto',
        )])
        
        fig.update_layout(
            title='Monthly Carbon Footprint Comparison',
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color="#ffffff"),
            title_font=dict(size=16, color="#00d4ff"),
            xaxis=dict(gridcolor='#333'),
            yaxis=dict(gridcolor='#333', title='CO₂ (kg)'),
            height=300
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Success message
        st.success("🎉 You're 72% below the national average!")
    
    st.markdown("---")
    
    # Fun carbon calculator using Streamlit inputs
    st.markdown("### 🧮 Quick Carbon Calculator")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("**🚗 Transportation**")
        miles = st.number_input("Miles driven this week", min_value=0, value=50, step=5)
        transport_co2 = miles * 0.404  # kg CO2 per mile
        st.metric("CO₂ Impact", f"{transport_co2:.1f} kg")
    
    with col2:
        st.markdown("**⚡ Energy**")
        kwh = st.number_input("kWh used this week", min_value=0, value=150, step=10)
        energy_co2 = kwh * 0.5  # kg CO2 per kWh
        st.metric("CO₂ Impact", f"{energy_co2:.1f} kg")
    
    with col3:
        st.markdown("**🍔 Food**")
        meals = st.number_input("Meat meals this week", min_value=0, value=7, step=1)
        food_co2 = meals * 2.5  # kg CO2 per meat meal
        st.metric("CO₂ Impact", f"{food_co2:.1f} kg")
    
    # Total calculation
    total_weekly = transport_co2 + energy_co2 + food_co2
    
    # Display total using Streamlit components
    col1, col2 = st.columns(2)
    with col1:
        st.metric(
            label="Weekly Total",
            value=f"{total_weekly:.1f} kg CO₂",
            delta=f"Monthly: {total_weekly * 4.33:.1f} kg"
        )
    
    with col2:
        if total_weekly < 50:
            st.success("🌟 Excellent! Very low carbon footprint")
        elif total_weekly < 100:
            st.info("👍 Good job! Room for improvement")
        else:
            st.warning("⚠️ Consider reducing your carbon footprint")
    
    # Eco tips using Streamlit info boxes
    st.markdown("---")
    st.markdown("### 💡 Eco Tips of the Day")
    
    tips = [
        "🌡️ Lower your thermostat by 2°F to save 2,000 lbs of CO₂ per year",
        "💡 Switch to LED bulbs - they use 75% less energy than incandescent",
        "🚿 Take shorter showers to save both water and the energy to heat it",
        "🚲 Bike or walk for trips under 2 miles instead of driving",
        "📱 Unplug electronics when not in use - they draw power even when off"
    ]
    
    # Display tips using Streamlit info components
    for i, tip in enumerate(tips[:3]):
        if i == 0:
            st.info(tip)
        elif i == 1:
            st.success(tip)
        else:
            st.warning(tip)
if __name__ == "__main__":
    main()
