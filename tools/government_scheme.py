import os
from dotenv import load_dotenv
from langchain_experimental.agents import create_csv_agent
from langchain_google_genai import ChatGoogleGenerativeAI

# Load environment variables
load_dotenv()

# API key for Gemini
api_key = os.getenv("GEMINI_API_KEY") 

# Initialize LLM
llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
    google_api_key=api_key
)

# Create CSV agent
agent = create_csv_agent(
    llm,
    "dataset/gov_scheme/Government_Schemes_Advanced.csv",
    verbose=False,
    allow_dangerous_code=True
)

# Define the tool function
def government_scheme_lookup(query: str) -> str:
    """Search government schemes dataset for relevant schemes."""
    return agent.run(query)

# Create LangChain tool
from langchain_core.tools import Tool

government_scheme_tool = Tool(
    name="government_scheme_lookup",
    description="Searches a preloaded CSV dataset of active central government agricultural schemes in India, providing scheme name, description, eligibility, benefits, and application process. If a scheme is not found in the dataset, this tool should call the Google Search Tool for up-to-date details.",
    func=government_scheme_lookup
)

