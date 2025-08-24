# connected_agent.py
import os
import re
from dotenv import load_dotenv

from langchain_core.tools import Tool
from langchain_community.utilities import GoogleSearchAPIWrapper

from price_prooces.predictor_tool import run_prediction


# =========================
# 🔹 Load Environment
# =========================
load_dotenv()

CSV_PATH = r"D:\OPEN_AI_API\dataset\historical_price\Price.csv"
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GOOGLE_CSE_ID = os.getenv("GOOGLE_CSE_ID")

if not CSV_PATH:
    raise ValueError("❌ CSV_PATH is not set in .env file")

if not GOOGLE_API_KEY or not GOOGLE_CSE_ID:
    raise ValueError("❌ Google API credentials are missing in .env file")


# =========================
# 🔹 Google Search Tool
# =========================
search = GoogleSearchAPIWrapper(
    google_api_key=GOOGLE_API_KEY,
    google_cse_id=GOOGLE_CSE_ID
)

CROPS = ["rice", "paddy", "wheat", "maize", "sugarcane", "barley", "mustard"]
DISTRICTS = ["gautam budh nagar", "agra", "meerut", "noida", "lucknow", "kanpur"]


def google_price_lookup(query: str):
    """
    Extract crop + district from query and fetch current market price using Google.
    """
    q = query.lower()

    # Extract crop
    commodity = next((c for c in CROPS if c in q), None)

    # Extract district (regex for flexible matching)
    district = next((d for d in DISTRICTS if re.search(rf"\b{d}\b", q)), None)

    if not commodity or not district:
        return "❌ Could not detect crop or district for Google search."

    # Make Google search query
    search_query = f"current mandi price of {commodity} in {district} today"
    resp = search.run(search_query)

    return resp[:300] if resp else "❌ No result from Google."


google_search_tool = Tool(
    name="google_search_tool",
    description="Fetches real-time mandi prices of crops from Google.",
    func=google_price_lookup
)


# =========================
# 🔹 Predictor Tool (ARIMA)
# =========================
def predictor_tool_func(query: str):
    """
    Extracts crop & district and runs ARIMA forecast.
    """
    q = query.lower()

    commodity = next((c.capitalize() for c in CROPS if c in q), None)
    district = next((d.title() for d in DISTRICTS if re.search(rf"\b{d}\b", q)), None)

    if not commodity or not district:
        return "❌ Could not detect crop or district for forecast."

    result = run_prediction(CSV_PATH, commodity, district)

    # Format forecast for readability
    if isinstance(result, dict) and "forecast" in result:
        try:
            result["forecast"] = result["forecast"].round(2).to_dict()
        except Exception:
            pass  # keep as-is if already dict/str

    return result


predictor_tool = Tool(
    name="predictor_tool",
    description="Forecasts crop price using ARIMA and gives sell/hold recommendation.",
    func=predictor_tool_func
)


# =========================
# 🔹 Combined Agent
# =========================
def connected_agent(query: str):
    """
    Runs both Google Search (for current price) and ARIMA Forecast (for future price).
    """
    print("🔎 Fetching current price from Google...")
    current_price = google_price_lookup(query)

    print("\n📈 Running ARIMA forecast...")
    forecast = predictor_tool_func(query)

    response = (
        f"=== Current Market Price (Google) ===\n{current_price}\n\n"
        f"=== Forecast & Recommendation (ARIMA) ===\n{forecast}"
    )
    return response


# =========================
# 🔹 Example Usage
# =========================
if __name__ == "__main__":
    query = "What is the current price of Maize in Gautam Budh Nagar 2025 and should I sell or not?"
    result = connected_agent(query)
    print("\nFinal Response:\n", result)
