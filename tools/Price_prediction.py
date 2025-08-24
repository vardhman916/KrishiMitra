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
# 🔹 Crop & District Dictionaries
# =========================
CROPS = {
    "rice": ["rice", "paddy"],
    "wheat": ["wheat"],
    "maize": ["maize", "corn"],
    "sugarcane": ["sugarcane"],
    "barley": ["barley"],
    "mustard": ["mustard", "sarson"],
}

DistrictS = [
    "gautam budh nagar", "agra", "meerut", "noida"
]
MarketS = [
    "dadri", "dankaur"  # <-- replace with your actual Market names in Gautam Budh Nagar
]


# =========================
# 🔹 Helper Functions
# =========================
def extract_crop_and_District(query: str):
    """
    Detect crop and District from query text.
    Returns (Commodity, District) or (None, None)
    """
    q = query.lower()

    # Crop detection
    Commodity = None
    for crop, aliases in CROPS.items():
        if any(alias in q for alias in aliases):
            Commodity = crop.capitalize()
            break

    # District detection (regex word boundary)
    District = None
    for d in DistrictS:
        if re.search(rf"\b{d}\b", q):
            District = d.capitalize()
            break

    Market = None
    for m in MarketS:
        if m in q:
            Market = m.title()
            break

    print(f"[DEBUG] Extracted Commodity: {Commodity}, District: {District}, Market: {Market}")
    return Commodity, District,Market


# =========================
# 🔹 Google Search Tool
# =========================
search = GoogleSearchAPIWrapper(
    google_api_key=GOOGLE_API_KEY,
    google_cse_id=GOOGLE_CSE_ID
)


def google_price_lookup(query: str):
    """
    Extract crop + District from query and fetch current Market price using Google.
    """
    Commodity, District,Market = extract_crop_and_District(query)

    if not Commodity or not District:
        return "❌ Could not detect crop or District for Google search."

    search_query = f"current {Market} mandi price of {Commodity} in {District} today"
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
    Extracts crop & District and runs ARIMA forecast.
    """
    Commodity, District,Market = extract_crop_and_District(query)

    if not Commodity or not District:
        return "❌ Could not detect crop or District for forecast."

    try:
        result = run_prediction(CSV_PATH, Commodity, District,Market)
    except Exception as e:
        print(f"[DEBUG] Exception in run_prediction: {e}")
        return f"❌ Error in prediction: {e}"

    # Format forecast nicely
    if isinstance(result, dict) and "forecast" in result:
        try:
            result["forecast"] = result["forecast"].round(2).to_dict()
        except Exception:
            pass  # already dict

    return result


predictor_tool = Tool(
    name="predictor_tool",
    description="Advanced ARIMA-based crop price forecasting tool that analyzes historical price data to predict future crop prices. Provides detailed price forecasts, trend analysis, and actionable buy/sell/hold recommendations based on predicted price movements. Use this tool when users ask about: future crop prices, price predictions, market trends, whether to sell or hold crops, investment decisions, or any forecasting-related queries. Input should include crop name, district, and market for accurate predictions.",
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

#conneted agent tool
connected_agent_tool = Tool(
    name="connected_agent_tool",
    description="Gets both current market prices from Google and ARIMA forecast with buy/sell recommendations for crops in specific districts and markets.",
    func=connected_agent
)

forcast = ['google_search_tool', 'predictor_tool', 'connected_agent_tool']