# Create LangChain Tool
from langchain_core.tools import Tool
from langchain_experimental.agents import create_csv_agent
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
import os
# Load environment variables
load_dotenv()

# API key for Gemini
api_key = os.getenv("GEMINI_API_KEY")

llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
    google_api_key=api_key
)

agent1 = create_csv_agent(
    llm,
    "dataset\gov_scheme\india_crop_dataset_complete (1).csv",
    verbose=False,
    allow_dangerous_code=True,
    handle_parsing_errors=True
)
# Function to query the crop dataset
def crop_cultivation_lookup(query: str) -> str:
    """Search crop cultivation dataset for relevant crop or farming practices."""
    try:
        result = agent1.run(query)
        if not result or "I am sorry" in result:
            return "No relevant data found for your query."
        return result
    except Exception as e:
        # Handle parsing or CSV errors gracefully
        return f"No relevant data found. (Error: {str(e)})"

crop_cultivation_tool = Tool(
    name="crop_cultivation_lookup",
    description=(
        """Retrieves detailed agronomic and cultivation information from a CSV dataset,Look up cultivation details for Cereals,Fibre Crops,Green Manure,Oilseeds,Pulses,Sugar And Starch Crops,Citrus,Flowers,
        Forestry,Fruit,Medicinal Plants,Plantation Crops,Spice And Condiments,Spice And Condiments,Vegetable Crops	,flowers, and crops from a preloaded dataset.
        Includes general information, climate, soil type, land preparation, sowing temperature , seed varity  and quality, 
        fertilizer information , weed control, irrigation, plant protection, diseases and control, harvesting, temperature  and humidity requirements,
        and post-harvest handling. If data is not found in the dataset, this tool should call the Google Search Tool or Wikidata tools for relevant agricultural resources."""
    ),
    func=crop_cultivation_lookup
)

