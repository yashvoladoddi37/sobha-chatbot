import json
import os
from knowledge_base.base_knowledge import SOBHA_KNOWLEDGE
from knowledge_base.facilities import FACILITIES_KNOWLEDGE
from knowledge_base.nearby_services import NEARBY_SERVICES

def dict_to_text(d, prefix=''):
    """Convert a nested dictionary to formatted text"""
    text = []
    for key, value in d.items():
        if isinstance(value, dict):
            text.append(f"{prefix}{key}:")
            text.append(dict_to_text(value, prefix + '  '))
        elif isinstance(value, list):
            text.append(f"{prefix}{key}:")
            for item in value:
                if isinstance(item, dict):
                    text.append(dict_to_text(item, prefix + '  '))
                else:
                    text.append(f"{prefix}  - {item}")
        else:
            text.append(f"{prefix}{key}: {value}")
    return '\n'.join(text)

def save_knowledge_as_docs():
    # Create documents directory if it doesn't exist
    if not os.path.exists("documents"):
        os.makedirs("documents")
    
    # Convert and save base knowledge
    with open("documents/base_knowledge.txt", "w") as f:
        f.write(dict_to_text(SOBHA_KNOWLEDGE))
    
    # Convert and save facilities knowledge
    with open("documents/facilities.txt", "w") as f:
        f.write(dict_to_text(FACILITIES_KNOWLEDGE))
    
    # Convert and save nearby services
    with open("documents/nearby_services.txt", "w") as f:
        f.write(dict_to_text(NEARBY_SERVICES))

if __name__ == "__main__":
    save_knowledge_as_docs() 