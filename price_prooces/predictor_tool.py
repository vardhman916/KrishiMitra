import pandas as pd
from price_prooces.data_loader import load_data, filter_data
from price_prooces.arima_model import forecast_prices
from price_prooces.recommender import give_recommendation

def run_prediction(csv_path: str, commodity: str, district: str,market: str): 
    """
    Run prediction pipeline:
    1. Load dataset
    2. Filter by commodity & district
    3. Forecast using ARIMA
    4. Generate recommendation
    """
    if not csv_path:
        raise ValueError("CSV path must be provided. No default is set.")
    if not commodity:
        raise ValueError("Commodity must be provided in the query. No default is set.")
    if not district:
        raise ValueError("District must be provided in the query. No default is set.")

    # Load data
    df = load_data(csv_path)

    # Filter dataset
    filtered = filter_data(df, commodity, district,market)

    if filtered.empty:
        raise ValueError(f"No data found for {commodity} in {market} in {district}")

    # Forecast future prices
    forecast = forecast_prices(filtered, steps=10)

    # Generate recommendation
    recommendation = give_recommendation(filtered["Price/quintal"], forecast)

    return {
        "forecast": forecast,
        "recommendation": recommendation
    }
