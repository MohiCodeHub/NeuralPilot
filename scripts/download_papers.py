import requests
import xmltodict
import os
import re
from time import sleep
import json

#function to sanitize title name, avoiding special characters.
#useful when creating file names based on paper title names
def safe_title(title):
    safe_title = re.sub(r'[^\w\s-]', '', title.strip())
    safe_title = re.sub(r'[-\s]+', '-', safe_title)
    return safe_title

if  __name__ == "__main__":

    keywords = ["artificial intelligence", "machine learning", "deep learning", "LLM", "Large Language Model", "AI", "NLP", "Natural Language Processing", "neural networks", "transformers", "AI Agents"]
    papers_dir = "/data/papers" 
    metadata_dir = "/data/paper_metadata.json"
    os.makedirs(papers_dir, exist_ok=True)
    #Some keywords query the same papers, this list holds metadata of all unique papers
    unique_papers = []
     
    for keyword in keywords:

        params = {
            "search_query": f"all:{keyword}",
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

        if not "entry" in data["feed"]:
            #no papers retrieved from keyword search, proceed to next keyword
            continue
        
        #obtain paper metadata, skipping those with missing fields
        for entry in data["feed"]["entry"]:
            try:
                title = safe_title(entry["title"])
                published = entry["published"]
                for ref in entry["link"]:
                    if ref["@type"] == "application/pdf":
                        pdf_url = ref["@href"]
                        break
                raw_authors = entry["author"]
                if isinstance(raw_authors, dict):
                     authors = [raw_authors["name"]]
                else:
                    authors = [author["name"] for author in raw_authors ]
                    papers.append({
                        "published": published,
                        "title": title,
                        "pdf_url": pdf_url,
                        "authors" : authors
                    }
                )
            except KeyError:
                #arvix sometimes has incomplete entries for a paper, in this case we skip the paper
                continue

        #download pdfs
        for paper in papers:
            pdf_url = paper["pdf_url"]
            response = requests.get(pdf_url)
            if response.status_code == 200:
                file_name = paper["title"]
                pdf_path = os.path.join(papers_dir, f"{file_name}.pdf")

                if os.path.isfile(pdf_path):
                    #paper already downloaded from previous keyword search.
                    continue           
                unique_papers.append(paper)
                with open(pdf_path, "wb") as f:
                    f.write(response.content)
        
        #prevent hitting API limits
        sleep(3)


    with open(metadata_dir,"w") as f:
        json.dump(unique_papers, f, indent = 2)
    
    print(f"Number of downloaded papers : {len(unique_papers)}")
