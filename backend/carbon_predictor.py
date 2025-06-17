import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
import joblib
import os

class CarbonPredictor:
    def __init__(self):
        self.model = None
        self.scaler = None
        self._initialize_model()

    def _initialize_model(self):
        """Initialize or load the prediction model"""
        model_path = "models/carbon_prediction_model.joblib"
        scaler_path = "models/scaler.joblib"

        # Create models directory if it doesn't exist
        os.makedirs("models", exist_ok=True)

        if os.path.exists(model_path) and os.path.exists(scaler_path):
            self.model = joblib.load(model_path)
            self.scaler = joblib.load(scaler_path)
        else:
            self._train_model()

    def _train_model(self):
        """Train a new model"""
        # Sample training data (in real app, this would come from historical data)
        data = {
            'transport_distance': [10, 20, 30, 40, 50],
            'food_type': [1, 2, 3, 1, 2],  # 1=plant-based, 2=mixed, 3=meat-heavy
            'energy_usage': [100, 150, 200, 250, 300],
            'shopping_frequency': [2, 3, 4, 5, 6],
            'carbon_footprint': [2.5, 4.0, 6.0, 7.5, 9.0]  # kg CO2
        }
        df = pd.DataFrame(data)

        # Features and target
        X = df.drop('carbon_footprint', axis=1)
        y = df['carbon_footprint']

        # Scale features
        self.scaler = StandardScaler()
        X_scaled = self.scaler.fit_transform(X)

        # Train model
        self.model = RandomForestRegressor(n_estimators=100, random_state=42)
        self.model.fit(X_scaled, y)

        # Save model and scaler
        joblib.dump(self.model, "models/carbon_prediction_model.joblib")
        joblib.dump(self.scaler, "models/scaler.joblib")

    def predict(self, user_data):
        """
        Predict carbon footprint based on user data
        
        Args:
            user_data (dict): User input data containing:
                - transport_distance: Distance traveled in km
                - food_type: Type of diet (1=plant-based, 2=mixed, 3=meat-heavy)
                - energy_usage: Monthly energy usage in kWh
                - shopping_frequency: Number of shopping trips per week
        
        Returns:
            float: Predicted carbon footprint in kg CO2
        """
        # Convert input to DataFrame
        input_df = pd.DataFrame([user_data])
        
        # Scale input data
        input_scaled = self.scaler.transform(input_df)
        
        # Make prediction
        prediction = self.model.predict(input_scaled)[0]
        return round(prediction, 2)

    def update_model(self, new_data):
        """
        Update the model with new training data
        
        Args:
            new_data (dict): New training data point containing:
                - features: Dictionary of input features
                - carbon_footprint: Actual carbon footprint
        """
        # Convert to DataFrame
        df = pd.DataFrame([new_data])
        
        # Extract features and target
        X = df.drop('carbon_footprint', axis=1)
        y = df['carbon_footprint']
        
        # Scale features
        X_scaled = self.scaler.transform(X)
        
        # Partial fit the model
        self.model.fit(X_scaled, y)
        
        # Save updated model
        joblib.dump(self.model, "models/carbon_prediction_model.joblib")
