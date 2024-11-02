import streamlit as st
from openai import OpenAI
from gtts import gTTS
from PIL import Image
import tempfile
import os
from pathlib import Path
import base64
from langchain.vectorstores import Chroma
from langchain.embeddings import OpenAIEmbeddings

# Initialize OpenAI client
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# Initialize embeddings and vectorstore globally
embeddings = OpenAIEmbeddings(openai_api_key=st.secrets["OPENAI_API_KEY"])

# Initialize vectorstore if it exists
if os.path.exists("./chroma_db"):
    vectorstore = Chroma(
        persist_directory="./chroma_db",
        embedding_function=embeddings
    )
else:
    st.error("Vector store not found. Please run document_processor.py first!")
    vectorstore = None

def initialize_session_state():
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {
                "role": "assistant", 
                "content": "Namaste! I'm Sobha, your personal assistant for Sobha Indraprastha. How may I help you today?"
            }
        ]
    if "enable_voice" not in st.session_state:
        st.session_state.enable_voice = True

def get_relevant_context(query: str) -> str:
    if vectorstore is None:
        return ""
        
    try:
        # Get relevant documents from vector store
        docs = vectorstore.similarity_search(query, k=3)
        # Combine the content from relevant documents
        context = "\n".join([doc.page_content for doc in docs])
        return context
    except Exception as e:
        st.error(f"Error retrieving context: {str(e)}")
        return ""

def text_to_speech(text):
    tts = gTTS(text=text, lang='en', tld='co.in')  # Indian English accent
    fp = tempfile.NamedTemporaryFile(delete=False)
    tts.save(fp.name)
    return fp.name

def autoplay_audio(file_path):
    with open(file_path, "rb") as f:
        data = f.read()
        b64 = base64.b64encode(data).decode()
        md = f"""
            <audio autoplay>
            <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
            </audio>
            """
        st.markdown(md, unsafe_allow_html=True)

def process_multimodal_input(text_input, files=None):
    try:
        # Get relevant context if there's text input
        context = get_relevant_context(text_input) if text_input else ""
        
        # Construct the messages array
        messages = [
            {
                "role": "system",
                "content": f"""You are Sobha, a warm and friendly assistant for Sobha Indraprastha luxury apartments. 
Remember to:
- Speak naturally and conversationally, as if chatting with a friend
- Use simple, everyday language instead of formal terms
- Include gentle Indian expressions like "namaste" or common Hindi phrases where appropriate
- Show enthusiasm and warmth in your responses
- Break up long responses into smaller, digestible parts

Use this context to answer questions: {context}

If unsure about something, be honest and say "I'm not entirely sure about that, but I'd be happy to check with our property team for you."

Remember to maintain a balance between being professional and friendly."""
            }
        ]
        
        # Add conversation history
        messages.extend([{"role": m["role"], "content": m["content"]} 
                        for m in st.session_state.messages])
        
        # Prepare current input
        if text_input and files:
            # Handle both text and images
            message_content = []
            message_content.append({"type": "text", "text": text_input})
            
            for file in files:
                image_data = base64.b64encode(file.getvalue()).decode()
                message_content.append({
                    "type": "image_url",
                    "image_url": f"data:image/jpeg;base64,{image_data}"
                })
                
            messages.append({"role": "user", "content": message_content})
            
        elif text_input:
            # Handle text-only input
            messages.append({"role": "user", "content": text_input})
            
        elif files:
            # Handle image-only input
            message_content = []
            for file in files:
                image_data = base64.b64encode(file.getvalue()).decode()
                message_content.append({
                    "type": "image_url",
                    "image_url": f"data:image/jpeg;base64,{image_data}"
                })
            message_content.append({"type": "text", "text": "What can you tell me about this image?"})
            messages.append({"role": "user", "content": message_content})
        
        # Get response from OpenAI
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            temperature=0.8,
            max_tokens=500
        )
        
        assistant_response = response.choices[0].message.content
        
        try:
            audio_file = text_to_speech(assistant_response)
        except Exception as e:
            st.warning("Text-to-speech failed, continuing with text only")
            audio_file = None
        
        message_data = {
            "role": "assistant",
            "content": assistant_response
        }
        
        if audio_file:
            message_data["audio"] = audio_file
            
        st.session_state.messages.append(message_data)
        
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        st.session_state.messages.append({
            "role": "assistant",
            "content": "I apologize, but I encountered an error. Please try again or contact support."
        })

def chat_interface():
    st.title("🏢 Sobha Indraprastha Assistant")
    
    # Create a container for the chat messages
    chat_container = st.container()
    
    # Display chat messages in the container
    with chat_container:
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                if isinstance(message["content"], str):
                    st.write(message["content"])
                elif isinstance(message["content"], dict):
                    if "text" in message["content"]:
                        st.write(message["content"]["text"])
                    if "image" in message["content"]:
                        st.image(message["content"]["image"])
                    if "audio" in message["content"] and st.session_state.enable_voice:
                        autoplay_audio(message["content"]["audio"])

    # File uploader - place it above the chat input but below messages
    uploaded_files = st.file_uploader(
        "Attach images (optional)",
        type=["png", "jpg", "jpeg"],
        accept_multiple_files=True,
        key="file_uploader",
        label_visibility="collapsed"
    )

    # Chat input at the bottom
    user_input = st.chat_input("Type your message here...")
    
    # Process input if either text or files are provided
    if user_input or (uploaded_files and len(uploaded_files) > 0):
        # Show user message immediately
        with st.chat_message("user"):
            if user_input:
                st.write(user_input)
            if uploaded_files:
                for file in uploaded_files:
                    st.image(file)
        
        # Process the input and get response
        process_multimodal_input(user_input, uploaded_files)

def main():
    initialize_session_state()
    
    # Sidebar for settings
    with st.sidebar:
        st.header("Settings")
        st.toggle("Enable voice responses", value=True, key="enable_voice")
    
    # Main chat interface
    chat_interface()

if __name__ == "__main__":
    main()