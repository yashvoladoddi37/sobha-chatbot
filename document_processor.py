import chromadb
from chromadb.utils import embedding_functions
from langchain.text_splitter import RecursiveCharacterTextSplitter
import os
from openai import OpenAI
import streamlit as st
from config import Config

def process_documents(directory_path: str):
    try:
        # Check if directory exists
        if not os.path.exists(directory_path):
            raise FileNotFoundError(f"Directory not found: {directory_path}")

        # Get list of document paths
        document_paths = [
            os.path.join(directory_path, f) 
            for f in os.listdir(directory_path) 
            if f.endswith(('.txt', '.md', '.pdf'))
        ]
        
        if not document_paths:
            print(f"No supported documents found in {directory_path}")
            return

        print(f"Found {len(document_paths)} documents to process")

        # Initialize ChromaDB client
        client = chromadb.PersistentClient(path="./chroma_db")
        
        # Initialize OpenAI embedding function
        openai_ef = embedding_functions.OpenAIEmbeddingFunction(
            api_key=Config.OPENAI_API_KEY,
            model_name="text-embedding-ada-002"
        )
        
        # Get or create collection with the embedding function
        collection = client.get_or_create_collection(
            name="sobha_docs",
            embedding_function=openai_ef
        )
        
        # Initialize text splitter
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )
        
        # Process each document
        total_chunks = 0
        for file_path in document_paths:
            print(f"Processing: {file_path}")
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    text = file.read()
                    chunks = text_splitter.split_text(text)
                    
                    # Generate IDs for chunks
                    ids = [f"doc_{os.path.basename(file_path)}_{i}" for i in range(len(chunks))]
                    
                    # Add documents to collection
                    collection.add(
                        documents=chunks,
                        ids=ids,
                        metadatas=[{"source": file_path} for _ in chunks]
                    )
                    
                    total_chunks += len(chunks)
                    print(f"Added {len(chunks)} chunks from {os.path.basename(file_path)}")
                    
            except Exception as e:
                print(f"Error processing file {file_path}: {e}")
                continue
        
        print(f"\nProcessing complete!")
        print(f"Total documents processed: {len(document_paths)}")
        print(f"Total chunks in collection: {total_chunks}")
        
    except Exception as e:
        print(f"Error processing documents: {e}")

if __name__ == "__main__":
    documents_dir = "./documents"
    process_documents(documents_dir)