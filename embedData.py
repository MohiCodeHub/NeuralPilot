import requests
import xmltodict
import os
from langchain.document_loaders import PyMuPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

if  __name__ == "__main__":

    keywords = "artificial intelligence, machine learning, deep learning, LLM, Large Language Model, AI, NLP, Natural Language Processing, neural networks, transformers, AI Agents"
    params = {
        "search_query": f"all:{keywords}",
        "start": "1",
        "max_results": "5",
    }

    response = requests.get("https://export.arxiv.org/api/query", params=params)
    if response.status_code == 200:
        data = response.text
    else:
        raise Exception(f"Failed to fetch data: {response.status_code}")

    data = xmltodict.parse(data)

    papers = []

    #Remove unnecessary data and skip papers with missing attributes
    for entry in data["feed"]["entry"]:
        try:
            published = entry["published"]
            title = entry["title"]
            for ref in entry["link"]:
                if ref["@type"] == "application/pdf":
                    pdf_url = ref["@href"]
                    break
            papers.append({
                "published": published,
                "title": title,
                "pdf_url": pdf_url
            }
        )
        except KeyError as e:
            #arvix sometimes has incomplete entries for a paper, in this case we skip the paper
            continue

    #set a chunk size
    chunk_size = 200 

    #Download the pdf from arvix, and turn into chunks
    for paper in papers:
        pdf_url = paper["pdf_url"]
        response = requests.get(pdf_url)
        if response.status_code == 200:
            pdf_path = os.path.join("papers", f"{paper['title']}.pdf")
            with open(pdf_path, "wb") as f:
                f.write(response.content)
            
            # Load the PDF and split it into chunks
            loader = PyMuPDFLoader(pdf_path)
            documents = loader.load()
            
            text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=20)
            chunks = text_splitter.split_documents(documents)
        else:
            #pdf link is sometimes outdated on arvix
            continue
    
