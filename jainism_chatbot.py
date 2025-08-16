from retriever.build_vectorstore import *
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain.chains import RetrievalQA
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.documents import Document
import streamlit as st
import os
from langchain_core.runnables import RunnableSequence, RunnableLambda
from langchain_core.runnables import RunnableParallel
from langchain_core.output_parsers import StrOutputParser
from langchain.agents import create_tool_calling_agent, AgentExecutor
from dotenv import load_dotenv
load_dotenv()
from langchain_chroma import Chroma
from langchain_core.tools import tool
from langchain.agents.agent_toolkits import create_retriever_tool
import wikipedia
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_retrieval_chain
embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001",
                                          google_api_key=gemini_api)

# Get API key
api_key = os.getenv("GEMINI_API_KEY")
folder_path = "./pdf"
docs = load_pdf(folder_path)
# Split document into chunks
chunks = split_documents(docs)
#embed and store the chunks in vectorstore
embed_and_store(chunks,save_path = "Jain chatbot vectorstore")
vectorestore_chroma = Chroma(
    embedding_function=embeddings,
    persist_directory="Jain chatbot vectorstore"
)

# it will do it will take all document from vector stor--->put in the prompt---> then it send to llm 


retriever_mmr = vectorestore_chroma.as_retriever(
    search_type="mmr",
    search_kwargs={"k": 15, "fetch_k": 20}
)

retriever_sim = vectorestore_chroma.as_retriever(
    search_type="similarity",
    search_kwargs={"k": 15}
)

# Wikipedia tool function
@tool
def wikipedia_search(query: str) -> str:
    """Search Wikipedia and return a short summary of the topic or jain festical date"""
    try:
        wikipedia.set_lang("en")
        return wikipedia.summary(query, sentences=3)
    except Exception as e:
        return f"Wikipedia error: {str(e)}"

@tool
def combined_jainism_tool(query: str) -> str:
    """Search Jain PDFs using both MMR and Similarity. Use this for most Jainism-related questions."""
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
    You are an AI assistant trained in Jainism. Use the following context to answer the question respectfully and accurately.

    <context>
    {context}
    </context>

    Question: {question}
    """)
    llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", google_api_key=gemini_api)
    document_chain = create_stuff_documents_chain(llm=llm, prompt=prompt)
    result = document_chain.invoke({"context": unique_docs, "question": query})
    return result

# Initiate the chat model
agent_prompt = ChatPromptTemplate.from_template("""
You are an AI assistant trained in Jainism. Your role is to provide clear, respectful, and accurate answers based on Jain scriptures, teachings, and philosophies.

You can use tools such as Jain PDF Search and Wikipedia to answer questions. Always prefer Jain PDF first. If it returns "NO_RESULTS_FOUND", you may use Wikipedia.

Instructions:
- Use the tools wisely based on the question.
- Do not guess.
- Be factual and respectful.

{agent_scratchpad}

Question: {input}
""")
    
# Tools and agent setup
tools = [combined_jainism_tool, wikipedia_search]
llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", google_api_key=gemini_api)
agent = create_tool_calling_agent(llm, tools,agent_prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=False)


# Streamlit UI
st.set_page_config(page_title="Geo Jainism AI Assistant", page_icon="./logo/logo.jpg")
# st.image("my_logo.png", width=150)
st.image("./logo/logo.jpg", width=50)
st.title("GeoJainism AI Assistant")
# st.image("A_screenshot_of_a_Jainism_AI_Assistant_web_applica.png", use_column_width=True)

user_query = st.text_input("Ask a question about Jainism:")
if st.button("Get Answer") and user_query:
    with st.spinner("Thinking..."):
        response =  agent_executor.invoke({"input": user_query})
        st.markdown("### 🕉️ Answer")
        st.write(response["output"])


#python jainism_chatbot.py
# sample_query = "Who was Mahavira?"
# results = parallel_retrievers.invoke(sample_query)
# print("MMR:", type(results["mmr"][0]))
# print("Similarity:", type(results["similarity"][0]))

#give me summary of  Sallekhana from wikipedia?
