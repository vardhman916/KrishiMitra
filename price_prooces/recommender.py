import numpy as np
import pandas as pd

def give_recommendation(history: pd.Series, forecast: pd.Series) -> str:
    """
    Recommendation: SELL if price expected to drop, else HOLD.
    """
    last_price = history.iloc[-1]
    avg_future = np.mean(forecast)

    if avg_future < last_price:
        return f"SELL ❌ | Current: {last_price}, Expected Avg Future: {round(avg_future,2)}"
    else:
        return f"HOLD ✅ | Current: {last_price}, Expected Avg Future: {round(avg_future,2)}"
