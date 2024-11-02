import os

# Create .streamlit directory if it doesn't exist
os.makedirs('.streamlit', exist_ok=True)

# Write the secrets file with proper encoding
with open('.streamlit/secrets.toml', 'w', encoding='utf-8') as f:
    f.write('OPENAI_API_KEY = "sk-UJ7TOoy0EIdg1B6_vS_NLdYsL65Rfnlubp55zEP-8xT3BlbkFJmhbaYSAeZsTlyKWeMiPBWQnB60OSF9OY_KEpGWIYIA"')
