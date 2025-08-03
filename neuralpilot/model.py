from openai import OpenAI
from langchain.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings


class Model:

    def __init__(self, model = "gpt-4o", embedding_model = "text-embedding-3-small",vector_store_dir = "data/vector_store"):
        self.client = OpenAI()
        self.model = model
        self.embedding  = OpenAIEmbeddings(model = embedding_model)
        self.vector_store = FAISS.load_local(vector_store_dir, self.embedding, allow_dangerous_deserialization=True)

    def get_results(self,query, k = 3):

        results = self.vector_store.similarity_search(query, k = k)
        return results

    def process_results(self, results):
        processed_results = []
        for doc in results:
            entry = {
                "title" : doc.metadata.get("title", "N/A"),
                "authors" : ", ".join(doc.metadata.get("authors",[])),
                "published" : doc.metadata.get("published", "N/A"),
                "pdf_url" : doc.metadata.get("pdf_url", "N/A"),
                "page_content" : doc.page_content
            }
            processed_results.append(entry)
        return processed_results
    
    def get_rag_prompt(self, query, processed_results):
        rag_prompt = ["Context :"]
        for result in processed_results:
            temp_str = "\n".join(list(result.values()))
            rag_prompt.append(temp_str)

        rag_prompt.append("Question:")
        rag_prompt.append(query)
        rag_prompt.append("Answer:")

        return "\n".join(rag_prompt)
    
    def get_LLM_output(self, query):
        results = self.get_results(query)
        processed_results = self.process_results(results)
        rag_prompt = self.get_rag_prompt(query,processed_results)
        system_prompt = "You are a scientific assistant that answers user questions based solely on the provided context Do not explicitly mention the existence of the provided context or that the information came from documents, unless citing a source in parentheses."

        response = self.client.chat.completions.create(
            model = "gpt-4o",
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Use the following context to answer the question.\n {rag_prompt}"}
            ]           
        )
        return response.choices[0].message.content


        

        
        



    
