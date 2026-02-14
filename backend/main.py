import logging
from fastapi import FastAPI, HTTPException
import httpx
from cachetools import TTLCache, cached
from typing import List, Optional

# Configure logging
the logging.basicConfig(level=logging.INFO)

app = FastAPI()

# Configuration for add-on URLs
URLS = {
    'OpenSubtitles': 'https://api.opensubtitles.org/',
    'SubMaker': 'https://api.submaker.net/'
}

# Cache for subtitles with a TTL of 10 minutes
cache = TTLCache(maxsize=100, ttl=600)

@cached(cache)
async def fetch_subtitles(imdb_id: str, language: Optional[List[str]] = None):
    search_params = {
        'imdbid': imdb_id,
    }
    # Add language filtering
    if language:
        search_params['language'] = ','.join(language)

    async with httpx.AsyncClient() as client:
        response = await client.get(URLS['OpenSubtitles'] + 'search', params=search_params)
        response.raise_for_status()
        return response.json()

@app.get("/subtitles/{imdb_id}", response_model=List[dict])
async def get_subtitles(imdb_id: str, languages: Optional[List[str]] = None):
    try:
        subtitles = await fetch_subtitles(imdb_id, languages)
        return subtitles
    except HTTPException as e:
        logging.error(f"HTTP error: {e}")
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/manifests")
async def get_manifests():
    manifests = []
    # Logic to fetch manifests from the add-ons would go here
    return manifests
