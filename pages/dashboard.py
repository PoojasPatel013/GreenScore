import streamlit as st
from auth import require_auth, check_authentication
from database import Database
from carbon_calculator import CarbonCalculator
from gamification import GamificationEngine
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import pandas as pd

@require_auth
def show_dashboard():
    """Display user dashboard with real data"""
    
    # Initialize components
    db = Database()
    calculator = CarbonCalculator()
    game_engine = GamificationEngine()
    
    user_data = st.session_state.user_data
    user_id = str(user_data['_id'])
    
    # Get real user statistics
    monthly_stats = db.get_user_monthly_stats(user_id)
    transactions = db.get_user_transactions(user_id, days=30, limit=10)
    goals = db.get_user_goals(user_id)
    
    # Calculate dynamic metrics
    current_score = game_engine.calculate_score(user_id, transactions)
    level_info = game_engine.get_user_level(current_score)
    
    # Update user stats in database
    updated_stats = {
        'total_score': current_score,
        'co2_saved_kg': max(0, (user_data.get('settings', {}).get('monthly_target_kg', 500) - monthly_stats['total_carbon'])),
        'trees_equivalent': int(monthly_stats['total_carbon'] / 22),  # ~22kg CO2 per tree per year
        'level': level_info['name']
    }
    db.update_user_stats(user_id, updated_stats)
    
    # Header with personalized greeting
    st.markdown(f"""
    <div style="
        background: linear-gradient(135deg, #1a1a1a 0%, #2a2a2a 100%);
        border: 2px solid #00d4ff;
        border-radius: 15px;
        padding: 2rem;
        margin-bottom: 2rem;
        text-align: center;
        box-shadow: 0 0 20px rgba(0, 212, 255, 0.3);
    ">
        <h1 style="color: #00d4ff; margin: 0;">
            Welcome back, {user_data.get('username', 'Eco Warrior')}! 🌍
        </h1>
        <p style="color: #b0b0b0; margin: 0.5rem 0;">
            Level: {level_info['name']} • Joined: {user_data.get('created_at', datetime.now()).strftime('%B %Y') if hasattr(user_data.get('created_at', datetime.now()), 'strftime') else 'Recently'}
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Real-time metrics
    col1, col2, col3, col4 = st.columns(4)
    
    monthly_target = user_data.get('settings', {}).get('monthly_target_kg', 500)
    
    with col1:
        st.metric(
            label="🔥 Monthly Carbon",
            value=f"{monthly_stats['total_carbon']:.1f} kg",
            delta=f"{monthly_stats['total_carbon'] - monthly_target:.1f} kg from target",
            delta_color="inverse"
        )
    
    with col2:
        st.metric(
            label="🌱 CO₂ Saved",
            value=f"{updated_stats['co2_saved_kg']:.1f} kg",
            delta=f"+{updated_stats['co2_saved_kg'] * 0.1:.1f} this week"
        )
    
    with col3:
        st.metric(
            label="⭐ EcoScore",
            value=f"{current_score:,.0f}",
            delta=f"Level: {level_info['name']}"
        )
    
    with col4:
        st.metric(
            label="🌳 Tree Equivalent",
            value=str(updated_stats['trees_equivalent']),
            delta=f"{len(transactions) if transactions else 0} activities logged"
        )
    
    st.markdown("---")
    
    # Main dashboard tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Analytics", 
        "💳 Transactions", 
        "🎯 Goals", 
        "🏆 Achievements"
    ])
    
    with tab1:
        show_analytics_tab(monthly_stats, transactions, user_id)
    
    with tab2:
        show_transactions_tab(db, calculator, user_id)
    
    with tab3:
        show_goals_tab(db, user_id, goals)
    
    with tab4:
        show_achievements_tab(user_data, current_score)

def show_analytics_tab(monthly_stats, transactions, user_id):
    """Show analytics with real user data"""
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Category breakdown pie chart
        if monthly_stats['categories']:
            categories = list(monthly_stats['categories'].keys())
            values = [monthly_stats['categories'][cat]['carbon'] for cat in categories]
            
            fig_pie = px.pie(
                values=values,
                names=categories,
                title="Carbon Footprint by Category",
                color_discrete_sequence=['#ff4757', '#ffa502', '#2ed573', '#00d4ff', '#9b59b6']
            )
            
            fig_pie.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color="#ffffff"),
                title_font=dict(color="#00d4ff")
            )
            
            st.plotly_chart(fig_pie, use_container_width=True)
        else:
            st.info("No transaction data available yet. Start logging your activities!")
    
    with col2:
        # Daily trend if we have data
        if transactions:
            # Group transactions by date
            df = pd.DataFrame(transactions)
            if not df.empty and 'date' in df.columns:
                df['date'] = pd.to_datetime(df['date'])
                daily_carbon = df.groupby(df['date'].dt.date)['carbon_kg'].sum().reset_index()
                
                fig_line = px.line(
                    daily_carbon,
                    x='date',
                    y='carbon_kg',
                    title="Daily Carbon Footprint Trend",
                    markers=True
                )
                
                fig_line.update_traces(line_color='#00d4ff', marker_color='#00d4ff')
                fig_line.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(color="#ffffff"),
                    title_font=dict(color="#00d4ff"),
                    xaxis=dict(gridcolor='#333'),
                    yaxis=dict(gridcolor='#333', title='CO₂ (kg)')
                )
                
                st.plotly_chart(fig_line, use_container_width=True)
        
        # Summary stats
        st.markdown("### 📈 Monthly Summary")
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total Transactions", monthly_stats['transaction_count'])
            st.metric("Daily Average", f"{monthly_stats['daily_average']:.1f} kg CO₂")
        
        with col2:
            st.metric("Total Spending", f"${monthly_stats['total_amount']:.2f}")
            efficiency = monthly_stats['total_carbon'] / monthly_stats['total_amount'] if monthly_stats['total_amount'] > 0 else 0
            st.metric("Carbon Efficiency", f"{efficiency:.2f} kg/$")

def show_transactions_tab(db, calculator, user_id):
    """Show transactions management"""
    
    col1, col2 = st.columns([2, 1])
    
    with col2:
        st.markdown("### ➕ Add New Transaction")
        
        with st.form("add_transaction"):
            description = st.text_input("Description", placeholder="e.g., Gas station fill-up")
            
            category = st.selectbox("Category", [
                "Transportation", "Energy", "Food", "Shopping", "Entertainment", "Other"
            ])
            
            subcategory = st.text_input("Subcategory (optional)", placeholder="e.g., gas, electricity")
            
            amount = st.number_input("Amount ($)", min_value=0.01, step=0.01)
            
            date = st.date_input("Date", value=datetime.now().date())
            
            if st.form_submit_button("💰 Add Transaction", use_container_width=True):
                if description and amount > 0:
                    # Calculate carbon footprint
                    carbon_kg = calculator.calculate_footprint(category, subcategory, amount)
                    
                    transaction_data = {
                        'user_id': user_id,
                        'description': description,
                        'category': category,
                        'subcategory': subcategory,
                        'amount': amount,
                        'carbon_kg': carbon_kg,
                        'date': datetime.combine(date, datetime.min.time())
                    }
                    
                    if db.add_transaction(transaction_data):
                        st.success(f"✅ Transaction added! Carbon impact: {carbon_kg:.2f} kg CO₂")
                        st.rerun()
                    else:
                        st.error("Failed to add transaction. Please try again.")
                else:
                    st.warning("Please fill in all required fields")
    
    with col1:
        st.markdown("### 📋 Recent Transactions")
        
        transactions = db.get_user_transactions(user_id, days=30, limit=20)
        
        if transactions:
            for transaction in transactions:
                # Determine impact level based on carbon footprint
                carbon = transaction.get('carbon_kg', 0)
                if carbon < 5:
                    impact_level, impact_color = "Low", "green"
                elif carbon < 15:
                    impact_level, impact_color = "Medium", "orange"
                else:
                    impact_level, impact_color = "High", "red"
                
                date_str = transaction.get('date', datetime.now()).strftime('%Y-%m-%d') if hasattr(transaction.get('date', datetime.now()), 'strftime') else str(transaction.get('date', ''))
                
                with st.container():
                    col1_inner, col2_inner, col3_inner = st.columns([3, 1, 1])
                    
                    with col1_inner:
                        st.markdown(f"**{transaction.get('description', 'Unknown')}**")
                        st.caption(f"📅 {date_str} • 📂 {transaction.get('category', 'Other')}")
                    
                    with col2_inner:
                        st.markdown(f"**${transaction.get('amount', 0):.2f}**")
                        if impact_level == "Low":
                            st.success(f"{impact_level} Impact")
                        elif impact_level == "Medium":
                            st.warning(f"{impact_level} Impact")
                        else:
                            st.error(f"{impact_level} Impact")
                    
                    with col3_inner:
                        st.markdown(f"**{carbon:.1f} kg CO₂**")
                    
                    st.divider()
        else:
            st.info("No transactions found. Add your first transaction to get started!")

def show_goals_tab(db, user_id, goals):
    """Show goals management"""
    
    col1, col2 = st.columns([2, 1])
    
    with col2:
        st.markdown("### 🎯 Create New Goal")
        
        with st.form("add_goal"):
            goal_type = st.selectbox("Goal Type", [
                "Reduce Monthly Footprint",
                "Use Public Transport",
                "Plant Trees",
                "Energy Efficiency",
                "Sustainable Shopping"
            ])
            
            target = st.number_input("Target Value", min_value=1, value=25)
            
            deadline = st.date_input("Deadline", value=datetime.now().date() + timedelta(days=30))
            
            if st.form_submit_button("🚀 Create Goal", use_container_width=True):
                goal_data = {
                    'title': f"{goal_type}: {target}",
                    'type': goal_type,
                    'target': target,
                    'current': 0,
                    'deadline': datetime.combine(deadline, datetime.min.time()),
                    'unit': '%' if 'Reduce' in goal_type else 'times' if 'Transport' in goal_type else 'trees'
                }
                
                if db.add_user_goal(user_id, goal_data):
                    st.success("🎉 Goal created successfully!")
                    st.rerun()
                else:
                    st.error("Failed to create goal. Please try again.")
    
    with col1:
        st.markdown("### 🏆 Active Goals")
        
        if goals:
            for goal in goals:
                progress = (goal.get('current', 0) / goal.get('target', 1)) * 100
                
                with st.container():
                    st.markdown(f"**{goal.get('title', 'Untitled Goal')}**")
                    
                    col1_inner, col2_inner = st.columns([3, 1])
                    
                    with col1_inner:
                        st.progress(min(progress / 100, 1.0))
                        deadline = goal.get('deadline', datetime.now())
                        if hasattr(deadline, 'strftime'):
                            deadline_str = deadline.strftime('%Y-%m-%d')
                        else:
                            deadline_str = str(deadline)
                        st.caption(f"Deadline: {deadline_str}")
                    
                    with col2_inner:
                        st.metric("Progress", f"{progress:.0f}%")
                        st.caption(f"{goal.get('current', 0)}/{goal.get('target', 0)} {goal.get('unit', '')}")
                    
                    if progress >= 100:
                        st.success("🎉 Goal Completed!")
                    
                    st.divider()
        else:
            st.info("No active goals. Create your first goal to get started!")

def show_achievements_tab(user_data, current_score):
    """Show achievements and badges"""
    
    user_achievements = user_data.get('stats', {}).get('achievements', [])
    
    st.markdown("### 🏅 Your Achievements")
    
    # Achievement definitions
    all_achievements = [
        {'name': 'First Steps', 'icon': '👶', 'description': 'Started your carbon tracking journey', 'unlock_score': 0},
        {'name': 'Week Warrior', 'icon': '⚡', 'description': 'Completed 7 days of tracking', 'unlock_score': 1200},
        {'name': 'Carbon Crusher', 'icon': '💪', 'description': 'Reduced emissions by 25%', 'unlock_score': 2500},
        {'name': 'Tree Hugger', 'icon': '🌳', 'description': 'Offset equivalent to 50 trees', 'unlock_score': 5000},
        {'name': 'Green Machine', 'icon': '🤖', 'description': 'Automated 10 eco-friendly habits', 'unlock_score': 7500},
        {'name': 'Planet Protector', 'icon': '🛡️', 'description': 'Saved 1000kg of CO₂', 'unlock_score': 10000},
    ]
    
    # Display achievements in grid
    cols = st.columns(3)
    for i, achievement in enumerate(all_achievements):
        with cols[i % 3]:
            earned = achievement['name'] in user_achievements
            can_unlock = current_score >= achievement['unlock_score'] and not earned
            
            if earned:
                st.success(f"{achievement['icon']} **{achievement['name']}**")
                st.caption(f"✅ {achievement['description']}")
            elif can_unlock:
                st.info(f"🔓 **{achievement['name']}** (Ready to unlock!)")
                st.caption(f"⭐ {achievement['description']}")
            else:
                st.info(f"🔒 **{achievement['name']}**")
                st.caption(f"🎯 Need {achievement['unlock_score']:,} points • {achievement['description']}")
    
    st.markdown("---")
    
    # Score progression
    st.markdown("### 📈 Score Progression")
    
    level_thresholds = [
        {'name': 'Eco Newbie', 'min_score': 0, 'color': '#888888'},
        {'name': 'Green Warrior', 'min_score': 1000, 'color': '#2ed573'},
        {'name': 'Carbon Crusher', 'min_score': 2500, 'color': '#00d4ff'},
        {'name': 'Sustainability Hero', 'min_score': 5000, 'color': '#9b59b6'},
        {'name': 'Planet Protector', 'min_score': 10000, 'color': '#f39c12'}
    ]
    
    current_level = None
    next_level = None
    
    for i, level in enumerate(level_thresholds):
        if current_score >= level['min_score']:
            current_level = level
            if i + 1 < len(level_thresholds):
                next_level = level_thresholds[i + 1]
    
    if current_level:
        st.markdown(f"**Current Level:** {current_level['name']} ({current_score:,} points)")
        
        if next_level:
            points_needed = next_level['min_score'] - current_score
            progress = (current_score - current_level['min_score']) / (next_level['min_score'] - current_level['min_score'])
            
            st.progress(progress)
            st.caption(f"Next Level: {next_level['name']} ({points_needed:,} points needed)")

def main():
    if not check_authentication():
        st.switch_page("pages/login.py")
    else:
        show_dashboard()

if __name__ == "__main__":
    main()
