from carbon_calculator import CarbonCalculator

def test_calculator():
    calculator = CarbonCalculator()
    
    # Test transportation
    print("\nTesting Transportation:")
    car_emission = calculator.calculate_footprint(
        category="Transportation",
        subcategory="gasoline_car",
        amount=50,  # miles
        unit="miles"
    )
    print(f"50 miles in gasoline car: {car_emission:.2f} kg CO2")
    
    # Test energy
    print("\nTesting Energy:")
    electricity_emission = calculator.calculate_footprint(
        category="Energy",
        subcategory="electricity",
        amount=100,  # kWh
        unit="kWh"
    )
    print(f"100 kWh electricity: {electricity_emission:.2f} kg CO2")
    
    # Test food
    print("\nTesting Food:")
    meat_emission = calculator.calculate_footprint(
        category="Food",
        subcategory="beef",
        amount=1,  # kg
        unit="kg"
    )
    print(f"1 kg beef: {meat_emission:.2f} kg CO2")

if __name__ == "__main__":
    test_calculator()
