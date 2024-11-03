from typing import Dict, List, Optional, Union
from dataclasses import dataclass
import base64
from config import Config

@dataclass
class Message:
    role: str
    content: Union[str, Dict, List]
    audio: Optional[str] = None

class MessageHandler:
    def __init__(self):
        self.messages: List[Message] = []
        self.max_messages = Config.MAX_MESSAGES

    def add_message(self, message: Message) -> None:
        self.messages.append(message)
        self._trim_messages()

    def _trim_messages(self) -> None:
        if len(self.messages) > self.max_messages:
            self.messages = self.messages[-self.max_messages:]

    def get_openai_messages(self, system_prompt: str) -> List[Dict]:
        messages = [{"role": "system", "content": system_prompt}]
        messages.extend([{"role": m.role, "content": m.content} for m in self.messages])
        return messages

    @staticmethod
    def prepare_image_content(file) -> Dict:
        image_data = base64.b64encode(file.getvalue()).decode()
        return {
            "type": "image_url",
            "image_url": f"data:image/jpeg;base64,{image_data}"
        } 