from langchain_community.tools.wikidata.tool import WikidataAPIWrapper, WikidataQueryRun
from langchain.tools import Tool

# Create the Wikidata API wrapper
wikidata_api = WikidataAPIWrapper()
wikidata_query = WikidataQueryRun(api_wrapper=wikidata_api)

# Define the LangChain tool
wikidata_tool = Tool(
    name="wikidata-farmer",
    func=wikidata_query.run,
    description=(
        """Do not use this for real-time weather or market prices.
        Fetches general agriculture-related facts and definitions from Wikidata. Used when farmers want background knowledge on crops, farming methods, pests, or agricultural concepts.
        Use this tool to answer factual questions related to farming,
        agriculture, crops, soil, fertilizers, irrigation, pests, agricultural policies,
        and rural development using Wikidata s knowledge base. """
    )
)
