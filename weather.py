#from fastmcp import FastMCP
from mcp.server.fastmcp import FastMCP
import time
import os
import json
from pathlib import Path
from typing import Dict, Optional
from fastmcp import FastMCP
from dotenv import load_dotenv
from aiohttp import ClientSession
# Create an MCP server

# Load environment variables
load_dotenv()

mcp = FastMCP(
    name="Weather",
    host="127.0.0.1",
    port=5001,
    timeout=30
)


# Cache configuration
CACHE_DIR = Path.home() / ".cache" / "weather"
LOCATION_CACHE_FILE = CACHE_DIR / "location_cache.json"

def get_cached_location_key(location: str) -> Optional[str]:
    """Get location key from cache."""
    if not LOCATION_CACHE_FILE.exists():
        return None
    
    try:
        with open(LOCATION_CACHE_FILE, "r") as f:
            cache = json.load(f)
            return cache.get(location)
    except (json.JSONDecodeError, FileNotFoundError):
        return None

def cache_location_key(location: str, location_key: str):
    """Cache location key for future use."""
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    
    try:
        if LOCATION_CACHE_FILE.exists():
            with open(LOCATION_CACHE_FILE, "r") as f:
                cache = json.load(f)
        else:
            cache = {}
        
        cache[location] = location_key
        
        with open(LOCATION_CACHE_FILE, "w") as f:
            json.dump(cache, f, indent=2)
    except Exception as e:
        print(f"Warning: Failed to cache location key: {e}")

def format_current_conditions(current_data: dict) -> dict:
    return {
        "current_conditions": {
            "observation_time": current_data["LocalObservationDateTime"],
            "is_daytime": current_data["IsDayTime"],
            "weather_text": current_data["WeatherText"],
            "temperature_c": current_data["Temperature"]["Metric"]["Value"],
            "temperature_f": current_data["Temperature"]["Imperial"]["Value"],
            "weather_icon": current_data["WeatherIcon"],
            "has_precipitation": current_data["HasPrecipitation"],
            "precipitation_type": current_data["PrecipitationType"],
            "link": current_data["Link"]
        }
    }

@mcp.tool(description="Get hourly weather forecast for a location")
async def get_hourly_weather(location: str) -> Dict:
    """Get hourly weather forecast for a location."""
    api_key = os.getenv("ACCUWEATHER_API_KEY")
    base_url = "http://dataservice.accuweather.com"
    print(f"api_key: {api_key}")
    # Try to get location key from cache first
    location_key = get_cached_location_key(location)
    
    async with ClientSession() as session:
        if not location_key:
            location_search_url = f"{base_url}/locations/v1/cities/search"
            params = {
                "apikey": api_key,
                "q": location,
            }
            async with session.get(location_search_url, params=params) as response:
                locations = await response.json()
                if response.status != 200:
                    raise Exception(f"Error fetching location data: {response.status}, {locations}")
                if not locations or len(locations) == 0:
                    raise Exception("Location not found")
            
            location_key = locations[0]["Key"]
            # Cache the location key for future use
            cache_location_key(location, location_key)
        
        # Get current conditions
        current_conditions_url = f"{base_url}/currentconditions/v1/{location_key}"
        params = {
            "apikey": api_key,
        }
        async with session.get(current_conditions_url, params=params) as response:
            current_conditions = await response.json()
        
        return(format_current_conditions(current_conditions[0]))
    

if __name__ == "__main__":
    try:
        print("Starting MCP server add on 127.0.0.1:5001")
        mcp.run(transport="sse")
    except Exception as e:
        print(f"Error: {e}")
        time.sleep (2)