from openai import OpenAI
from langchain.vectorstores import FAISS
from langchain.schema import Document
from langchain_openai import OpenAIEmbeddings
from typing import List, Dict, Tuple, Optional


class Model:

    def __init__(self, model: str = "gpt-4o", embedding_model: str = "text-embedding-3-small", vector_store_dir: str = "data/vector_store"):
        self.client = OpenAI()
        self.model = model
        self.embedding = OpenAIEmbeddings(model=embedding_model)
        self.vector_store = FAISS.load_local(vector_store_dir, self.embedding, allow_dangerous_deserialization=True)

    # Fetch top semantically similar results from vector database
    def get_results(self, query: str, k: int = 3) -> List[Document]:
        results = self.vector_store.similarity_search(query, k=k)
        return results

    # Process results through unpacking document metadata and content into a dictionary
    def process_results(self, results: List[Document]) -> List[Dict[str, str]]:
        processed_results = []
        for doc in results:
            entry = {
                "title": doc.metadata.get("title", "N/A"),
                "authors": ", ".join(doc.metadata.get("authors", [])),
                "published": doc.metadata.get("published", "N/A"),
                "pdf_url": doc.metadata.get("pdf_url", "N/A"),
                "page_content": doc.page_content
            }
            processed_results.append(entry)
    
        return processed_results
    
    # Structure the RAG prompt by prepending fetched results as context to the query
    def get_rag_prompt(self, query: str, processed_results: List[Dict[str, str]]) -> str:
        rag_prompt = ["Context :"]
        for result in processed_results:
            temp_str = "\n".join(list(result.values()))
            rag_prompt.append(temp_str)

        rag_prompt.append("Question:")
        rag_prompt.append(query)
        rag_prompt.append("Answer:")

        return "\n".join(rag_prompt)
    
    # Context is inputted and stored as a list of tuples [(user_msg: str, bot_msg: str)]
    # Unpack context into OpenAI API formatted messages to pass to client
    def process_context(self, context: List[Tuple[str, str]]) -> List[Dict[str, str]]:
        processed_context = []
        for query, response in context:
            processed_context.append(
                {"role": "user", "content": query}
            )
            processed_context.append(
                {"role": "assistant", "content": response}
            )
        return processed_context

    # Use an LLM to check if a query is related to any ML topic
    def Is_ML_related(self, query: str) -> bool:
        keywords = "artificial intelligence, machine learning, deep learning, LLM, Large Language Model, AI, NL, Natural Language Processing, neural networks, transformers, AI Agents"
        system_prompt = f"You are a classifier. Respond only with yes or no depending on whether the input is related to any of the following keywords {keywords} ."
        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": query}
            ]
        )
        response = response.choices[0].message.content.strip().lower()
        if response == "yes":
            return True
        return False
    
    # Main RAG Pipeline
    # 1. Fetch results from vector db 
    # 2. process conversation context and results and obtain RAG prompt
    # 3. pass RAG prompt, system message, and context into the client. Return client response.
    def get_rag_output(self, query: str, conversation_context: List[Tuple[str, str]]) -> str:
        processed_context = self.process_context(conversation_context)
        results = self.get_results(query)
        processed_results = self.process_results(results)
        rag_prompt = self.get_rag_prompt(query, processed_results)
        system_prompt = """
                        You are NeuralPilot, an ML focused scientific assistant that answers user questions based solely on the provided context, which has
                        been fetched from ML papers on arxiv.
                        Do not explicitly mention the existence of the provided context. When using information from the context,
                        you must reference it in your response, using the provided title name, authors, and date of publishment. Format
                        such data into formal citations, in a user-friendly format.
                        """
        

        messages = [{"role": "system", "content": system_prompt}]
        messages += processed_context
        messages.append({"role": "user", "content": f"Use the following context to answer the question.\n {rag_prompt}"})

        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
        )
        return response.choices[0].message.content

    # Non RAG pipeline
    # Pass conversation context, system_prompt, and query into client. Return response
    def get_non_rag_output(self, query: str, conversation_context: List[Tuple[str, str]]) -> str:
        processed_context = self.process_context(conversation_context)
        system_prompt = "You are NeuralPilot, a friendly research assistant that provides reliable and up-to-date ML data."
        messages = processed_context + [{"role": "system", "content": system_prompt}] + [{"role": "user", "content": query}]
        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=messages
        )
        return response.choices[0].message.content
        
    # get_output wraps around both output functions, get_non_rag_output and get_rag_output. 
    # Main method to be called for obtaining client response
    # If a query is related to ML, get_rag_output is called. Otherwise, get_non_rag_output is called.
    # client response from either call is returned.
    def get_output(self, query: str, conversation_context: List[Tuple[str, str]] = []) -> str:
        if self.Is_ML_related(query):
            response = self.get_rag_output(query, conversation_context)
        else:
            response = self.get_non_rag_output(query, conversation_context)
        
        return response
        
        

        
        



    
