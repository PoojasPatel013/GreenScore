import streamlit as st
import plotly.express as px
import pandas as pd
from backend import CarbonCalculator, Gamification
from datetime import datetime

def dashboard():
    """Main dashboard component"""
    st.title("GreenScore Dashboard 🌱")
    
    # Initialize gamification
    gamification = Gamification()
    
    # Create columns for stats
    col1, col2, col3 = st.columns(3)
    
    # Stats cards
    with col1:
        st.markdown("""
            <div class="stat-card">
                <div class="stat-value">1200</div>
                <div class="stat-label">Carbon Score</div>
                <div class="stat-progress">
                    <div class="progress-bar">
                        <div class="progress" style="width: 70%"></div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
            <div class="stat-card">
                <div class="stat-value">50%</div>
                <div class="stat-label">Weekly Goal</div>
                <div class="stat-progress">
                    <div class="progress-bar">
                        <div class="progress" style="width: 50%"></div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
            <div class="stat-card">
                <div class="stat-value">3</div>
                <div class="stat-label">Trees Planted</div>
                <div class="stat-progress">
                    <div class="progress-bar">
                        <div class="progress" style="width: 90%"></div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    # Badges section
    st.markdown("""
        <div class="card">
            <h3>🏆 Your Badges</h3>
            <div class="badge-grid">
                <div class="badge-item">
                    <div class="badge-icon">🌱</div>
                    <div class="badge-name">Herbivore Hero</div>
                    <div class="badge-description">No meat consumption for a week</div>
                </div>
                <div class="badge-item">
                    <div class="badge-icon">🚴‍♂️</div>
                    <div class="badge-name">Bike Champion</div>
                    <div class="badge-description">Biked to work 5 times this week</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Challenges section
    st.markdown("""
        <div class="card">
            <h3>🎯 Active Challenges</h3>
            <div class="challenge-grid">
                <div class="challenge-item">
                    <div class="challenge-icon">🚴‍♂️</div>
                    <div class="challenge-name">Bike to Work</div>
                    <div class="challenge-progress">
                        <div class="progress-bar">
                            <div class="progress" style="width: 60%"></div>
                        </div>
                    </div>
                    <div class="challenge-description">Bike to work 5 times this week</div>
                </div>
                <div class="challenge-item">
                    <div class="challenge-icon">🥗</div>
                    <div class="challenge-name">Meatless Week</div>
                    <div class="challenge-progress">
                        <div class="progress-bar">
                            <div class="progress" style="width: 80%"></div>
                        </div>
                    </div>
                    <div class="challenge-description">No meat consumption for 7 days</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Carbon Footprint Chart
    st.markdown("""
        <div class="chart-container">
            <h3>Carbon Footprint by Category</h3>
        </div>
        """, unsafe_allow_html=True)
    
    # Generate sample data for the chart
    data = {
        'Category': ['Transport', 'Food', 'Utilities', 'Shopping', 'Other'],
        'Carbon Footprint': [150, 100, 50, 75, 25]
    }
    df = pd.DataFrame(data)
    
    fig = px.pie(df, values='Carbon Footprint', names='Category', 
                title='Carbon Footprint Distribution',
                color_discrete_sequence=px.colors.sequential.Greens)
    st.plotly_chart(fig)
    
    # Recent Transactions
    st.markdown("""
        <div class="transaction-list">
            <h3>Recent Events</h3>
        </div>
        """, unsafe_allow_html=True)
    
    # Generate sample transactions
    transactions = [
        {'date': datetime.now().strftime('%Y-%m-%d'), 
         'description': 'Biked to work', 
         'category': 'Transport',
         'icon': '🚴‍♂️'},
        {'date': datetime.now().strftime('%Y-%m-%d'), 
         'description': 'Home cooked vegan meal', 
         'category': 'Food',
         'icon': '🥗'},
        {'date': datetime.now().strftime('%Y-%m-%d'), 
         'description': 'Recycled waste', 
         'category': 'Utilities',
         'icon': '♻️'},
    ]
    
    for tx in transactions:
        st.markdown(f"""
            <div class="transaction-item">
                <div class="transaction-icon">{tx['icon']}</div>
                <div class="transaction-info">
                    <div class="transaction-date">{tx['date']}</div>
                    <div class="transaction-description">{tx['description']}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    # Recommendations
    st.markdown("""
        <div class="card">
            <h3>💡 Green Recommendations</h3>
            <ul>
                <li>Consider using public transport instead of ridesharing</li>
                <li>Switch to energy-efficient appliances</li>
                <li>Reduce meat consumption</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    # Carbon Footprint Chart
    st.markdown("""
        <div class="chart-container">
            <h3>Carbon Footprint by Category</h3>
        </div>
        """, unsafe_allow_html=True)
    
    # Generate sample data for the chart
    data = {
        'Category': ['Transport', 'Food', 'Utilities', 'Shopping', 'Other'],
        'Carbon Footprint': [150, 100, 50, 75, 25]
    }
    df = pd.DataFrame(data)
    
    fig = px.pie(df, values='Carbon Footprint', names='Category', 
                title='Carbon Footprint Distribution')
    st.plotly_chart(fig)
    
    # Progress Bar
    st.markdown("""
        <div class="progress-bar">
            <div class="progress" style="width: 70%"></div>
        </div>
        """, unsafe_allow_html=True)
    
    # Recent Transactions
    st.markdown("""
        <div class="transaction-list">
            <h3>Recent Transactions</h3>
        </div>
        """, unsafe_allow_html=True)
    
    # Generate sample transactions
    transactions = [
        {'date': '2024-06-17', 'description': 'Uber Ride', 'amount': 25.00, 'category': 'Transport'},
        {'date': '2024-06-16', 'description': 'Grocery Store', 'amount': 50.00, 'category': 'Food'},
        {'date': '2024-06-15', 'description': 'Electricity Bill', 'amount': 100.00, 'category': 'Utilities'},
    ]
    
    for tx in transactions:
        st.markdown(f"""
            <div class="transaction-item">
                <div>{tx['date']} - {tx['description']}</div>
                <div>$ {tx['amount']:.2f}</div>
            </div>
            """, unsafe_allow_html=True)
    
    # Recommendations
    st.markdown("""
        <div class="card">
            <h3>Green Recommendations</h3>
            <ul>
                <li>Consider using public transport instead of ridesharing</li>
                <li>Switch to energy-efficient appliances</li>
                <li>Reduce meat consumption</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
