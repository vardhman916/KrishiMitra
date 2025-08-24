import pandas as pd
from statsmodels.tsa.arima.model import ARIMA

def forecast_prices(df: pd.DataFrame, steps: int = 10):
    """
    Train ARIMA model and forecast future prices.
    df: must contain 'Date' and 'Price/quintal' columns.
    steps: number of future periods to forecast.
    """
    if df.empty:
        raise ValueError("No data available for the given filters. Cannot forecast.")

    series = df.set_index("Date")["Price/quintal"].sort_index()

    if len(series) < 30:  # You can tune this threshold
        raise ValueError(f"Not enough historical records ({len(series)}) to build a reliable ARIMA model.")

    # Fit ARIMA (basic config, can be tuned)
    try:
        model = ARIMA(series, order=(2, 1, 2))
        model_fit = model.fit()
    except Exception as e:
        raise RuntimeError(f"ARIMA model training failed: {str(e)}")

    # Forecast future prices
    forecast = model_fit.forecast(steps=steps)

    return forecast
