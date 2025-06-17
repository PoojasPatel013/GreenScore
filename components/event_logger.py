import streamlit as st
from datetime import datetime
import pandas as pd
from backend import Database

class EventLogger:
    def __init__(self):
        self.db = Database()
        self.event_categories = {
            'transport': ['Walk', 'Bike', 'Public Transport', 'Car', 'Taxi'],
            'food': ['Home Cooked', 'Restaurant', 'Fast Food', 'Vegan', 'Meat'],
            'utilities': ['Electricity', 'Water', 'Gas', 'Recycling'],
            'daily_habits': ['Recycled', 'Composted', 'No Single-Use Plastic', 'Used Reusable Bag']
        }

    def log_event(self):
        """Streamlit component for logging daily events"""
        st.title("Daily Activity Logger 📝")
        
        # Date selector
        date = st.date_input("Date", value=datetime.now())
        
        # Event categories
        for category, options in self.event_categories.items():
            st.header(category.capitalize())
            
            # Create columns for multiple events
            cols = st.columns(len(options))
            for i, option in enumerate(options):
                with cols[i]:
                    if st.button(f"{option} ✅"):
                        self._save_event(date, category, option)
                        st.success(f"Logged {option} in {category}")
                        st.experimental_rerun()

    def _save_event(self, date, category, event):
        """Save event to database"""
        event_data = {
            'date': date,
            'category': category,
            'event': event,
            'timestamp': datetime.now()
        }
        self.db.add_transaction(None, event_data)

    def get_user_events(self, user_id):
        """Get user's events for today"""
        return self.db.get_user_transactions(user_id)

    def get_daily_summary(self, user_id):
        """Get summary of today's events"""
        events = self.get_user_events(user_id)
        summary = {}
        
        for event in events:
            category = event['category']
            if category not in summary:
                summary[category] = []
            summary[category].append(event['event'])
        
        return summary
