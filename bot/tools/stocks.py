import yfinance as yf


STOCK_MAP = {
    "apple": "AAPL", "google": "GOOGL", "alphabet": "GOOGL",
    "microsoft": "MSFT", "amazon": "AMZN", "tesla": "TSLA",
    "meta": "META", "facebook": "META", "netflix": "NFLX",
    "nvidia": "NVDA", "amd": "AMD", "intel": "INTC",
    "reliance": "RELIANCE.NS", "tcs": "TCS.NS", "infosys": "INFY.NS",
    "hdfc": "HDFCBANK.NS", "icici": "ICICIBANK.NS", "wipro": "WIPRO.NS",
}


def get_stock_price(ticker: str) -> str:
    ticker = ticker.strip().upper()
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period="2d")

        if hist.empty:
            return f"Could not find stock data for **'{ticker}'**. Check the ticker symbol."

        current = hist["Close"].iloc[-1]
        prev_close = hist["Close"].iloc[-2] if len(hist) >= 2 else hist["Open"].iloc[-1]
        change = current - prev_close
        change_pct = (change / prev_close) * 100

        info = stock.info
        name = info.get("longName", ticker)
        currency = info.get("currency", "USD")
        market_cap = info.get("marketCap", 0)
        volume = info.get("volume", 0)

        arrow = "▲" if change >= 0 else "▼"
        color_tag = "📈" if change >= 0 else "📉"

        cap_str = ""
        if market_cap:
            if market_cap >= 1e12:
                cap_str = f"\n💰 Market Cap: ${market_cap/1e12:.2f}T"
            elif market_cap >= 1e9:
                cap_str = f"\n💰 Market Cap: ${market_cap/1e9:.2f}B"

        vol_str = f"\n📊 Volume: {volume:,}" if volume else ""

        return (
            f"{color_tag} **{name} ({ticker})**\n"
            f"💵 Price: **{currency} {current:.2f}** "
            f"{arrow} {abs(change):.2f} ({abs(change_pct):.2f}%)"
            f"{cap_str}{vol_str}"
        )
    except Exception as e:
        return f"❌ Error fetching stock data for '{ticker}': {str(e)}"


def resolve_ticker(query: str) -> str:
    q = query.lower()
    for name, ticker in STOCK_MAP.items():
        if name in q:
            return ticker
    # Look for uppercase ticker-like word
    for word in query.split():
        w = word.strip(".,?!").upper()
        if 1 <= len(w) <= 5 and w.isalpha():
            return w
    return "AAPL"
