import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import requests
from database import Database
from carbon_calculator import CarbonCalculator
from ai_parser import TransactionParser
from gamification import GamificationEngine

# Initialize components
@st.cache_resource
def init_components():
    db = Database()
    calculator = CarbonCalculator()
    parser = TransactionParser()
    game_engine = GamificationEngine()
    return db, calculator, parser, game_engine

def main():
    st.set_page_config(
        page_title="GreenScore - Carbon Footprint Tracker",
        page_icon="🌱",
        layout="wide"
    )
    
    db, calculator, parser, game_engine = init_components()
    
    # Sidebar navigation
    st.sidebar.title("🌱 GreenScore")
    page = st.sidebar.selectbox(
        "Navigate",
        ["Dashboard", "Add Transaction", "Goals & Challenges", "Leaderboard", "Recommendations"]
    )
    
    # User session (simplified)
    if 'user_id' not in st.session_state:
        st.session_state.user_id = "user_123"  # In real app, handle authentication
    
    user_id = st.session_state.user_id
    
    if page == "Dashboard":
        show_dashboard(db, calculator, game_engine, user_id)
    elif page == "Add Transaction":
        show_add_transaction(db, parser, calculator, user_id)
    elif page == "Goals & Challenges":
        show_goals_challenges(db, game_engine, user_id)
    elif page == "Leaderboard":
        show_leaderboard(db, game_engine)
    elif page == "Recommendations":
        show_recommendations(db, calculator, user_id)

def show_dashboard(db, calculator, game_engine, user_id):
    st.title("🌱 Your Carbon Dashboard")
    
    # Get user data
    user_data = db.get_user_data(user_id)
    transactions = db.get_user_transactions(user_id, days=30)
    
    # Calculate metrics
    total_footprint = sum(t['carbon_kg'] for t in transactions)
    daily_avg = total_footprint / 30 if transactions else 0
    score = game_engine.calculate_score(user_id, transactions)
    
    # Display key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("🌍 Monthly Footprint", f"{total_footprint:.1f} kg CO₂", 
                 delta=f"{daily_avg:.1f} kg/day")
    
    with col2:
        st.metric("🏆 GreenScore", f"{score:.0f}", 
                 delta=f"+{game_engine.get_score_change(user_id)}")
    
    with col3:
        level = game_engine.get_user_level(score)
        st.metric("📈 Level", level['name'], 
                 delta=f"{score - level['min_score']}/{level['max_score'] - level['min_score']} XP")
    
    with col4:
        trees_planted = user_data.get('trees_planted', 0)
        st.metric("🌳 Trees Planted", trees_planted)
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        # Daily footprint chart
        if transactions:
            df = pd.DataFrame(transactions)
            df['date'] = pd.to_datetime(df['date'])
            daily_footprint = df.groupby(df['date'].dt.date)['carbon_kg'].sum().reset_index()
            
            fig = px.line(daily_footprint, x='date', y='carbon_kg',
                         title="Daily Carbon Footprint (Last 30 Days)",
                         labels={'carbon_kg': 'CO₂ (kg)', 'date': 'Date'})
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Category breakdown
        if transactions:
            category_footprint = df.groupby('category')['carbon_kg'].sum().reset_index()
            fig = px.pie(category_footprint, values='carbon_kg', names='category',
                        title="Carbon Footprint by Category")
            st.plotly_chart(fig, use_container_width=True)
    
    # Recent transactions
    st.subheader("Recent Transactions")
    if transactions:
        recent_df = pd.DataFrame(transactions[:10])
        st.dataframe(recent_df[['date', 'description', 'category', 'amount', 'carbon_kg']], 
                    use_container_width=True)

def show_add_transaction(db, parser, calculator, user_id):
    st.title("💳 Add Transaction")
    
    tab1, tab2 = st.tabs(["Manual Entry", "Bank Statement Upload"])
    
    with tab1:
        with st.form("manual_transaction"):
            col1, col2 = st.columns(2)
            
            with col1:
                description = st.text_input("Description", placeholder="e.g., Grocery shopping at Whole Foods")
                amount = st.number_input("Amount ($)", min_value=0.0, step=0.01)
                category = st.selectbox("Category", 
                    ["Food", "Transportation", "Energy", "Shopping", "Entertainment", "Other"])
            
            with col2:
                date = st.date_input("Date", datetime.now())
                subcategory = st.text_input("Subcategory (optional)", 
                    placeholder="e.g., Organic groceries")
            
            submitted = st.form_submit_button("Add Transaction")
            
            if submitted and description and amount > 0:
                # Calculate carbon footprint
                carbon_kg = calculator.calculate_footprint(category, subcategory, amount)
                
                # Save transaction
                transaction = {
                    'user_id': user_id,
                    'date': date.isoformat(),
                    'description': description,
                    'amount': amount,
                    'category': category,
                    'subcategory': subcategory,
                    'carbon_kg': carbon_kg
                }
                
                db.add_transaction(transaction)
                st.success(f"Transaction added! Carbon footprint: {carbon_kg:.2f} kg CO₂")
                st.rerun()
    
    with tab2:
        uploaded_file = st.file_uploader("Upload Bank Statement (CSV)", type=['csv'])
        
        if uploaded_file:
            df = pd.read_csv(uploaded_file)
            st.write("Preview of uploaded data:")
            st.dataframe(df.head())
            
            if st.button("Process Transactions"):
                with st.spinner("Processing transactions with AI..."):
                    processed_transactions = parser.parse_transactions(df, user_id)
                    
                    for transaction in processed_transactions:
                        db.add_transaction(transaction)
                    
                    st.success(f"Processed {len(processed_transactions)} transactions!")
                    st.rerun()

def show_goals_challenges(db, game_engine, user_id):
    st.title("🎯 Goals & Challenges")
    
    # Current goals
    goals = db.get_user_goals(user_id)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Your Goals")
        
        if goals:
            for goal in goals:
                progress = (goal['current'] / goal['target']) * 100
                st.write(f"**{goal['title']}**")
                st.progress(min(progress / 100, 1.0))
                st.write(f"{goal['current']:.1f} / {goal['target']:.1f} {goal['unit']}")
                st.write(f"Reward: {goal['reward']}")
                st.write("---")
        else:
            st.info("No active goals. Create one below!")
        
        # Create new goal
        with st.expander("Create New Goal"):
            goal_type = st.selectbox("Goal Type", 
                ["Reduce Monthly Footprint", "Use Public Transport", "Plant Trees"])
            target = st.number_input("Target", min_value=1.0, step=1.0)
            
            if st.button("Create Goal"):
                new_goal = game_engine.create_goal(user_id, goal_type, target)
                db.add_user_goal(new_goal)
                st.success("Goal created!")
                st.rerun()
    
    with col2:
        st.subheader("Weekly Challenges")
        
        challenges = game_engine.get_weekly_challenges()
        
        for challenge in challenges:
            with st.container():
                st.write(f"**{challenge['title']}**")
                st.write(challenge['description'])
                st.write(f"Reward: {challenge['reward']} points")
                
                if st.button(f"Join Challenge", key=challenge['id']):
                    game_engine.join_challenge(user_id, challenge['id'])
                    st.success("Joined challenge!")
                
                st.write("---")

def show_leaderboard(db, game_engine):
    st.title("🏆 Leaderboard")
    
    tab1, tab2 = st.tabs(["Global Leaderboard", "Friends"])
    
    with tab1:
        leaderboard = game_engine.get_global_leaderboard()
        
        for i, user in enumerate(leaderboard[:10]):
            col1, col2, col3, col4 = st.columns([1, 3, 2, 2])
            
            with col1:
                if i == 0:
                    st.write("🥇")
                elif i == 1:
                    st.write("🥈")
                elif i == 2:
                    st.write("🥉")
                else:
                    st.write(f"{i+1}")
            
            with col2:
                st.write(user['username'])
            
            with col3:
                st.write(f"{user['score']:.0f} points")
            
            with col4:
                st.write(f"{user['footprint_reduction']:.1f}% reduction")
    
    with tab2:
        st.info("Connect with friends to see their progress!")

def show_recommendations(db, calculator, user_id):
    st.title("💡 Green Recommendations")
    
    # Get user's transaction patterns
    transactions = db.get_user_transactions(user_id, days=30)
    recommendations = calculator.get_recommendations(transactions)
    
    for rec in recommendations:
        with st.container():
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.write(f"**{rec['title']}**")
                st.write(rec['description'])
                st.write(f"💰 Potential savings: ${rec['cost_savings']:.2f}/month")
                st.write(f"🌍 Carbon reduction: {rec['carbon_savings']:.1f} kg CO₂/month")
            
            with col2:
                if st.button("Learn More", key=rec['id']):
                    st.info(rec['details'])
            
            st.write("---")

if __name__ == "__main__":
    main()
