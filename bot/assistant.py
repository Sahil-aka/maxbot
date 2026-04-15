import re
from bot.tools.weather import get_weather
from bot.tools.stocks import get_stock_price, resolve_ticker
from bot.tools.youtube import search_youtube
from bot.tools.web_search import web_search
from bot.gemini_agent import GeminiAgent

WEATHER_KW = ["weather", "temperature", "forecast", "rain", "sunny", "cloudy", "humidity", "wind speed"]
STOCK_KW = ["stock", "share price", "stock price", "market cap", "trading at", "how much is", "price of"]
YOUTUBE_KW = ["play ", "on youtube", "youtube video", "find video", "watch ", "music video", "song by"]
EMAIL_KW = ["send email", "compose email", "send mail", "write email", "email to", "draft email"]
SEARCH_KW = ["search for", "look up", "google", "find information", "news about", "latest news", "what is", "who is", "how to", "tell me about"]


class Assistant:
    def __init__(self):
        self.gemini = GeminiAgent()

    def process(self, query: str) -> str:
        q = query.lower().strip()

        if any(kw in q for kw in WEATHER_KW):
            city = self._extract_location(q)
            return get_weather(city)

        if any(kw in q for kw in STOCK_KW):
            ticker = resolve_ticker(q)
            return get_stock_price(ticker)

        if any(kw in q for kw in YOUTUBE_KW):
            term = self._extract_youtube_query(q)
            return search_youtube(term)

        if any(kw in q for kw in EMAIL_KW):
            return "EMAIL_MODAL"

        if any(kw in q for kw in SEARCH_KW):
            scraped_data = web_search(query)
            if "❌" in scraped_data:
                return scraped_data 
            
            # Feed the scraped text physically into Gemini to summarize
            prompt = f"System Instruction: The user searched Google. Summarize the following extracted text directly and conversationally for them, as if you searched it yourself. User query: '{query}'\n\nExtracted Web Results:\n{scraped_data}"
            return self.gemini.chat(prompt)

        return self.gemini.chat(query)

    def clear_memory(self):
        self.gemini.clear_history()

    def _extract_location(self, query: str) -> str:
        patterns = [
            r"(?:weather|temperature|forecast)\s+(?:in|at|for|of)\s+([a-zA-Z\s,]+?)(?:\?|$|\.)",
            r"how(?:'s| is)\s+(?:the\s+)?weather\s+(?:in|at)\s+([a-zA-Z\s,]+)",
            r"(?:in|at)\s+([a-zA-Z\s,]+?)\s+(?:weather|temperature)",
        ]
        for pat in patterns:
            m = re.search(pat, query, re.IGNORECASE)
            if m:
                return m.group(1).strip().rstrip("?.,!")
        return "London"

    def _extract_youtube_query(self, query: str) -> str:
        prefixes = ["play ", "watch ", "find video ", "search youtube for ", "on youtube "]
        q = query.lower()
        for p in prefixes:
            if p in q:
                return q.split(p, 1)[-1].strip().rstrip("?.,!")
        return query.strip()
