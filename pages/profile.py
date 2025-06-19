import streamlit as st
from auth import require_auth, check_authentication
from database import Database
from datetime import datetime

@require_auth
def show_profile_page():
    """Display user profile management page"""
    
    db = Database()
    user_data = st.session_state.user_data
    user_id = str(user_data['_id'])
    
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
        <h1 style="color: #00d4ff; margin: 0;">👤 Profile Settings</h1>
        <p style="color: #b0b0b0; margin: 0.5rem 0;">
            Manage your account and preferences
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["👤 Profile", "⚙️ Settings", "📊 Statistics"])
    
    with tab1:
        show_profile_tab(db, user_data, user_id)
    
    with tab2:
        show_settings_tab(db, user_data, user_id)
    
    with tab3:
        show_stats_tab(db, user_data, user_id)

def show_profile_tab(db, user_data, user_id):
    """Show profile information and edit form"""
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown("### 🖼️ Profile Picture")
        
        # Avatar placeholder
        avatar_url = user_data.get('profile', {}).get('avatar_url', '')
        if avatar_url:
            st.image(avatar_url, width=200)
        else:
            st.markdown(f"""
            <div style="
                width: 200px;
                height: 200px;
                border-radius: 50%;
                background: linear-gradient(135deg, #00d4ff, #0099cc);
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 4rem;
                color: white;
                margin: 0 auto;
            ">
                {user_data.get('username', 'U')[0].upper()}
            </div>
            """, unsafe_allow_html=True)
        
        st.info("Avatar upload functionality coming soon!")
    
    with col2:
        st.markdown("### ✏️ Edit Profile")
        
        profile = user_data.get('profile', {})
        
        with st.form("profile_form"):
            first_name = st.text_input("First Name", value=profile.get('first_name', ''))
            last_name = st.text_input("Last Name", value=profile.get('last_name', ''))
            
            bio = st.text_area("Bio", value=profile.get('bio', ''), placeholder="Tell us about yourself...")
            location = st.text_input("Location", value=profile.get('location', ''), placeholder="City, Country")
            
            # Preferences
            st.markdown("#### Preferences")
            
            col1, col2 = st.columns(2)
            
            with col1:
                units = st.selectbox("Units", ["metric", "imperial"], 
                                   index=0 if profile.get('preferences', {}).get('units', 'metric') == 'metric' else 1)
            
            with col2:
                public_profile = st.checkbox("Public Profile", 
                                           value=profile.get('preferences', {}).get('public_profile', False))
            
            notifications = st.checkbox("Email Notifications", 
                                      value=profile.get('preferences', {}).get('notifications', True))
            
            if st.form_submit_button("💾 Save Changes", use_container_width=True):
                updated_profile = {
                    'first_name': first_name,
                    'last_name': last_name,
                    'bio': bio,
                    'location': location,
                    'avatar_url': profile.get('avatar_url', ''),
                    'preferences': {
                        'units': units,
                        'notifications': notifications,
                        'public_profile': public_profile
                    }
                }
                
                if db.update_user_profile(user_id, updated_profile):
                    st.success("✅ Profile updated successfully!")
                    # Update session state
                    st.session_state.user_data['profile'] = updated_profile
                    st.rerun()
                else:
                    st.error("❌ Failed to update profile. Please try again.")

def show_settings_tab(db, user_data, user_id):
    """Show account settings"""
    
    st.markdown("### ⚙️ Account Settings")
    
    # Current settings
    settings = user_data.get('settings', {})
    
    with st.form("settings_form"):
        st.markdown("#### Carbon Tracking Settings")
        
        monthly_target = st.number_input(
            "Monthly Carbon Target (kg CO₂)", 
            min_value=50, 
            max_value=2000, 
            value=settings.get('monthly_target_kg', 500),
            step=50,
            help="Set your monthly carbon footprint reduction goal"
        )
        
        currency = st.selectbox(
            "Currency", 
            ["USD", "EUR", "GBP", "CAD", "AUD"],
            index=["USD", "EUR", "GBP", "CAD", "AUD"].index(settings.get('currency', 'USD'))
        )
        
        timezone = st.selectbox(
            "Timezone",
            ["UTC", "EST", "PST", "CET", "GMT"],
            index=["UTC", "EST", "PST", "CET", "GMT"].index(settings.get('timezone', 'UTC'))
        )
        
        st.markdown("#### Privacy Settings")
        
        data_sharing = st.checkbox(
            "Share anonymous data for research",
            value=settings.get('data_sharing', False),
            help="Help improve carbon tracking algorithms by sharing anonymized data"
        )
        
        marketing_emails = st.checkbox(
            "Receive eco-tips and updates",
            value=settings.get('marketing_emails', True)
        )
        
        if st.form_submit_button("💾 Save Settings", use_container_width=True):
            updated_settings = {
                'monthly_target_kg': monthly_target,
                'currency': currency,
                'timezone': timezone,
                'data_sharing': data_sharing,
                'marketing_emails': marketing_emails
            }
            
            # Update in database (you'd need to add this method to Database class)
            try:
                if hasattr(db, 'use_json_fallback'):
                    db.json_data['users'][user_id]['settings'] = updated_settings
                    db._save_json_data()
                else:
                    db.users.update_one(
                        {'_id': db.ObjectId(user_id)},
                        {'$set': {'settings': updated_settings}}
                    )
                
                st.success("✅ Settings updated successfully!")
                st.session_state.user_data['settings'] = updated_settings
                st.rerun()
                
            except Exception as e:
                st.error(f"❌ Failed to update settings: {str(e)}")
    
    st.markdown("---")
    
    # Danger zone
    st.markdown("### 🚨 Danger Zone")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🔄 Reset All Data", type="secondary", use_container_width=True):
            st.warning("This will reset all your transactions and achievements. This action cannot be undone!")
    
    with col2:
        if st.button("🗑️ Delete Account", type="secondary", use_container_width=True):
            st.error("Account deletion functionality will be implemented with proper safeguards.")

def show_stats_tab(db, user_data, user_id):
    """Show detailed user statistics"""
    
    st.markdown("### 📊 Your Statistics")
    
    # Get comprehensive stats
    monthly_stats = db.get_user_monthly_stats(user_id)
    all_transactions = db.get_user_transactions(user_id, days=365, limit=1000)
    
    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Total Transactions",
            len(all_transactions),
            f"+{len(db.get_user_transactions(user_id, days=7))} this week"
        )
    
    with col2:
        total_carbon = sum(t.get('carbon_kg', 0) for t in all_transactions)
        st.metric(
            "Total Carbon Tracked",
            f"{total_carbon:.1f} kg",
            f"{monthly_stats['total_carbon']:.1f} kg this month"
        )
    
    with col3:
        total_amount = sum(t.get('amount', 0) for t in all_transactions)
        st.metric(
            "Total Amount Tracked",
            f"${total_amount:.2f}",
            f"${monthly_stats['total_amount']:.2f} this month"
        )
    
    with col4:
        join_date = user_data.get('created_at', datetime.now())
        if hasattr(join_date, 'date'):
            days_active = (datetime.now().date() - join_date.date()).days
        else:
            days_active = 0
        
        st.metric(
            "Days Active",
            days_active,
            f"Since {join_date.strftime('%B %Y') if hasattr(join_date, 'strftime') else 'Recently'}"
        )
    
    st.markdown("---")
    
    # Category breakdown
    if monthly_stats['categories']:
        st.markdown("### 📈 Category Breakdown (This Month)")
        
        for category, data in monthly_stats['categories'].items():
            col1, col2, col3 = st.columns([2, 1, 1])
            
            with col1:
                st.markdown(f"**{category}**")
            
            with col2:
                st.metric("Transactions", data['count'])
            
            with col3:
                st.metric("Carbon", f"{data['carbon']:.1f} kg")
    
    st.markdown("---")
    
    # Account information
    st.markdown("### ℹ️ Account Information")
    
    info_data = {
        "Username": user_data.get('username', 'N/A'),
        "Email": user_data.get('email', 'N/A'),
        "Account Created": user_data.get('created_at', datetime.now()).strftime('%Y-%m-%d %H:%M') if hasattr(user_data.get('created_at', datetime.now()), 'strftime') else 'Recently',
        "Last Login": user_data.get('last_login', 'N/A'),
        "Current Level": user_data.get('stats', {}).get('level', 'Eco Newbie'),
        "Total Score": f"{user_data.get('stats', {}).get('total_score', 1000):,} points"
    }
    
    for key, value in info_data.items():
        col1, col2 = st.columns([1, 2])
        with col1:
            st.markdown(f"**{key}:**")
        with col2:
            st.markdown(str(value))

def main():
    if not check_authentication():
        st.switch_page("pages/login.py")
    else:
        show_profile_page()

if __name__ == "__main__":
    main()
