import chromadb
from chromadb.utils import embedding_functions
import streamlit as st

def test_queries():
    # Initialize ChromaDB client
    client = chromadb.PersistentClient(path="./chroma_db")
    
    # Initialize embedding function
    embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name="all-MiniLM-L6-v2"
    )
    
    # Get collection
    collection = client.get_collection(
        name="sobha_docs",
        embedding_function=embedding_function
    )

    # Test queries
    test_questions = [
        "What amenities are available?",
        "Tell me about the floor plans",
        "What maintenance services are offered?",
        "What are the community guidelines?"
    ]

    print("\nTesting Vector Store Queries:")
    print("=" * 50)
    
    for question in test_questions:
        print(f"\nQuery: {question}")
        results = collection.query(
            query_texts=[question],
            n_results=1
        )
        if results and results['documents']:
            print(f"Found relevant content: {results['documents'][0][0][:200]}...")

if __name__ == "__main__":
    test_queries() 