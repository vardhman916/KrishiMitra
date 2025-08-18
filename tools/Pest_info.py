from langchain_google_genai import GoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain.prompts import ChatPromptTemplate
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_retrieval_chain
from langchain_chroma import Chroma
from langchain_core.runnables import RunnableLambda
from langchain.tools import tool
import os
from dotenv import load_dotenv

load_dotenv()

gemini_api = os.getenv("GEMINI_API_KEY3")

# Validate API key
if not gemini_api:
    raise ValueError("GEMINI_API_KEY3 environment variable not found")

print("Setting up embeddings and LLM...")

# 1. Load embeddings + vectorstore
embeddings = GoogleGenerativeAIEmbeddings(
    model="models/embedding-001",  # Fixed: Added slash
    google_api_key=gemini_api
)

llm = GoogleGenerativeAI(
    model="gemini-2.0-flash",  # Fixed: Use stable model
    google_api_key=gemini_api,
    temperature=0.1
)

# Fixed typo: vectorestore -> vectorstore
vectorstore_chroma = Chroma(
    embedding_function=embeddings,
    persist_directory="./vectorstore"  # Fixed: Match your build script path
)

# Check if vectorstore has documents
try:
    collection = vectorstore_chroma._collection
    doc_count = collection.count()
    print(f"Number of documents in vectorstore: {doc_count}")
    
    if doc_count == 0:
        print("Warning: Vectorstore is empty. Please run the build_vectorstore.py script first.")
        exit()
        
except Exception as e:
    print(f"Error accessing vectorstore: {e}")
    print("Make sure you've run the build_vectorstore.py script first.")
    exit()



# 2. Use both similarity and MMR retrievers
retriever_sim = vectorstore_chroma.as_retriever(
    search_type="similarity",
    search_kwargs={"k": 15}
)

retriever_mmr = vectorstore_chroma.as_retriever(
    search_type="mmr",
    search_kwargs={"k": 15, "fetch_k": 20}
)

 


retriever_mmr = vectorstore_chroma.as_retriever(
    search_type="mmr",
    search_kwargs={"k": 15, "fetch_k": 20}
)

retriever_sim = vectorstore_chroma.as_retriever(
    search_type="similarity",
    search_kwargs={"k": 15}
)



@tool
def combined_Pest_tool(query: str) -> str:
    """Search Pest regarding information for any crops in PDFs using both MMR and Similarity. if no result retrun then do google search or wikidata"""
    mmr_docs = retriever_mmr.invoke(query)
    sim_docs = retriever_sim.invoke(query)

    all_docs = mmr_docs + sim_docs
    seen = set()
    unique_docs = []
    for doc in all_docs:
        if doc.page_content not in seen:
            seen.add(doc.page_content)
            unique_docs.append(doc)
        if not unique_docs:
            return "NO_RESULTS_FOUND"
    prompt = ChatPromptTemplate.from_template("""
    You are **Krishi Mitra**, a Farmer AI assistant. 
Your role is to provide farmers with accurate and practical information about crop pests.

Instructions:
1. First, clearly identify the pest(s) related to the crop in the question. 
   - Mention the common name, scientific name, and the crop part affected.
2. Then, give **Farming Advice**:
   - Explain the symptoms and damage in simple words.
   - Suggest organic / biological / chemical control measures.
   - Keep the advice clear, step-by-step, and farmer-friendly.

<context>
{context}
</context>

Question: {question}

Answer:
""")
    llm = GoogleGenerativeAI(model="gemini-2.0-flash", google_api_key=gemini_api)
    document_chain = create_stuff_documents_chain(llm=llm, prompt=prompt)
    result = document_chain.invoke({"context": unique_docs, "question": query})
    return result