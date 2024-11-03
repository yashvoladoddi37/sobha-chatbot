import chromadb
from chromadb.config import Settings
import sqlite3
import os

def vacuum_chroma_db():
    try:
        # Path to your ChromaDB directory
        db_path = "./chroma_db"
        
        # Path to the SQLite database file within ChromaDB directory
        sqlite_path = os.path.join(db_path, "chroma.sqlite3")
        
        if os.path.exists(sqlite_path):
            print("Found SQLite database, performing vacuum...")
            
            # Connect to the SQLite database
            conn = sqlite3.connect(sqlite_path)
            
            # Perform vacuum
            conn.execute("VACUUM")
            conn.close()
            
            print("Vacuum completed successfully!")
        else:
            print(f"SQLite database not found at {sqlite_path}")
            
        # Reinitialize ChromaDB client
        client = chromadb.Client(Settings(
            chroma_db_impl="duckdb+parquet",
            persist_directory=db_path,
            anonymized_telemetry=False  # Disable telemetry if desired
        ))
        
        print("ChromaDB reinitialized successfully!")
        
    except Exception as e:
        print(f"Error during vacuum process: {e}")

if __name__ == "__main__":
    vacuum_chroma_db() 