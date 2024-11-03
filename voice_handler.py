from gtts import gTTS
import tempfile
import os
from config import Config

class VoiceHandler:
    def __init__(self):
        self.temp_files = []

    def text_to_speech(self, text: str) -> str:
        tts = gTTS(text=text, lang=Config.VOICE_LANG, tld=Config.VOICE_TLD)
        fp = tempfile.NamedTemporaryFile(delete=False)
        tts.save(fp.name)
        self.temp_files.append(fp.name)
        return fp.name

    def cleanup(self) -> None:
        for file in self.temp_files:
            try:
                os.remove(file)
            except Exception:
                continue
        self.temp_files = [] 