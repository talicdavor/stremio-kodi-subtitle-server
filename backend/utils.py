import httpx
import logging
from typing import List, Dict, Optional
import asyncio

logger = logging.getLogger(__name__)

# Stremio add-on URLs
STREMIO_ADDONS = {
    'opensubtitles': 'https://opensubtitles-v3.strem.io',
    'submaker': 'https://submaker.elfhosted.com'
}

class StremioSubtitleFetcher:
    """Fetches subtitles from Stremio add-ons"""
    
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=10.0)
    
    async def get_manifest(self, addon_name: str) -> Dict:
        """Fetch manifest from a Stremio add-on"""
        try:
            url = f"{STREMIO_ADDONS.get(addon_name)}/manifest.json"
            response = await self.client.get(url)
            response.raise_for_status()
            logger.info(f"Successfully fetched manifest from {addon_name}")
            return response.json()
        except Exception as e:
            logger.error(f"Error fetching manifest from {addon_name}: {str(e)}")
            return {}
    
    async def search_subtitles(self, addon_name: str, imdb_id: str, languages: Optional[List[str]] = None) -> List[Dict]:
        """Search for subtitles by IMDB ID"""
        try:
            addon_url = STREMIO_ADDONS.get(addon_name)
            search_url = f"{addon_url}/subtitles/movie/{imdb_id}.json"
            response = await self.client.get(search_url)
            response.raise_for_status()
            data = response.json()
            subtitles = data.get('subtitles', {})
            
            if languages:
                filtered_subtitles = {}
                for lang in languages:
                    if lang in subtitles:
                        filtered_subtitles[lang] = subtitles[lang]
                subtitles = filtered_subtitles
            
            logger.info(f"Found {len(subtitles)} subtitle languages for {imdb_id}")
            return subtitles
        
        except Exception as e:
            logger.error(f"Error searching subtitles: {str(e)}")
            return []
    
    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()


async def get_all_subtitles(imdb_id: str, languages: Optional[List[str]] = None) -> Dict:
    """Fetch subtitles from all configured add-ons"""
    fetcher = StremioSubtitleFetcher()
    results = {}
    
    try:
        tasks = [
            fetcher.search_subtitles(addon_name, imdb_id, languages)
            for addon_name in STREMIO_ADDONS.keys()
        ]
        
        addon_results = await asyncio.gather(*tasks)
        
        for addon_name, subtitles in zip(STREMIO_ADDONS.keys(), addon_results):
            results[addon_name] = subtitles
    
    finally:
        await fetcher.close()
    
    return results