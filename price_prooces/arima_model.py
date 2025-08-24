import pandas as pd
from statsmodels.tsa.arima.model import ARIMA
import warnings

# warnings.filterwarnings('ignore', category=FutureWarning)

warnings.filterwarnings('ignore', category=UserWarning)

def forecast_prices(df: pd.DataFrame, steps: int = 10):
    """
    Train ARIMA model and forecast future prices.
    df: must contain 'Date' and 'Price/quintal' columns.
    steps: number of future periods to forecast.
    """
    if df.empty:
        raise ValueError("No data available for the given filters. Cannot forecast.")

    df_clean = df.groupby("Date")["Price/quintal"].mean().reset_index()
    df_clean.set_index("Date", inplace=True)
    series = df_clean["Price/quintal"]
    
    # Clean and set proper frequency
    series.index = pd.to_datetime(series.index)

    # Try to infer frequency first
    try:
        inferred_freq = pd.infer_freq(series.index)
        if inferred_freq:
            series = series.asfreq(inferred_freq)
        else:
            # Fallback to daily frequency with interpolation
            series = series.resample('D').interpolate(method='linear')
    except:
        # If all else fails, use daily resampling
        series = series.resample('D').mean().interpolate()


    if len(series) < 30:  # You can tune this threshold
        raise ValueError(f"Not enough historical records ({len(series)}) to build a reliable ARIMA model.")

    # Fit ARIMA (basic config, can be tuned)
    series = series.dropna()
    try:
        model = ARIMA(series, order=(1, 1, 1))
        model_fit = model.fit()
    except Exception as e:
        raise RuntimeError(f"ARIMA model training failed: {str(e)}")

    # Forecast future prices
    forecast_result = model_fit.get_forecast(steps=steps)
    forecast = forecast_result.predicted_mean

    return forecast
