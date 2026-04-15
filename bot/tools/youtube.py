import urllib.request
import urllib.parse
import re
import json

def search_youtube(query: str) -> str:
    query = query.strip().rstrip("?.,!")
    if not query:
        return "❌ Please provide a search term for YouTube."

    try:
        encoded_query = urllib.parse.quote(query)
        req = urllib.request.Request(
            f"https://www.youtube.com/results?search_query={encoded_query}",
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        )
        html = urllib.request.urlopen(req).read().decode('utf-8')
        
        # Extract ytInitialData
        match = re.search(r"var ytInitialData = ({.*?});</script>", html)
        if match:
            data = json.loads(match.group(1))
            try:
                results = []
                contents = data['contents']['twoColumnSearchResultsRenderer']['primaryContents']['sectionListRenderer']['contents'][0]['itemSectionRenderer']['contents']
                for item in contents:
                    if 'videoRenderer' in item:
                        video = item['videoRenderer']
                        vid = video['videoId']
                        title = video['title']['runs'][0]['text']
                        url = f"https://www.youtube.com/watch?v={vid}"
                        thumbnail = f"https://i.ytimg.com/vi/{vid}/hqdefault.jpg"
                        channel = video.get('ownerText', {}).get('runs', [{}])[0].get('text', 'YouTube')
                        results.append({
                            "title": title,
                            "channel": channel,
                            "url": url,
                            "thumbnail": thumbnail,
                            "id": vid
                        })
                        if len(results) >= 5:
                            break
                            
                if results:
                    return f"YOUTUBE_GALLERY|{json.dumps(results)}"
            except KeyError:
                pass
                
        # Fallback regex if generic structure fails
        video_ids = list(dict.fromkeys(re.findall(r"watch\?v=(\S{11})", html)))
        if not video_ids:
            return f"❌ No YouTube results found for **'{query}'**."
            
        results = []
        for vid in video_ids[:5]:
            url = f"https://www.youtube.com/watch?v={vid}"
            thumbnail = f"https://i.ytimg.com/vi/{vid}/hqdefault.jpg"
            results.append({
                "title": f"YouTube Video",
                "channel": "YouTube",
                "url": url,
                "thumbnail": thumbnail,
                "id": vid
            })
            
        return f"YOUTUBE_GALLERY|{json.dumps(results)}"

    except Exception as e:
        return f"❌ YouTube search error: {str(e)}"
