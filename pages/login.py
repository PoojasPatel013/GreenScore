import streamlit as st
from auth import AuthManager
from database import Database

def show_login_page():
    st.markdown("""
    <div style="
        max-width: 400px;
        margin: 2rem auto;
        padding: 2rem;
        background: linear-gradient(135deg, #1a1a1a 0%, #2a2a2a 100%);
        border: 2px solid #00d4ff;
        border-radius: 15px;
        text-align: center;
        box-shadow: 0 0 20px rgba(0, 212, 255, 0.3);
    ">
        <h1 style="color: #00d4ff; margin-bottom: 1rem;">🌍 Welcome Back</h1>
        <p style="color: #b0b0b0; margin-bottom: 2rem;">Sign in to your CarbonTrace account</p>
    </div>
    """, unsafe_allow_html=True)
    
    db = Database()
    auth = AuthManager(db)
    
    # Create tabs for Login and Sign Up
    tab1, tab2 = st.tabs(["🔑 Login", "📝 Sign Up"])
    
    with tab1:
        show_login_form(auth)
    
    with tab2:
        show_signup_form(auth)

def show_login_form(auth):
    """Display login form"""
    with st.form("login_form"):
        st.markdown("### Login to Your Account")
        
        email = st.text_input("📧 Email", placeholder="Enter your email")
        password = st.text_input("🔒 Password", type="password", placeholder="Enter your password")
        
        col1, col2 = st.columns(2)
        with col1:
            login_btn = st.form_submit_button("🚀 Login", use_container_width=True)
        with col2:
            forgot_btn = st.form_submit_button("🤔 Forgot Password?", use_container_width=True)
        
        if login_btn:
            if email and password:
                success, message, data = auth.login_user(email, password)
                
                if success:
                    st.session_state.authenticated = True
                    st.session_state.user_token = data['token']
                    st.session_state.user_data = data['user']
                    st.success(message)
                    st.rerun()
                else:
                    st.error(message)
            else:
                st.warning("Please fill in all fields")
        
        if forgot_btn:
            st.info("Password reset functionality will be implemented soon!")

def show_signup_form(auth):
    """Display signup form"""
    with st.form("signup_form"):
        st.markdown("### Create New Account")
        
        col1, col2 = st.columns(2)
        with col1:
            username = st.text_input("👤 Username", placeholder="Choose a username")
        with col2:
            email = st.text_input("📧 Email", placeholder="Enter your email")
        
        password = st.text_input("🔒 Password", type="password", placeholder="Create a strong password")
        confirm_password = st.text_input("🔒 Confirm Password", type="password", placeholder="Confirm your password")
        
        # Terms and conditions
        agree_terms = st.checkbox("I agree to the Terms of Service and Privacy Policy")
        
        signup_btn = st.form_submit_button("🎉 Create Account", use_container_width=True)
        
        if signup_btn:
            if not all([username, email, password, confirm_password]):
                st.warning("Please fill in all fields")
            elif password != confirm_password:
                st.error("Passwords do not match")
            elif not agree_terms:
                st.warning("Please agree to the Terms of Service")
            else:
                success, message = auth.register_user(email, password, username)
                
                if success:
                    st.success(message)
                    st.info("You can now login with your credentials!")
                else:
                    st.error(message)

def main():
    # Check if user is already authenticated
    if st.session_state.get('authenticated', False):
        st.switch_page("app.py")
    else:
        show_login_page()

if __name__ == "__main__":
    main()
