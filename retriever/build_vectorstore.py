from langchain_community.document_loaders import PyMuPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document
from langchain_google_genai import GoogleGenerativeAIEmbeddings
import os
from dotenv import load_dotenv
load_dotenv()
import glob

gemini_api = os.getenv("GEMINI_API_KEY3")
# python retriever/build_vectorstore.py

# load PDF file from data repository
def load_pdf(folder_path):
    pdf_files = glob.glob(os.path.join(folder_path, "*.pdf"))
    all_docs = []
    for pdf_file in pdf_files:
        try:
            loader = PyMuPDFLoader(pdf_file)
            docs = loader.load()
            all_docs.extend(docs)
            print(f"Successfully loaded: {pdf_file}")
        except Exception as e:
            print(f"Error loading {pdf_file}: {e}")
            continue
    return all_docs

def split_documents(docs):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size = 1000,
        chunk_overlap = 300)
    return splitter.split_documents(docs)

def embed_and_store(docs, save_path):
    try:
        embeddings = GoogleGenerativeAIEmbeddings(
            model="models/embedding-001",
            google_api_key=gemini_api
        )
        
        if isinstance(docs[0], str):
            docs = [Document(page_content=chunk) for chunk in docs]
            
        vectorstore = Chroma.from_documents(
            documents=docs, 
            embedding=embeddings, 
            persist_directory=save_path
        )
        print(f"Successfully created vectorstore with {len(docs)} documents")
        return vectorstore
    except Exception as e:
        print(f"Error creating vectorstore: {e}")
        return None
    

if __name__ == "__main__":
    folder_path = "./dataset"
    save_path = "vectorstore"
    
    print("Starting PDF processing...") 
    
    # Load PDF documents
    docs = load_pdf(folder_path)
    print(f"Loaded {len(docs)} documents")
    
    if not docs:
        print("No documents loaded. Exiting.")
        exit()
    
    # Split documents into smaller chunks
    split_docs = split_documents(docs)
    print(f"Split into {len(split_docs)} chunks")
    
    # Embed and store in vectorstore
    vectorstore = embed_and_store(split_docs, save_path)
    
    if vectorstore:
        print("Vectorstore created successfully!")
    else:
        print("Failed to create vectorstore.")