"""
Weather API Integration Module

This module provides integration with weather data APIs for the Open Manus AI system.
"""

import os
import logging
import requests
from datetime import datetime
from dotenv import load_dotenv

# Configure logging
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

class WeatherAPI:
    """
    Weather API integration for accessing weather data and forecasts.
    """
    
    def __init__(self):
        """Initialize the Weather API integration."""
        self.openweather_key = os.getenv("OPENWEATHER_API_KEY")
        
        if not self.openweather_key:
            logger.warning("OpenWeather API key not found in environment variables")
        else:
            logger.info("Weather API integration initialized successfully")
    
    def get_current_weather(self, location, units="metric"):
        """
        Get current weather data for a location.
        
        Args:
            location (str): City name or coordinates (lat,lon)
            units (str, optional): Units of measurement (metric, imperial, standard)
            
        Returns:
            dict: Current weather data
        """
        try:
            if not self.openweather_key:
                return {"success": False, "error": "OpenWeather API key not configured"}
            
            # Determine if location is coordinates or city name
            if "," in location and all(part.replace("-", "").replace(".", "").isdigit() for part in location.split(",")):
                # Location is coordinates
                lat, lon = location.split(",")
                url = f"https://api.openweathermap.org/data/2.5/weather"
                params = {
                    "lat": lat.strip(),
                    "lon": lon.strip(),
                    "units": units,
                    "appid": self.openweather_key
                }
            else:
                # Location is city name
                url = f"https://api.openweathermap.org/data/2.5/weather"
                params = {
                    "q": location,
                    "units": units,
                    "appid": self.openweather_key
                }
            
            # Make API request
            response = requests.get(url, params=params)
            data = response.json()
            
            # Check for error
            if data.get("cod") != 200:
                return {"success": False, "error": data.get("message", "Unknown error")}
            
            # Process and format the data
            weather_data = {
                "location": {
                    "name": data.get("name", ""),
                    "country": data.get("sys", {}).get("country", ""),
                    "coordinates": {
                        "lat": data.get("coord", {}).get("lat", 0),
                        "lon": data.get("coord", {}).get("lon", 0)
                    }
                },
                "weather": {
                    "condition": data.get("weather", [{}])[0].get("main", ""),
                    "description": data.get("weather", [{}])[0].get("description", ""),
                    "icon": data.get("weather", [{}])[0].get("icon", ""),
                    "temperature": {
                        "current": data.get("main", {}).get("temp", 0),
                        "feels_like": data.get("main", {}).get("feels_like", 0),
                        "min": data.get("main", {}).get("temp_min", 0),
                        "max": data.get("main", {}).get("temp_max", 0)
                    },
                    "humidity": data.get("main", {}).get("humidity", 0),
                    "pressure": data.get("main", {}).get("pressure", 0),
                    "wind": {
                        "speed": data.get("wind", {}).get("speed", 0),
                        "direction": data.get("wind", {}).get("deg", 0)
                    },
                    "clouds": data.get("clouds", {}).get("all", 0),
                    "visibility": data.get("visibility", 0),
                    "sunrise": datetime.fromtimestamp(data.get("sys", {}).get("sunrise", 0)).isoformat(),
                    "sunset": datetime.fromtimestamp(data.get("sys", {}).get("sunset", 0)).isoformat()
                },
                "units": units,
                "timestamp": datetime.now().isoformat()
            }
            
            return {
                "weather_data": weather_data,
                "raw_data": data,
                "success": True
            }
            
        except Exception as e:
            logger.error(f"Error retrieving current weather for {location}: {e}")
            return {"success": False, "error": str(e)}
    
    def get_weather_forecast(self, location, units="metric", days=5):
        """
        Get weather forecast for a location.
        
        Args:
            location (str): City name or coordinates (lat,lon)
            units (str, optional): Units of measurement (metric, imperial, standard)
            days (int, optional): Number of days for forecast (max 5)
            
        Returns:
            dict: Weather forecast data
        """
        try:
            if not self.openweather_key:
                return {"success": False, "error": "OpenWeather API key not configured"}
            
            # Determine if location is coordinates or city name
            if "," in location and all(part.replace("-", "").replace(".", "").isdigit() for part in location.split(",")):
                # Location is coordinates
                lat, lon = location.split(",")
                url = f"https://api.openweathermap.org/data/2.5/forecast"
                params = {
                    "lat": lat.strip(),
                    "lon": lon.strip(),
                    "units": units,
                    "appid": self.openweather_key
                }
            else:
                # Location is city name
                url = f"https://api.openweathermap.org/data/2.5/forecast"
                params = {
                    "q": location,
                    "units": units,
                    "appid": self.openweather_key
                }
            
            # Make API request
            response = requests.get(url, params=params)
            data = response.json()
            
            # Check for error
            if data.get("cod") != "200":
                return {"success": False, "error": data.get("message", "Unknown error")}
            
            # Process and format the data
            location_data = {
                "name": data.get("city", {}).get("name", ""),
                "country": data.get("city", {}).get("country", ""),
                "coordinates": {
                    "lat": data.get("city", {}).get("coord", {}).get("lat", 0),
                    "lon": data.get("city", {}).get("coord", {}).get("lon", 0)
                }
            }
            
            # Group forecast by day
            forecast_by_day = {}
            for item in data.get("list", []):
                dt = datetime.fromtimestamp(item.get("dt", 0))
                day_key = dt.strftime("%Y-%m-%d")
                
                if day_key not in forecast_by_day:
                    forecast_by_day[day_key] = []
                
                forecast_item = {
                    "datetime": dt.isoformat(),
                    "temperature": {
                        "current": item.get("main", {}).get("temp", 0),
                        "feels_like": item.get("main", {}).get("feels_like", 0),
                        "min": item.get("main", {}).get("temp_min", 0),
                        "max": item.get("main", {}).get("temp_max", 0)
                    },
                    "weather": {
                        "condition": item.get("weather", [{}])[0].get("main", ""),
                        "description": item.get("weather", [{}])[0].get("description", ""),
                        "icon": item.get("weather", [{}])[0].get("icon", "")
                    },
                    "humidity": item.get("main", {}).get("humidity", 0),
                    "pressure": item.get("main", {}).get("pressure", 0),
                    "wind": {
                        "speed": item.get("wind", {}).get("speed", 0),
                        "direction": item.get("wind", {}).get("deg", 0)
                    },
                    "clouds": item.get("clouds", {}).get("all", 0),
                    "precipitation": {
                        "probability": item.get("pop", 0),
                        "rain": item.get("rain", {}).get("3h", 0),
                        "snow": item.get("snow", {}).get("3h", 0)
                    }
                }
                
                forecast_by_day[day_key].append(forecast_item)
            
            # Limit to requested number of days
            days_keys = sorted(forecast_by_day.keys())[:days]
            limited_forecast = {k: forecast_by_day[k] for k in days_keys if k in forecast_by_day}
            
            forecast_data = {
                "location": location_data,
                "forecast": limited_forecast,
                "units": units,
                "timestamp": datetime.now().isoformat()
            }
            
            return {
                "forecast_data": forecast_data,
                "raw_data": data,
                "success": True
            }
            
        except Exception as e:
            logger.error(f"Error retrieving weather forecast for {location}: {e}")
            return {"success": False, "error": str(e)}
    
    def get_air_pollution(self, location):
        """
        Get air pollution data for a location.
        
        Args:
            location (str): Coordinates (lat,lon)
            
        Returns:
            dict: Air pollution data
        """
        try:
            if not self.openweather_key:
                return {"success": False, "error": "OpenWeather API key not configured"}
            
            # Location must be coordinates for this API
            if "," not in location or not all(part.replace("-", "").replace(".", "").isdigit() for part in location.split(",")):
                return {"success": False, "error": "Location must be coordinates (lat,lon) for air pollution data"}
            
            lat, lon = location.split(",")
            url = f"https://api.openweathermap.org/data/2.5/air_pollution"
            params = {
                "lat": lat.strip(),
                "lon": lon.strip(),
                "appid": self.openweather_key
            }
            
            # Make API request
            response = requests.get(url, params=params)
            data = response.json()
            
            # Check for error
            if data.get("cod") and data.get("cod") != 200:
                return {"success": False, "error": data.get("message", "Unknown error")}
            
            # Process and format the data
            if not data.get("list"):
                return {"success": False, "error": "No air pollution data available"}
            
            pollution_data = data.get("list", [{}])[0]
            
            # AQI description
            aqi_descriptions = {
                1: "Good",
                2: "Fair",
                3: "Moderate",
                4: "Poor",
                5: "Very Poor"
            }
            
            aqi = pollution_data.get("main", {}).get("aqi", 0)
            
            formatted_data = {
                "location": {
                    "coordinates": {
                        "lat": float(lat.strip()),
                        "lon": float(lon.strip())
                    }
                },
                "air_quality": {
                    "aqi": aqi,
                    "description": aqi_descriptions.get(aqi, "Unknown"),
                    "components": {
                        "co": pollution_data.get("components", {}).get("co", 0),
                        "no": pollution_data.get("components", {}).get("no", 0),
                        "no2": pollution_data.get("components", {}).get("no2", 0),
                        "o3": pollution_data.get("components", {}).get("o3", 0),
                        "so2": pollution_data.get("components", {}).get("so2", 0),
                        "pm2_5": pollution_data.get("components", {}).get("pm2_5", 0),
                        "pm10": pollution_data.get("components", {}).get("pm10", 0),
                        "nh3": pollution_data.get("components", {}).get("nh3", 0)
                    }
                },
                "timestamp": datetime.fromtimestamp(pollution_data.get("dt", 0)).isoformat()
            }
            
            return {
                "pollution_data": formatted_data,
                "raw_data": data,
                "success": True
            }
            
        except Exception as e:
            logger.error(f"Error retrieving air pollution data for {location}: {e}")
            return {"success": False, "error": str(e)}
