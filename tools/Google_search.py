# Google Search Tool for Agricultural Information
import os
from langchain_core.tools import Tool
from langchain_community.utilities import GoogleSearchAPIWrapper
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Read API keys
GOOGLE_CSE_ID = os.getenv("GOOGLE_CSE_ID")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# Initialize Google Search API
search = GoogleSearchAPIWrapper(
    google_api_key=GOOGLE_API_KEY,
    google_cse_id=GOOGLE_CSE_ID
)

# Define the tool
google_search_tool = Tool(
    name="google_search_tool",
    description="Performs real-time searches to fetch missing or latest agricultural information not found in local datasets. Acts as a backup for the Government Schemes Tool and Other Information Tool, and can fetch news, reports,other information and policy updates.",
    func=search.run
)
