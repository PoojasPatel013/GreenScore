# 🌍 CarbonTrace - Complete Setup Guide

## 🚀 **Quick Start (Recommended)**

### **Option 1: One-Click Setup**
```bash
# Download and run the complete setup
python run_setup.py


# GreenScore - Personal Carbon Footprint Tracker

An AI-powered application that helps users track and reduce their carbon footprint through gamification and rewards.

## Features

- AI-powered transaction analysis and categorization
- Real-time carbon footprint tracking
- Personalized eco-friendly recommendations
- Weekly goals and challenges
- Social leaderboards
- Eco-rewards system

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up environment variables:
Create a `.env` file with your API keys:
```
PLAID_CLIENT_ID=your_plaid_id
PLAID_SECRET=your_plaid_secret
CARBON_INTERFACE_API_KEY=your_carbon_api_key
```

3. Run the application:
```bash
python app.py
```

## Tech Stack

- Frontend: Streamlit
- Backend: Flask
- AI/ML: Python (pandas, scikit-learn, spaCy, BERT)
- Database: PostgreSQL
- APIs: Plaid, CarbonInterface
