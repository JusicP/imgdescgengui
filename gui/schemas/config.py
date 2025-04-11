import json
from pydantic import BaseModel, Field
from enum import Enum

from imgdescgenlib.chatbot.gemini.gemini import GeminiConfig

class ChatbotName(str, Enum):
    GEMINI = "gemini"

class ImgDescGenConfigSchema(BaseModel):
    input_dir: str = ""
    output_dir: str = ""
    selected_images: list[str] | None = None
    exiftool_path: str = ""
    chatbot: str = ChatbotName.GEMINI
    chatbots: dict[str, GeminiConfig] = Field(default_factory=lambda: {
        ChatbotName.GEMINI: GeminiConfig(),
    })

class ImgDescGenConfig():
    def __init__(self, filename):
        self.loadConfig(filename)
        
    def loadConfig(self, filename):
        try:
            with open(filename, "r", encoding="utf-8") as f:
                data = json.load(f)
                self._filename = filename
        except FileNotFoundError:
            ...
            
        if data:
            self._config = ImgDescGenConfigSchema.model_validate(data)
        else:
            self._config = ImgDescGenConfigSchema() # load default cfg

    def getSchema(self) -> ImgDescGenConfigSchema:
        return self._config
    
    def saveConfig(self, filename = None) -> bool:
        try:
            with open(filename if filename else self._filename, "w", encoding="utf-8") as f:
                json.dump(self._config.model_dump(), f, ensure_ascii=False, indent=4)
        except FileNotFoundError:
            return False
        
        return True
