import shutil
import os

def cleanup_chroma():
    db_path = "./chroma_db"
    if os.path.exists(db_path):
        shutil.rmtree(db_path)
        print(f"Removed {db_path}")
    else:
        print(f"{db_path} does not exist")

if __name__ == "__main__":
    cleanup_chroma() 