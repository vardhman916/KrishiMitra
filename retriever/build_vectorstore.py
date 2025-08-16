from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_google_genai import GoogleGenerativeAIEmbeddings
import os
from dotenv import load_dotenv
load_dotenv()
import glob
gemini_api = os.getenv("GEMINI_API_KEY")
# python retriever/build_vectorstore.py

# load PDF file from data repository
def load_pdf(folder_path):
    pdf_files = glob.glob(os.path.join(folder_path, "*.pdf"))
    all_docs = []
    for pdf_file in pdf_files:
        loader = PyPDFLoader(pdf_file)
        docs = loader.load()
        all_docs.extend(docs)
    return all_docs

def split_documents(docs):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size = 2000,
        chunk_overlap = 300)
    return splitter.split_documents(docs)

def embed_and_store(docs,save_path):
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001",
                                          google_api_key=gemini_api)
    if isinstance(docs[0], str):
        docs = [Document(page_content=chunk) for chunk in docs]
    vectorstore = Chroma.from_documents(documents = docs, 
                                        embedding = embeddings, 
                                        persist_directory=save_path)
    return vectorstore