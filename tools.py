import chromadb
from openai import OpenAI
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np



class extractiontool:
    

    def __init__(self,document):
        self.client = chromadb.PersistentClient(path="./chroma_store")
        self.collection = self.client.get_or_create_collection("resume_documents")
    

    def embedtext(self,document,api_key):
        # Convert document to string if it's a dictionary
        if isinstance(document, dict):
            # Convert dictionary to readable string format
            document_text = ""
            for key, value in document.items():
                if value:  # Only include non-empty values
                    document_text += f"{key}: {value}\n"
            document = document_text

        openai_client = OpenAI(api_key = api_key)
        response = openai_client.embeddings.create(
            model="text-embedding-3-small",
            input=document
        )
        return response.data[0].embedding
    
    def similar_document(self, document,api_key):
        embeddings = self.embedtext(document,api_key)

        extracted_document = self.collection.get(include=["embeddings", "documents"])

        stored_embedding = extracted_document['embeddings']
        stored_docs = extracted_document['documents']

        for doc,emb in zip(stored_docs,stored_embedding):
            sim = cosine_similarity([embeddings],[emb])[0][0]
            return doc
        
        return "No document found"


    def disimilar_document(self,document):

        emebddings = self.embedtext(document)

        extracted_document = self.collection.get(include = ['embeddings', 'documents'])

        stored_embedding = extracted_document['embeddings']
        stored_docs = extracted_document['documents']

        for doc,emb in zip(stored_docs, stored_embedding):
            sim = cosine_similarity() 
