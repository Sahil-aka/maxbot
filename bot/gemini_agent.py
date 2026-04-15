import os
import logging
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are MAX, a friendly, witty, and intelligent voice assistant.
Keep responses concise (2-4 sentences) and conversational — you're speaking to a person.
You can check weather, stock prices, play YouTube videos, search the web, and send emails via the interface.
If asked about yourself, say you are MAX, an AI assistant built with Python, Flask, and Google Gemini."""


class GeminiAgent:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not set in .env file.")
        self._setup(api_key)

    def _setup(self, api_key: str):
        try:
            from langchain_google_genai import ChatGoogleGenerativeAI
            from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
            self._HumanMessage = HumanMessage
            self._SystemMessage = SystemMessage
            self._AIMessage = AIMessage
            self.llm = ChatGoogleGenerativeAI(
                model="gemini-2.5-flash",
                google_api_key=api_key,
                temperature=0.7,
                convert_system_message_to_human=True,
            )
            self.history = []
            self._available = True
            logger.info("Gemini LangChain agent initialized.")
        except Exception as e:
            logger.error(f"Gemini init failed: {e}")
            self._available = False

    def chat(self, message: str) -> str:
        if not self._available:
            return "⚠️ Gemini AI is not available. Please check your GEMINI_API_KEY."
        try:
            messages = [self._SystemMessage(content=SYSTEM_PROMPT)]
            messages.extend(self.history[-10:])  # last 5 exchanges
            messages.append(self._HumanMessage(content=message))

            response = self.llm.invoke(messages)
            result = response.content

            self.history.append(self._HumanMessage(content=message))
            self.history.append(self._AIMessage(content=result))
            if len(self.history) > 20:
                self.history = self.history[-20:]

            return result
        except Exception as e:
            logger.error(f"Gemini chat error: {e}")
            return f"⚠️ Gemini error: {str(e)}"

    def clear_history(self):
        self.history = []
