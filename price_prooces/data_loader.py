import pandas as pd

def load_data(filepath: str) -> pd.DataFrame:
    """
    Load and clean agriculture price dataset.
    """
    df = pd.read_csv(filepath)

    # Convert Date column to datetime
    df["Date"] = pd.to_datetime(df["Date"], format="%d-%m-%Y", errors="coerce")

    # Ensure price is numeric
    df["Price/quintal"] = pd.to_numeric(df["Price/quintal"], errors="coerce")

    # Drop missing values
    df.dropna(subset=["Price/quintal"], inplace=True)

    return df


def filter_data(df: pd.DataFrame, commodity: str, district: str = None, market: str = None) -> pd.DataFrame:
    """
    Filter dataset by commodity, district, and market.
    """
    data = df[df["Commodity"].str.contains(commodity, case=False, na=False)]

    if district:
        data = data[data["District"].str.contains(district, case=False, na=False)]

    if market:
        data = data[data["Market"].str.contains(market, case=False, na=False)]

    return data.sort_values("Date")
