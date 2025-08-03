import os
import json
from langchain_community.document_loaders import PyMuPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
from langchain_community.vectorstores import faiss
from langchain_openai import OpenAIEmbeddings

if  __name__ == "__main__":
    API_KEY = os.getenv("OPENAI_API_KEY")
    if not API_KEY:
        raise Exception("API Key is not set as env variable")
    metadata_dir = "data/paper_metadata.json"
    papers_dir = "data/papers"
    
    with open(metadata_dir, "r") as f:
        papers = json.load(f)


    #set a chunk size
    chunk_size = 1000 
    #Load pdfs and turn into chunks for embedding
    for paper in papers:
        try:
            title = paper["title"]
            pdf_path = os.path.join(papers_dir, f"{title}.pdf")
            loader = PyMuPDFLoader(pdf_path)
            pdf_documents = loader.load()
                
            text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=20)
            chunks = text_splitter.split_documents(pdf_documents)
            paper["chunks"] = chunks
        except Exception as e:
            print(f"Error processing PDF for {paper['title']}: {e}")
            continue
    
    # Prepare documents with metadata for FAISS
    documents = []
    
    for paper in papers:
        if "chunks" not in paper:
            continue
            
        for chunk in paper["chunks"]:
            doc = Document(
                page_content=chunk.page_content,
                metadata={
                    "title": paper["title"],
                    "authors": paper["authors"],
                    "pdf_url": paper["pdf_url"],
                    "published": paper["published"]
                }
            )
            documents.append(doc)

    #Embedding model 
    embedding = OpenAIEmbeddings(model="text-embedding-3-small")


    db = faiss.FAISS.from_documents(
        documents, 
        embedding,
        normalize_L2=True,  
        #Use cosine similarity, since OpenAI embedding model is trained on it.
        distance_strategy=faiss.DistanceStrategy.COSINE  
    )
    db.save_local("data/vector_store")
    
    print(f"Successfully created vector database with {len(documents)} documents")#







    
        
    
    


    

    
