import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.ensemble import RandomForestClassifier, GradientBoostingRegressor
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, mean_squared_error, r2_score
import joblib
import matplotlib.pyplot as plt
import seaborn as sns
from transformers import AutoTokenizer, AutoModelForSequenceClassification, Trainer, TrainingArguments
import torch
from torch.utils.data import Dataset
import warnings
warnings.filterwarnings('ignore')

class TransactionDataset(Dataset):
    """Custom dataset for BERT fine-tuning"""
    
    def __init__(self, texts, labels, tokenizer, max_length=128):
        self.texts = texts
        self.labels = labels
        self.tokenizer = tokenizer
        self.max_length = max_length
    
    def __len__(self):
        return len(self.texts)
    
    def __getitem__(self, idx):
        text = str(self.texts[idx])
        encoding = self.tokenizer(
            text,
            truncation=True,
            padding='max_length',
            max_length=self.max_length,
            return_tensors='pt'
        )
        
        return {
            'input_ids': encoding['input_ids'].flatten(),
            'attention_mask': encoding['attention_mask'].flatten(),
            'labels': torch.tensor(self.labels[idx], dtype=torch.long)
        }

class TransactionClassifierTrainer:
    def __init__(self):
        """Initialize transaction classifier trainer"""
        
        self.models = {}
        self.vectorizers = {}
        self.encoders = {}
        self.scalers = {}
        
        # Model configurations
        self.model_configs = {
            'random_forest': {
                'n_estimators': [100, 200, 300],
                'max_depth': [10, 20, None],
                'min_samples_split': [2, 5, 10]
            },
            'logistic_regression': {
                'C': [0.1, 1, 10],
                'max_iter': [1000]
            }
        }
    
    def load_and_prepare_data(self, data_file: str) -> tuple:
        """Load and prepare training data"""
        
        print(f"📂 Loading data from {data_file}...")
        df = pd.read_csv(data_file)
        
        print(f"📊 Dataset shape: {df.shape}")
        print(f"📋 Categories: {df['category'].value_counts()}")
        
        # Prepare features
        X_text = df['description'].values
        X_numeric = df[['amount', 'description_length', 'description_word_count', 
                       'has_numbers', 'has_special_chars', 'day_of_week', 'month']].values
        
        # Prepare labels
        y_category = df['category'].values
        y_subcategory = df['subcategory'].values
        y_carbon_intensity = df['carbon_intensity'].values
        
        return X_text, X_numeric, y_category, y_subcategory, y_carbon_intensity, df
    
    def create_text_features(self, X_text_train, X_text_test):
        """Create TF-IDF features from text"""
        
        print("🔤 Creating TF-IDF features...")
        
        # Create TF-IDF vectorizer
        vectorizer = TfidfVectorizer(
            max_features=5000,
            stop_words='english',
            ngram_range=(1, 2),
            lowercase=True
        )
        
        # Fit and transform
        X_text_train_tfidf = vectorizer.fit_transform(X_text_train)
        X_text_test_tfidf = vectorizer.transform(X_text_test)
        
        self.vectorizers['tfidf'] = vectorizer
        
        return X_text_train_tfidf, X_text_test_tfidf
    
    def train_category_classifier(self, X_train, y_train, X_test, y_test):
        """Train category classification models"""
        
        print("🏷️ Training category classifiers...")
        
        # Encode labels
        label_encoder = LabelEncoder()
        y_train_encoded = label_encoder.fit_transform(y_train)
        y_test_encoded = label_encoder.transform(y_test)
        
        self.encoders['category'] = label_encoder
        
        results = {}
        
        # Random Forest
        print("  Training Random Forest...")
        rf_grid = GridSearchCV(
            RandomForestClassifier(random_state=42),
            self.model_configs['random_forest'],
            cv=5,
            scoring='accuracy',
            n_jobs=-1
        )
        
        rf_grid.fit(X_train, y_train_encoded)
        rf_best = rf_grid.best_estimator_
        
        # Predictions
        rf_pred = rf_best.predict(X_test)
        rf_accuracy = (rf_pred == y_test_encoded).mean()
        
        results['random_forest'] = {
            'model': rf_best,
            'accuracy': rf_accuracy,
            'predictions': rf_pred,
            'best_params': rf_grid.best_params_
        }
        
        print(f"    Random Forest Accuracy: {rf_accuracy:.4f}")
        
        # Logistic Regression
        print("  Training Logistic Regression...")
        lr_grid = GridSearchCV(
            LogisticRegression(random_state=42),
            self.model_configs['logistic_regression'],
            cv=5,
            scoring='accuracy',
            n_jobs=-1
        )
        
        lr_grid.fit(X_train, y_train_encoded)
        lr_best = lr_grid.best_estimator_
        
        lr_pred = lr_best.predict(X_test)
        lr_accuracy = (lr_pred == y_test_encoded).mean()
        
        results['logistic_regression'] = {
            'model': lr_best,
            'accuracy': lr_accuracy,
            'predictions': lr_pred,
            'best_params': lr_grid.best_params_
        }
        
        print(f"    Logistic Regression Accuracy: {lr_accuracy:.4f}")
        
        # Select best model
        best_model_name = max(results.keys(), key=lambda k: results[k]['accuracy'])
        best_model = results[best_model_name]
        
        print(f"  🏆 Best model: {best_model_name} (Accuracy: {best_model['accuracy']:.4f})")
        
        self.models['category_classifier'] = best_model['model']
        
        # Generate classification report
        y_pred_labels = label_encoder.inverse_transform(best_model['predictions'])
        y_test_labels = label_encoder.inverse_transform(y_test_encoded)
        
        print("\n📊 Classification Report:")
        print(classification_report(y_test_labels, y_pred_labels))
        
        return results
    
    def train_bert_classifier(self, X_text, y_category, test_size=0.2):
        """Train BERT-based classifier"""
        
        print("🤖 Training BERT classifier...")
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X_text, y_category, test_size=test_size, random_state=42, stratify=y_category
        )
        
        # Encode labels
        label_encoder = LabelEncoder()
        y_train_encoded = label_encoder.fit_transform(y_train)
        y_test_encoded = label_encoder.transform(y_test)
        
        # Initialize tokenizer and model
        model_name = "bert-base-uncased"
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        model = AutoModelForSequenceClassification.from_pretrained(
            model_name, 
            num_labels=len(label_encoder.classes_)
        )
        
        # Create datasets
        train_dataset = TransactionDataset(X_train, y_train_encoded, tokenizer)
        test_dataset = TransactionDataset(X_test, y_test_encoded, tokenizer)
        
        # Training arguments
        training_args = TrainingArguments(
            output_dir='./bert_model',
            num_train_epochs=3,
            per_device_train_batch_size=16,
            per_device_eval_batch_size=64,
            warmup_steps=500,
            weight_decay=0.01,
            logging_dir='./logs',
            evaluation_strategy="epoch",
            save_strategy="epoch",
            load_best_model_at_end=True,
        )
        
        # Initialize trainer
        trainer = Trainer(
            model=model,
            args=training_args,
            train_dataset=train_dataset,
            eval_dataset=test_dataset,
        )
        
        # Train model
        print("  Training BERT model (this may take a while)...")
        trainer.train()
        
        # Save model
        model.save_pretrained('./models/bert_transaction_classifier')
        tokenizer.save_pretrained('./models/bert_transaction_classifier')
        
        # Evaluate
        eval_results = trainer.evaluate()
        print(f"  BERT Evaluation Results: {eval_results}")
        
        self.models['bert_classifier'] = model
        self.encoders['bert_category'] = label_encoder
        
        return eval_results
    
    def save_models(self, output_dir: str = "models"):
        """Save trained models"""
        
        from pathlib import Path
        Path(output_dir).mkdir(exist_ok=True)
        
        # Save scikit-learn models
        for name, model in self.models.items():
            if hasattr(model, 'predict'):  # sklearn models
                joblib.dump(model, f"{output_dir}/{name}.joblib")
                print(f"💾 Saved {name}")
        
        # Save vectorizers and encoders
        for name, vectorizer in self.vectorizers.items():
            joblib.dump(vectorizer, f"{output_dir}/vectorizer_{name}.joblib")
            print(f"💾 Saved vectorizer_{name}")
        
        for name, encoder in self.encoders.items():
            joblib.dump(encoder, f"{output_dir}/encoder_{name}.joblib")
            print(f"💾 Saved encoder_{name}")
        
        print(f"✅ All models saved to {output_dir}/")

class CarbonEstimatorTrainer:
    def __init__(self):
        """Initialize carbon footprint estimator trainer"""
        
        self.models = {}
        self.scalers = {}
        self.encoders = {}
    
    def load_and_prepare_data(self, data_file: str) -> tuple:
        """Load and prepare carbon estimation data"""
        
        print(f"📂 Loading carbon data from {data_file}...")
        df = pd.read_csv(data_file)
        
        print(f"📊 Dataset shape: {df.shape}")
        
        # Prepare features
        features = ['activity_amount', 'true_emission_factor', 'uncertainty']
        
        # Encode categorical features
        category_encoder = LabelEncoder()
        subcategory_encoder = LabelEncoder()
        unit_encoder = LabelEncoder()
        
        df['category_encoded'] = category_encoder.fit_transform(df['category'])
        df['subcategory_encoded'] = subcategory_encoder.fit_transform(df['subcategory'])
        df['unit_encoded'] = unit_encoder.fit_transform(df['activity_unit'])
        
        # Store encoders
        self.encoders['category'] = category_encoder
        self.encoders['subcategory'] = subcategory_encoder
        self.encoders['unit'] = unit_encoder
        
        # Features
        X = df[features + ['category_encoded', 'subcategory_encoded', 'unit_encoded']].values
        y = df['calculated_carbon_kg'].values
        
        return X, y, df
    
    def train_carbon_estimator(self, X, y):
        """Train carbon footprint estimation models"""
        
        print("🌱 Training carbon estimator...")
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        # Scale features
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        self.scalers['carbon_features'] = scaler
        
        # Train Gradient Boosting Regressor
        print("  Training Gradient Boosting Regressor...")
        
        gbr_params = {
            'n_estimators': [100, 200],
            'max_depth': [5, 10],
            'learning_rate': [0.1, 0.01]
        }
        
        gbr_grid = GridSearchCV(
            GradientBoostingRegressor(random_state=42),
            gbr_params,
            cv=5,
            scoring='neg_mean_squared_error',
            n_jobs=-1
        )
        
        gbr_grid.fit(X_train_scaled, y_train)
        gbr_best = gbr_grid.best_estimator_
        
        # Predictions
        gbr_pred = gbr_best.predict(X_test_scaled)
        gbr_mse = mean_squared_error(y_test, gbr_pred)
        gbr_r2 = r2_score(y_test, gbr_pred)
        
        print(f"    GBR MSE: {gbr_mse:.4f}")
        print(f"    GBR R²: {gbr_r2:.4f}")
        
        self.models['carbon_estimator'] = gbr_best
        
        # Create feature importance plot
        self.plot_feature_importance(gbr_best, X_test_scaled.shape[1])
        
        return {
            'model': gbr_best,
            'mse': gbr_mse,
            'r2': gbr_r2,
            'predictions': gbr_pred,
            'actual': y_test
        }
    
    def plot_feature_importance(self, model, n_features):
        """Plot feature importance"""
        
        feature_names = ['activity_amount', 'emission_factor', 'uncertainty', 
                        'category', 'subcategory', 'unit']
        
        if hasattr(model, 'feature_importances_'):
            importances = model.feature_importances_
            
            plt.figure(figsize=(10, 6))
            indices = np.argsort(importances)[::-1]
            
            plt.title("Feature Importance - Carbon Estimation")
            plt.bar(range(len(importances)), importances[indices])
            plt.xticks(range(len(importances)), [feature_names[i] for i in indices], rotation=45)
            plt.tight_layout()
            plt.savefig('models/carbon_feature_importance.png')
            plt.show()
    
    def save_models(self, output_dir: str = "models"):
        """Save carbon estimation models"""
        
        from pathlib import Path
        Path(output_dir).mkdir(exist_ok=True)
        
        # Save models
        for name, model in self.models.items():
            joblib.dump(model, f"{output_dir}/{name}.joblib")
            print(f"💾 Saved {name}")
        
        # Save scalers and encoders
        for name, scaler in self.scalers.items():
            joblib.dump(scaler, f"{output_dir}/scaler_{name}.joblib")
            print(f"💾 Saved scaler_{name}")
        
        for name, encoder in self.encoders.items():
            joblib.dump(encoder, f"{output_dir}/carbon_encoder_{name}.joblib")
            print(f"💾 Saved carbon_encoder_{name}")

def main():
    """Main training function"""
    
    print("Starting model training...")
    
    # Create models directory
if __name__ == "__main__":
    main()
