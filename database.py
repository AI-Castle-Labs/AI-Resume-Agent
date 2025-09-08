

import chromadb
from chromadb.api import ClientAPI
from chromadb.api.models.Collection import Collection
from fastapi import Depends
from dotenv import load_dotenv
import os
import requests
import json
from chromadb.utils import embedding_functions
from main import extend_api

load_dotenv()

_client: ClientAPI | None = None
_collection: Collection | None = None

def get_chroma_client() -> ClientAPI:
	global _client
	if _client is None:
		_client = chromadb.CloudClient(
            api_key=os.getenv("CHROMA_API_KEY"),
            tenant=os.getenv("CHROMA_TENANT"),
            database=os.getenv("CHROMA_DATABASE")
        )
	return _client

    




def get_chroma_collection(client: ClientAPI = Depends(get_chroma_client)) -> Collection:
    global _collection
    if _collection is None:
        # Using OpenAI embeddings
        openai_ef = embedding_functions.OpenAIEmbeddingFunction(
            api_key=os.getenv("OPENAI_API_KEY"),
            model_name="text-embedding-ada-002"
        )
        
        _collection = client.get_or_create_collection(
            name="resume_documents",
            embedding_function=openai_ef
        )
    return _collection

def get_extend_document(processor_id: str):
    """Retrieve document from Extend AI"""
    url = "https://api.extend.ai/processor_runs"
    headers = {
        "x-extend-api-version": "2025-04-21",
        "Authorization": f"Bearer {os.getenv('EXTEND_API_KEY')}",
        "Content-Type": "application/json",
    }
    
    payload = {
        "processorId": processor_id,
        "sync": True
    }
    
    response = requests.post(url, json=payload, headers=headers)
    return response.json()

def get_next_document_id():
    """Get the next available numeric ID for documents"""
    try:
        collection = get_chroma_collection(get_chroma_client())

        # Get all existing IDs
        existing_docs = collection.get(include=[])
        existing_ids = existing_docs['ids']

        if not existing_ids:
            return 1  # First document

        # Extract numeric IDs and find the maximum
        numeric_ids = []
        for doc_id in existing_ids:
            try:
                # Try to convert to int, skip non-numeric IDs
                numeric_id = int(doc_id)
                numeric_ids.append(numeric_id)
            except (ValueError, TypeError):
                continue

        if numeric_ids:
            return max(numeric_ids) + 1
        else:
            return 1

    except Exception as e:
        print(f"Error getting next document ID: {str(e)}")
        return 1

def add_extend_document_with_auto_id(processor_id: str, overwrite_existing: bool = False):
    """Add Extend AI document to ChromaDB with auto-incrementing numeric ID"""
    # Get next available numeric ID
    doc_id = get_next_document_id()

    # Get ChromaDB collection
    collection = get_chroma_collection(get_chroma_client())

    # Check if we're trying to add the same processor_id again
    # Search for existing documents with this processor_id in metadata
    existing_docs = collection.get(
        where={"processor_id": processor_id},
        include=["metadatas"]
    )

    if existing_docs['ids']:
        existing_id = existing_docs['ids'][0]
        if overwrite_existing:
            print(f"Updating existing document (ID: {existing_id}) for processor: {processor_id}")
            collection.delete(ids=[existing_id])
        else:
            print(f"Document for processor {processor_id} already exists (ID: {existing_id}). Use overwrite_existing=True to update.")
            return False

    # Get document from Extend AI
    doc_data = extend_api(processor_id)
    print(f"Retrieved document for processor ID: {processor_id}")

    # Process the document data
    doc_text = json.dumps(doc_data) if isinstance(doc_data, dict) else str(doc_data)

    # Add to ChromaDB with numeric ID
    collection.add(
        documents=[doc_text],
        metadatas=[{
            "source": "extend_ai",
            "processor_id": processor_id,
            "document_id": doc_id,
            "last_updated": str(os.getenv('CURRENT_TIME', 'unknown'))
        }],
        ids=[str(doc_id)]  # Convert to string for ChromaDB
    )

    print(f"Successfully added document with processor ID {processor_id} as document ID {doc_id} to ChromaDB")
    return True


print()
