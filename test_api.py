from carbon_api_integrator import CarbonAPIIntegrator
import asyncio
import os

async def test_api():
    # Initialize API integrator
    api = CarbonAPIIntegrator()
    
    # Test electricity usage
    print("\nTesting Electricity Usage:")
    electricity_data = {
        'kwh': 100,
        'country': 'us',
        'state': 'ca'  # California
    }
    try:
        # Use the main get_carbon_estimate method which handles all providers
        electricity_estimate = await api.get_carbon_estimate('electricity', electricity_data)
        if electricity_estimate:
            print(f"100 kWh in California: {electricity_estimate.carbon_kg:.2f} kg CO2")
            print(f"Source: {electricity_estimate.source}")
            print(f"Methodology: {electricity_estimate.methodology}")
        else:
            print("No estimate available for electricity")
    except Exception as e:
        print(f"Error in electricity estimate: {str(e)}")
    
    # Test transportation
    print("\nTesting Transportation:")
    transport_data = {
        'distance': 50,
        'vehicle_type': 'gasoline_car'
    }
    try:
        # Use the main get_carbon_estimate method which handles all providers
        transport_estimate = await api.get_carbon_estimate('transportation', transport_data)
        if transport_estimate:
            print(f"50 miles in gasoline car: {transport_estimate.carbon_kg:.2f} kg CO2")
            print(f"Source: {transport_estimate.source}")
            print(f"Methodology: {transport_estimate.methodology}")
        else:
            print("No estimate available for transportation")
    except Exception as e:
        print(f"Error in transportation estimate: {str(e)}")

if __name__ == "__main__":
    # Set API key (replace with your actual API key)
    os.environ['CARBON_INTERFACE_API_KEY'] = 'your_api_key_here'
    asyncio.run(test_api())
