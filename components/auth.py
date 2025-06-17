import streamlit as st
from backend import AuthService
from datetime import datetime

def login_page():
    st.title("Login to GreenScore 🌱")
    
    with st.form("login_form"):
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Login")
        
        if submit:
            auth_service = AuthService(db)
            user = auth_service.login_user(email, password)
            if user:
                st.success("Logged in successfully!")
                st.experimental_rerun()
            else:
                st.error("Invalid email or password")
    
    st.markdown("---")
    st.write("Don't have an account? [Sign up here](/signup)")

def signup_page():
    st.title("Sign Up for GreenScore 🌱")
    
    with st.form("signup_form"):
        email = st.text_input("Email")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        confirm_password = st.text_input("Confirm Password", type="password")
        submit = st.form_submit_button("Sign Up")
        
        if submit:
            if password != confirm_password:
                st.error("Passwords do not match!")
                return
            
            auth_service = AuthService(db)
            user_id = auth_service.register_user(email, password, username)
            if user_id:
                st.success("Account created successfully!")
                st.experimental_rerun()
            else:
                st.error("Email already exists!")
    
    st.markdown("---")
    st.write("Already have an account? [Login here](/login)")

def profile_page(user_id):
    st.title("My Profile 📝")
    
    auth_service = AuthService(db)
    
    # Get user data
    user = db.get_user_by_id(user_id)
    profile = db.get_profile(user_id)
    
    # Display user info
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Username", user['username'])
        st.metric("Email", user['email'])
    with col2:
        st.metric("Level", user.get('level', 1))
        st.metric("Points", user.get('points', 0))
    
    # Profile picture
    if profile and profile.get('avatar_url'):
        st.image(profile['avatar_url'], width=200)
    
    # Update profile form
    with st.form("profile_form"):
        full_name = st.text_input("Full Name", profile.get('full_name', '') if profile else '')
        bio = st.text_area("Bio", profile.get('bio', '') if profile else '', height=100)
        location = st.text_input("Location", profile.get('location', '') if profile else '')
        submit = st.form_submit_button("Update Profile")
        
        if submit:
            auth_service.update_profile(user_id, full_name, bio, location)
            st.success("Profile updated successfully!")
            st.experimental_rerun()

def account_dashboard(user_id):
    st.title("Account Dashboard 📊")
    
    # User stats
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Points", db.get_user_by_id(user_id).get('points', 0))
    with col2:
        st.metric("Level", db.get_user_by_id(user_id).get('level', 1))
    with col3:
        st.metric("Carbon Saved", f"{db.get_user_by_id(user_id).get('carbon_saved', 0):.2f} kg")
    
    # Recent activity
    st.header("Recent Activity")
    events = db.get_user_events(user_id)
    for event in events[:5]:
        st.write(f"**{event['event_type']}**: {event['description']} - {event['impact']:.2f} kg CO₂")
    
    # Achievements
    st.header("Achievements")
    achievements = db.get_user_achievements(user_id)
    for achievement in achievements:
        st.write(f"**{achievement['name']}**: {achievement['description']}")
    
    # Change password
    st.header("Change Password")
    with st.form("change_password_form"):
        current_password = st.text_input("Current Password", type="password")
        new_password = st.text_input("New Password", type="password")
        confirm_new_password = st.text_input("Confirm New Password", type="password")
        submit = st.form_submit_button("Change Password")
        
        if submit:
            if new_password != confirm_new_password:
                st.error("New passwords do not match!")
                return
            
            auth_service = AuthService(db)
            user = auth_service.login_user(user['email'], current_password)
            if user:
                auth_service.update_user(user_id, {'password_hash': generate_password_hash(new_password)})
                st.success("Password changed successfully!")
            else:
                st.error("Invalid current password!")
