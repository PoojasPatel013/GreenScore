import streamlit as st

def leaderboard():
    """Leaderboard component"""
    st.title("Leaderboard 🏆")
    
    # Generate sample leaderboard data
    users = [
        {'username': 'eco_warrior', 'score': 1500, 'trees_planted': 10},
        {'username': 'green_guru', 'score': 1350, 'trees_planted': 8},
        {'username': 'sustainable_life', 'score': 1200, 'trees_planted': 6},
        {'username': 'eco_friendly', 'score': 1100, 'trees_planted': 5},
        {'username': 'green_thinker', 'score': 1050, 'trees_planted': 4},
    ]
    
    st.markdown("""
        <div class="leaderboard">
            <h3>Top Users</h3>
        </div>
        """, unsafe_allow_html=True)
    
    for i, user in enumerate(users, 1):
        st.markdown(f"""
            <div class="leaderboard-item">
                <div style="display: flex; align-items: center; gap: 10px;">
                    <span style="font-size: 24px; font-weight: bold;">{i}.</span>
                    <span>{user['username']}</span>
                </div>
                <div style="display: flex; align-items: center; gap: 10px;">
                    <span style="color: {st.session_state.get('primary_color', '#4CAF50')};">{user['score']} pts</span>
                    <span>• {user['trees_planted']} 🌳</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    # Add some motivational text
    st.markdown("""
        <div class="card">
            <p style="text-align: center;">
                🌱 Compete with friends and reduce your carbon footprint! 🌍
            </p>
        </div>
        """, unsafe_allow_html=True)
