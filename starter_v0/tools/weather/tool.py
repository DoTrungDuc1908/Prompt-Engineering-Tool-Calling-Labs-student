from __future__ import annotations

from typing import Any

import requests

from tools._shared import err


def get_weather(latitude: float = 0.0, longitude: float = 0.0) -> dict[str, Any]:
    try:
        resp = requests.get(
            "https://api.open-meteo.com/v1/forecast",
            params={
                "latitude": latitude,
                "longitude": longitude,
                "current": "temperature_2m,relative_humidity_2m,weather_code,wind_speed_10m",
            },
            timeout=15,
        )
        resp.raise_for_status()
        data = resp.json()
        current = data.get("current", {})
        weather_codes = {
            0: "Clear sky", 1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
            45: "Fog", 48: "Depositing rime fog",
            51: "Light drizzle", 53: "Moderate drizzle", 55: "Dense drizzle",
            61: "Slight rain", 63: "Moderate rain", 65: "Heavy rain",
            71: "Slight snowfall", 73: "Moderate snowfall", 75: "Heavy snowfall",
            80: "Slight rain showers", 81: "Moderate rain showers", 82: "Violent rain showers",
            95: "Thunderstorm", 96: "Thunderstorm with slight hail", 99: "Thunderstorm with heavy hail",
        }
        code = current.get("weather_code", 0)
        return {"tool": "get_weather", "items": [{
            "latitude": latitude,
            "longitude": longitude,
            "temperature_c": current.get("temperature_2m"),
            "humidity": current.get("relative_humidity_2m"),
            "weather": weather_codes.get(code, f"Code {code}"),
            "wind_speed": current.get("wind_speed_10m"),
            "source": "open-meteo.com",
        }]}
    except Exception as exc:
        return err("get_weather", exc)
