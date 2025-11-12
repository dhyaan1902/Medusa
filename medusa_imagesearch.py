# medusa_imagesearch.py
import requests, random, re
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

FALLBACK_SITES = [
    "https://wallhaven.cc/search?q={query}",
    "https://wallpaperaccess.com/search?q={query}",
    "https://www.wallpaperflare.com/search?wallpaper={query}"
]


def get_imagesearch_results(query, count=1):
    """Fetch high-quality wallpaper images using DuckDuckGo (with fallback)."""
    urls = []

    # --- 1️⃣ Try DuckDuckGo image search ---

        # Step 1: Get vqd token
        # --- Improved vqd token extraction ---
    try:
        resp = requests.post(
            "https://duckduckgo.com/",
            data={"q": query},
            headers={
                "User-Agent": HEADERS["User-Agent"],
                "Referer": "https://duckduckgo.com/"
            },
            timeout=10
        )
        text = resp.text

        # Try multiple regex formats (DuckDuckGo changes often)
        match = re.search(r"vqd='([0-9\-]+)'", text)
        if not match:
            match = re.search(r"vqd=([0-9\-]+)\&", text)
        if not match:
            print("[ImageSearch] Could not extract vqd token from DuckDuckGo HTML")
            return []
        else:
            vqd = match.group(1)
    except Exception as e:
        print(f"[ImageSearch] Token fetch error: {e}")
        return []


            # Step 2: Fetch image results as JSON
        res = requests.get(
            "https://duckduckgo.com/i.js",
            params={"l": "us-en", "o": "json", "q": query, "vqd": vqd},
            headers=HEADERS,
            timeout=10
        )
        data = res.json()
        for img in data.get("results", []):
            url = img.get("image")
            if not url:
                continue

                # Filter: only keep large / wallpaper-like images
                title = img.get("title", "").lower()
                if any(x in url.lower() for x in ["thumb", "icon", "logo", "small"]):
                    continue
                if any(x in title for x in ["icon", "logo", "sticker"]):
                    continue
                if any(k in url.lower() for k in ["wallpaper", "1920", "4k", "1080", "background", "wide"]):
                    urls.append(url)

            urls = list(dict.fromkeys(urls))  # dedupe
            random.shuffle(urls)
            if len(urls) >= count:
                return urls[:count]
    except Exception as e:
        print(f"[ImageSearch] DuckDuckGo error: {e}")

    # --- 2️⃣ Fallback: scrape wallpaper sites if DDG fails ---
    try:
        for base in random.sample(FALLBACK_SITES, len(FALLBACK_SITES)):
            try:
                resp = requests.get(base.format(query=query.replace(" ", "+")), headers=HEADERS, timeout=10)
                soup = BeautifulSoup(resp.text, "html.parser")
                imgs = [img.get("src") or img.get("data-src") for img in soup.find_all("img")]
                imgs = [u for u in imgs if u and u.startswith("http") and not u.endswith(".svg")]

                # Prefer large / wallpaper-related URLs
                imgs = [u for u in imgs if any(k in u.lower() for k in ["wallpaper", "1920", "1080", "4k", "wide"])]

                if imgs:
                    urls.extend(imgs)
                    if len(urls) >= count:
                        break
            except Exception as se:
                print(f"[ImageSearch] Fallback site error: {se}")
                continue

        urls = list(dict.fromkeys(urls))
        random.shuffle(urls)
        return urls[:count]
    except Exception as e:
        print(f"[ImageSearch] Error fetching fallback results: {e}")
        return []
