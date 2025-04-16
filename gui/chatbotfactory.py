from gui.schemas.config import ChatbotName
from imgdescgenlib.chatbot.client_base import ChatbotClientBase
from imgdescgenlib.chatbot.gemini.gemini import GeminiClient, GeminiConfig

def create_chatbot(chatbot_name: str, config) -> ChatbotClientBase:
    """
    Create a chatbot client based on the provided name and configuration.
    """
    if chatbot_name == ChatbotName.GEMINI:
        return GeminiClient(config)
    
    raise ValueError(f"Unknown chatbot name: {chatbot_name}")