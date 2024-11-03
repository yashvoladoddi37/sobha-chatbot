import chromadb
from chromadb.config import Settings
from langchain_openai import OpenAIEmbeddings
import streamlit as st
import shutil
import os

def clean_existing_db():
    db_path = "./chroma_db"
    if os.path.exists(db_path):
        shutil.rmtree(db_path)
        print(f"Removed existing database at {db_path}")

def init_chroma():
    try:
        # Clean existing DB
        clean_existing_db()
        
        # Initialize with new client configuration
        client = chromadb.PersistentClient(
            path="./chroma_db"
        )

        # Create a new collection
        collection = client.create_collection(
            name="sobha_docs",
            metadata={"hnsw:space": "cosine"}  # Using cosine similarity
        )

        print("Successfully initialized new ChromaDB!")
        print(f"Created collection: {collection.name}")
        return client

    except Exception as e:
        print(f"Error initializing ChromaDB: {e}")
        return None

if __name__ == "__main__":
    init_chroma() 