# medusa_core.py
import os
import json
import time
import requests
from datetime import datetime
from PIL import Image
try:
    from medusa_imagesearch import get_imagesearch_results
    HAS_IMAGESEARCH = True
except ImportError:
    HAS_IMAGESEARCH = False

HOME = os.path.expanduser("~")
DEFAULT_WALLDIR = os.path.join(HOME, "Medusa")
CONFIG_FILE = os.path.join(HOME, ".medusa_config.json")
LAST_RUN_FILE = os.path.join(HOME, ".medusa_last_run")
os.makedirs(DEFAULT_WALLDIR, exist_ok=True)

APIS = {
    "Unsplash": {"key": "", "url": "https://api.unsplash.com/photos/random"},
    "Pexels": {"key": "", "url": "https://api.pexels.com/v1/search"},
    "NASA": {"key": "DEMO_KEY", "url": "https://api.nasa.gov/planetary/apod"}
}

DEFAULT_CONFIG = {
    "wall_dir": DEFAULT_WALLDIR,
    "apis": {name: data["key"] for name, data in APIS.items()},
    "queries": [
        {"query": "cyberpunk city 4k", "count": 3, "api": "Pexels"},
        {"query": "space nebula", "count": 2, "api": "Unsplash"}
    ],
    "nuke": True,
    "auto_refresh": False,
    "refresh_hours": 24.0
}

def load_config():
    try:
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, "r") as f:
                cfg = json.load(f)
                for k, v in DEFAULT_CONFIG.items():
                    if k not in cfg:
                        cfg[k] = v
                if "apis" not in cfg:
                    cfg["apis"] = {name: data["key"] for name, data in APIS.items()}
                return cfg
    except Exception:
        pass
    return DEFAULT_CONFIG.copy()

def save_config(cfg):
    try:
        with open(CONFIG_FILE, "w") as f:
            json.dump(cfg, f, indent=2)
    except Exception:
        pass

def _log(msg):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[Medusa] {ts} - {msg}")

def get_image_url(api_name, key, query):
    try:
        if api_name == "Unsplash":
            resp = requests.get(APIS[api_name]["url"], params={
                "client_id": key, "query": query, "orientation": "landscape"
            }, timeout=10)
            data = resp.json()
            if isinstance(data, dict) and data.get("urls"):
                return data["urls"].get("raw") + "&auto=format&fit=crop"
        elif api_name == "Pexels":
            resp = requests.get(APIS[api_name]["url"], headers={"Authorization": key}, params={
                "query": query, "per_page": 1, "page": 1
            }, timeout=10)
            data = resp.json()
            photos = data.get("photos")
            if photos:
                return photos[0]["src"].get("original")
        elif api_name == "NASA":
            resp = requests.get(APIS[api_name]["url"], params={"api_key": key}, timeout=10)
            data = resp.json()
            if data.get("media_type") != "image":
                return None
            return data.get("hdurl") or data.get("url")
       
        elif api_name == "ImageSearch":
            if not HAS_IMAGESEARCH:
                _log("ImageSearch module not found.")
                return None
            urls = get_imagesearch_results(query, count=1)
            if urls:
                return urls[0]

    except Exception as e:
        _log(f"get_image_url error ({api_name}): {e}")
    return None

def save_image(url, src, wall_dir=None):
    if wall_dir is None:
        wall_dir = DEFAULT_WALLDIR
    try:
        r = requests.get(url, timeout=30)
        r.raise_for_status()
        img = r.content
        ext = url.split(".")[-1].split("?")[0]
        if len(ext) > 5 or "/" in ext or len(ext) == 0:
            ext = "jpg"
        fname = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{src[:3]}.{ext}"
        os.makedirs(wall_dir, exist_ok=True)
        path = os.path.join(wall_dir, fname)
        with open(path, "wb") as f:
            f.write(img)
        try:
            Image.open(path).verify()
        except Exception:
            os.remove(path)
            return None
        return path
    except Exception as e:
        _log(f"save_image error: {e}")
    return None

def run_downloads(cfg, show_progress=None):
    wall_dir = cfg.get("wall_dir", DEFAULT_WALLDIR)
    if cfg.get("nuke", False):
        try:
            for f in os.listdir(wall_dir):
                try:
                    os.remove(os.path.join(wall_dir, f))
                except Exception:
                    pass
        except Exception:
            pass
    total = 0
    for q in cfg.get("queries", []):
        try:
            total += int(q.get("count", 0))
        except Exception:
            pass
    if total == 0:
        _log("No images to download (total 0)")
        return []

    downloaded = []
    for q in cfg.get("queries", []):
        query = q.get("query", "").strip()
        try:
            count = int(q.get("count", 0))
        except Exception:
            count = 0
        api_name = q.get("api")
        if not query or count <= 0 or not api_name:
            continue
        key = cfg.get("apis", {}).get(api_name, "").strip()
        if not key and api_name != "ImageSearch":
            _log(f"Skipping {api_name} for '{query}' — no API key")
            continue
        for _ in range(count):
            url = get_image_url(api_name, key, query)
            if url:
                path = save_image(url, api_name, wall_dir=wall_dir)
                if path:
                    downloaded.append(path)
                    if show_progress:
                        try:
                            show_progress(path)
                        except Exception:
                            pass
            time.sleep(0.3)
    _log(f"Downloaded {len(downloaded)}/{total} images")
    try:
        with open(LAST_RUN_FILE, "w") as f:
            f.write(datetime.now().isoformat())
    except Exception:
        pass
    return downloaded
