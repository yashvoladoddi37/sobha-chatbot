import os
from dataclasses import dataclass

@dataclass
class Config:
    OPENAI_MODEL = "gpt-4o-mini"
    MAX_TOKENS = 500
    TEMPERATURE = 0.8
    MAX_MESSAGES = 50
    VOICE_LANG = 'en'
    VOICE_TLD = 'co.in'
    ALLOWED_IMAGE_TYPES = ["png", "jpg", "jpeg"]
    CHROMA_DB_PATH = "./chroma_db"
    MAX_CONTEXT_DOCS = 3
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
