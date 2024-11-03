from typing import Dict, List, Optional, Union
import streamlit as st
from openai import OpenAI
import logging
from config import Config
from message_handler import MessageHandler, Message
from voice_handler import VoiceHandler
# from langchain_chroma import Chroma # type: ignore
from langchain_openai import OpenAIEmbeddings # type: ignore
import base64
import os
import chromadb
from chromadb.config import Settings
from langchain_chroma import Chroma

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ChatApp:
    def __init__(self):
        self.client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
        self.embeddings = OpenAIEmbeddings(openai_api_key=st.secrets["OPENAI_API_KEY"])
        self.message_handler = MessageHandler()
        self.voice_handler = VoiceHandler()
        self.initialize_vectorstore()
        self.initialize_session_state()

    def initialize_vectorstore(self):
        try:
            if os.path.exists(Config.CHROMA_DB_PATH):
                # Initialize ChromaDB client
                chroma_client = chromadb.PersistentClient(
                    path=Config.CHROMA_DB_PATH
                )
                
                # Initialize Langchain's Chroma wrapper
                self.vectorstore = Chroma(
                    embedding_function=self.embeddings,
                    persist_directory=Config.CHROMA_DB_PATH,
                    collection_name="sobha_docs"
                )
            else:
                st.error("Vector store not found. Please run init_chroma.py first!")
                self.vectorstore = None
        except Exception as e:
            logger.error(f"Error initializing vectorstore: {e}")
            self.vectorstore = None

    @staticmethod
    def initialize_session_state():
        if "messages" not in st.session_state:
            st.session_state.messages = []
        st.session_state.enable_voice = True  # Set default value without UI control

    def get_relevant_context(self, query: str) -> str:
        if not self.vectorstore:
            return ""
        
        try:
            docs = self.vectorstore.similarity_search(query, k=Config.MAX_CONTEXT_DOCS)
            return "\n".join([doc.page_content for doc in docs])
        except Exception as e:
            logger.error(f"Error retrieving context: {e}")
            return ""

    def process_response(self, response_text: str) -> Dict:
        message_data = {"role": "assistant", "content": response_text}
        
        if st.session_state.enable_voice:
            try:
                audio_file = self.voice_handler.text_to_speech(response_text)
                message_data["audio"] = audio_file
            except Exception as e:
                logger.error(f"Text-to-speech failed: {e}")
                st.warning("Voice response generation failed")

        return message_data

    def render_chat_interface(self):
        st.title("🏢 Sobha Indraprastha Assistant")
        
        # Display chat history
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.write(message["content"])
        
        # File uploader
        uploaded_files = st.file_uploader(
            "Attach images (optional)",
            type=Config.ALLOWED_IMAGE_TYPES,
            accept_multiple_files=True,
            key="file_uploader",
            label_visibility="collapsed"
        )

        # Chat input
        if user_input := st.chat_input("Type your message here..."):
            self.handle_user_input(user_input, uploaded_files)

    def handle_user_input(self, user_input: str, uploaded_files: List = None):
        # Add debug logging
        logger.info(f"Received user input: {user_input}")
        
        if not user_input and not uploaded_files:
            return

        # Display user message immediately
        with st.chat_message("user"):
            st.write(user_input)

        # Prepare user message
        user_message = {"role": "user", "content": user_input}
        if uploaded_files:
            user_message["content"] = {
                "text": user_input or "Image uploaded",
                "image": uploaded_files[0]
            }

        # Add user message to session state
        st.session_state.messages.append(user_message)

        # Show a spinner while processing
        with st.spinner("Thinking..."):
            try:
                # Get context from RAG system
                context = self.get_relevant_context(user_input) if user_input else ""
                
                system_prompt = f"""You are Sobha, a helpful and knowledgeable assistant for Sobha Indraprastha property. 
                You have a warm, professional demeanor and speak with an Indian English accent. 
                Your responses should be:
                1. Accurate and based on the provided context
                2. Professional yet friendly
                3. Concise but complete
                4. Safety-conscious when discussing facilities
                5. Always prioritizing resident comfort and security

                Context for this conversation: {context}

                If you don't find relevant information in the context, politely acknowledge that and offer to forward the query to the management team."""

                # Prepare messages for API call
                messages = [
                    {"role": "system", "content": system_prompt},
                    *[{"role": m["role"], "content": m["content"]} 
                      for m in st.session_state.messages[-10:]]
                ]

                # Make API call
                response = self.client.chat.completions.create(
                    model=Config.OPENAI_MODEL,
                    messages=messages,
                    temperature=Config.TEMPERATURE,
                    max_tokens=Config.MAX_TOKENS
                )

                # Extract response text
                response_text = response.choices[0].message.content

                # Simplified response handling without audio
                response_message = {"role": "assistant", "content": response_text}
                st.session_state.messages.append(response_message)

                # Make the response visible immediately
                with st.chat_message("assistant"):
                    st.write(response_text)

            except Exception as e:
                logger.error(f"Error processing message: {e}")
                st.error("Sorry, I encountered an error processing your request.")

    def handle_voice_input(self):
        try:
            audio_file = self.voice_handler.record_audio()
            if audio_file:
                text = self.voice_handler.speech_to_text(audio_file)
                if text:
                    self.handle_user_input(text)
                else:
                    st.warning("Could not understand the audio. Please try again.")
        except Exception as e:
            logger.error(f"Error processing voice input: {e}")
            st.error("Error processing voice input. Please try again.")

    def run(self):
        with st.sidebar:
            st.header("Settings")
            st.toggle("Enable voice responses", value=True, key="enable_voice")
        
        self.render_chat_interface()

        # Cleanup temporary files at the end of the session
        self.voice_handler.cleanup()

if __name__ == "__main__":
    app = ChatApp()
    app.run()