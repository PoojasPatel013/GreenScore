# 📊 Kaggle Datasets for Carbon Footprint Tracking Models

## 🏦 **Transaction Classification Datasets**

### **Primary Datasets**
1. **[PaySim Mobile Money Dataset](https://www.kaggle.com/ealaxi/paysim1)**
   - **Size**: 6.3M transactions
   - **Features**: Transaction type, amount, origin/destination accounts
   - **Use**: Transaction pattern analysis and fraud detection
   - **Relevance**: High - real transaction data with categories

2. **[Credit Card Fraud Detection](https://www.kaggle.com/mlg-ulb/creditcardfraud)**
   - **Size**: 284K transactions
   - **Features**: Anonymized features, transaction amount, class
   - **Use**: Anomaly detection in financial transactions
   - **Relevance**: Medium - good for transaction analysis

3. **[Bank Account Transactions](https://www.kaggle.com/aabhinavbhat/bank-account-transactions)**
   - **Size**: 50K+ transactions
   - **Features**: Description, amount, date, category
   - **Use**: Direct transaction categorization
   - **Relevance**: Very High - exactly what we need

### **Merchant & Business Datasets**
4. **[Yelp Dataset](https://www.kaggle.com/yelp-dataset/yelp-dataset)**
   - **Size**: 8M reviews, 200K businesses
   - **Features**: Business categories, location, reviews
   - **Use**: Merchant categorization and carbon intensity mapping
   - **Relevance**: High - comprehensive business categories

5. **[Brazilian E-Commerce Dataset](https://www.kaggle.com/olistbr/brazilian-ecommerce)**
   - **Size**: 100K orders
   - **Features**: Product categories, seller info, customer data
   - **Use**: E-commerce transaction patterns
   - **Relevance**: Medium - specific to e-commerce

## 🌍 **Carbon Emissions Datasets**

### **Primary Carbon Data**
6. **[CO2 Emissions Dataset](https://www.kaggle.com/sovitrath/carbon-emissions)**
   - **Size**: Global emissions by country/year
   - **Features**: Country, year, CO2 emissions, population
   - **Use**: Country-level emission factors
   - **Relevance**: High - baseline emission factors

7. **[Greenhouse Gas Reporting Program](https://www.kaggle.com/epa/greenhouse-gas-reporting-program)**
   - **Size**: EPA facility-level emissions
   - **Features**: Facility type, emissions by gas type, location
   - **Use**: Industry-specific emission factors
   - **Relevance**: Very High - official EPA data

8. **[Global Food Emissions](https://www.kaggle.com/sevgisarac/how-much-co2-does-your-food-produce)**
   - **Size**: Food product emissions
   - **Features**: Food type, CO2 per kg, production method
   - **Use**: Food carbon footprint calculation
   - **Relevance**: Very High - specific to food emissions

### **Energy & Transportation**
9. **[US Energy Consumption](https://www.kaggle.com/robikscube/hourly-energy-consumption)**
   - **Size**: Hourly energy consumption data
   - **Features**: Date, energy consumption by region
   - **Use**: Energy usage patterns and emission factors
   - **Relevance**: High - for electricity carbon calculations

10. **[Global Transportation Emissions](https://www.kaggle.com/prasertk/co2-emissions-vs-gasoline-consumption)**
    - **Size**: Transportation emissions by country
    - **Features**: Country, fuel consumption, CO2 emissions
    - **Use**: Transportation emission factors
    - **Relevance**: High - transportation is major category

## 🛍️ **Retail & Shopping Datasets**

11. **[Online Retail Dataset](https://www.kaggle.com/vijayuv/onlineretail)**
    - **Size**: 1M+ transactions
    - **Features**: Product description, quantity, price, customer
    - **Use**: Product categorization and shopping patterns
    - **Relevance**: Medium - for shopping carbon estimation

12. **[US Consumer Expenditure Survey](https://www.kaggle.com/bureau-of-labor-statistics/consumer-expenditure-survey)**
    - **Size**: Detailed household spending
    - **Features**: Spending categories, demographics, amounts
    - **Use**: Spending pattern analysis for carbon estimation
    - **Relevance**: High - realistic spending patterns

## 📱 **Additional Specialized Datasets**

### **Location & Demographics**
13. **[US Census Data](https://www.kaggle.com/census/population-estimates)**
    - **Use**: Regional factors for carbon calculations
    - **Relevance**: Medium - for regional scaling

14. **[World Cities Database](https://www.kaggle.com/max-mind/world-cities-database)**
    - **Use**: Location-based emission factors
    - **Relevance**: Medium - geographic context

### **Financial Market Data**
15. **[Stock Market Dataset](https://www.kaggle.com/borismarjanovic/price-volume-data-for-all-us-stocks-etfs)**
    - **Use**: Corporate spending pattern analysis
    - **Relevance**: Low - indirect relevance

## 🔧 **How to Use These Datasets**

### **For Transaction Classification:**
```python
# Combine datasets for comprehensive training
datasets = [
    'bank-account-transactions',  # Primary transaction data
    'yelp-dataset',              # Merchant categories
    'paysim1'                    # Transaction patterns
]

# Features to extract:
features = [
    'description',     # Transaction description
    'amount',         # Transaction amount
    'merchant',       # Merchant name
    'category',       # Ground truth category
    'date',          # Temporal features
    'location'       # Geographic features
]
