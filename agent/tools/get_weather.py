import requests


def get_weather(location: str) -> dict:
    """Get the current weather in a location.

    Uses the Open-Meteo API (no API key required).
    First resolves the location name to coordinates via geocoding,
    then fetches the current weather.
    """
    # Step 1: Geocode the location name to latitude/longitude
    geo_url = "https://geocoding-api.open-meteo.com/v1/search"
    geo_resp = requests.get(
        geo_url,
        params={"name": location, "count": 1, "language": "en"},
        timeout=10,
    )
    geo_resp.raise_for_status()
    geo_data = geo_resp.json()

    results = geo_data.get("results")
    if not results:
        return {"error": f"Location '{location}' not found"}

    place = results[0]
    latitude = place["latitude"]
    longitude = place["longitude"]
    resolved_name = place.get("name", location)
    country = place.get("country", "")

    # Step 2: Fetch current weather
    weather_url = "https://api.open-meteo.com/v1/forecast"
    weather_resp = requests.get(
        weather_url,
        params={
            "latitude": latitude,
            "longitude": longitude,
            "current": "temperature_2m,relative_humidity_2m,weather_code,wind_speed_10m",
        },
        timeout=10,
    )
    weather_resp.raise_for_status()
    weather_data = weather_resp.json()

    current = weather_data.get("current", {})
    return {
        "location": resolved_name,
        "country": country,
        "latitude": latitude,
        "longitude": longitude,
        "temperature": current.get("temperature_2m"),
        "temperature_unit": "°C",
        "humidity": current.get("relative_humidity_2m"),
        "humidity_unit": "%",
        "weather_code": current.get("weather_code"),
        "wind_speed": current.get("wind_speed_10m"),
        "wind_speed_unit": "km/h",
    }
