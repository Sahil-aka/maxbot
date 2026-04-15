from duckduckgo_search import DDGS


def web_search(query: str, max_results: int = 4) -> str:
    query = query.strip()
    if not query:
        return "❌ Please provide a search query."

    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=max_results))

        if not results:
            return f"❌ No results found for **'{query}'**."

        lines = [f"🔍 **Search results for '{query}':**\n"]
        for i, r in enumerate(results, 1):
            title = r.get("title", "No title")
            href = r.get("href", "")
            body = r.get("body", "")[:220]
            lines.append(f"**{i}. {title}**\n{body}...\n🔗 {href}")

        return "\n\n".join(lines)
    except Exception as e:
        return f"❌ Web search error: {str(e)}"
