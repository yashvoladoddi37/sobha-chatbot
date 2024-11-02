from langchain.document_loaders import DirectoryLoader, TextLoader
from langchain.text_splitter import MarkdownTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma
import os

def process_markdown_documents():
    # Initialize loader for markdown files
    loader = DirectoryLoader(
        'documents/',
        glob="**/*.md",
        loader_cls=TextLoader
    )
    documents = loader.load()
    
    # Split documents into chunks
    markdown_splitter = MarkdownTextSplitter(
        chunk_size=1000,
        chunk_overlap=100
    )
    splits = markdown_splitter.split_documents(documents)
    
    # Create embeddings and store in ChromaDB
    embedding = OpenAIEmbeddings()
    vectorstore = Chroma.from_documents(
        documents=splits,
        embedding=embedding,
        persist_directory="./chroma_db"
    )
    
    return vectorstore

if __name__ == "__main__":
    vectorstore = process_markdown_documents()
    print(f"Processed {len(vectorstore.get())} document chunks") 