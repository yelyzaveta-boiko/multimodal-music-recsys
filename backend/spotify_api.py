"""
Spotify helper
──────────────
(artist + song)  ➜  spotify_uri   &   preview_url

Adds noisy console output so you can verify each step.
"""

import os
import base64
import time
import json
from pathlib import Path

import requests
from dotenv import load_dotenv

load_dotenv()
CLIENT_ID     = os.getenv("SPOTIFY_CLIENT_ID")
CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")

# on-disk cache to not spam the API 
CACHE_FILE = Path(__file__).parent / ".spotify_cache.json"
_memory = json.loads(CACHE_FILE.read_text()) if CACHE_FILE.exists() else {}
print(f"[spotify] loaded {len(_memory)} cached tracks from disk")

_token = None        # bearer token
_exp   = 0.0         # expiry epoch-seconds


def _get_token():
    """Return a valid bearer token, refreshing if needed."""
    global _token, _exp

    if _token and time.time() < _exp - 60:
        return _token     # still fresh

    print("[spotify] refreshing access-token …")
    auth_hdr = base64.b64encode(f"{CLIENT_ID}:{CLIENT_SECRET}".encode()).decode()

    resp = requests.post(
        "https://accounts.spotify.com/api/token",
        headers={
            "Authorization": f"Basic {auth_hdr}",
            "Content-Type":  "application/x-www-form-urlencoded",
        },
        data={"grant_type": "client_credentials"},
        timeout=10,
    )
    resp.raise_for_status()
    js = resp.json()
    _token = js["access_token"]
    _exp = time.time() + js["expires_in"]
    print("[spotify] token OK until", time.strftime("%H:%M:%S", time.localtime(_exp)))
    return _token


# enrich every dict with "spotify_uri" and "preview_url"
def enrich(records): 

    headers = {"Authorization": f"Bearer {_get_token()}"}

    for rec in records:
        key = f"{rec['artists']} {rec['name']}".lower()

        if key in _memory:
            print(f"[spotify] cache-hit -> {key}")
        else:
            print(f"[spotify] API query -> {key}")
            query = {"q": key, "type": "track", "limit": 1}
            r = requests.get(
                "https://api.spotify.com/v1/search",
                headers=headers,
                params=query,
                timeout=10,
            )

            if r.ok and r.json()["tracks"]["items"]:
                t = r.json()["tracks"]["items"][0]
                meta = {"spotify_uri": t["uri"], "preview_url": t["preview_url"]}
                print("           -> found", meta["spotify_uri"])
            else:
                meta = {"spotify_uri": None, "preview_url": None}
                print("           -> nothing found")

            _memory[key] = meta
            time.sleep(0.15)

        rec.update(_memory[key])

    try:
        CACHE_FILE.write_text(json.dumps(_memory))
    except Exception as e:
        print("[spotify] WARNING: couldn’t write cache ", e)

    print(f"[spotify] enriched {len(records)} tracks this call")
    return records
