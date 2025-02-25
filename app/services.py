import httpx
import requests
import logging
from app.config import API_URL_OPENWEATHERMAP, API_KEY_OPENWEATHERMAP


async def get_weather_data(city: str) -> dict:
    try:
        params = {"q": city, "appid": API_KEY_OPENWEATHERMAP, "units": "metric"}
        async with httpx.AsyncClient() as client:
            response = await client.get(API_URL_OPENWEATHERMAP, params=params)
        response.raise_for_status()

        data = response.json()
        processed_data = {
            "city": data["name"],
            "temperature": data["main"]["temp"],
            "description": data["weather"][0]["description"]
        }

        # Validate the data
        if not validate_data(processed_data):
            raise ValueError(f"Invalid data: {processed_data}")

        logging.info(f"Successfully processed data for city: {city}")
        return processed_data

    except httpx.HTTPStatusError as http_exc:
        # If the status code is 404 (city not found)
        if http_exc.response.status_code == 404:
            logging.error(f"City {city} not found. Error: {str(http_exc)}")
            return {"City": city, "Error": "City not found"}
        else:
            logging.error(f"HTTP error for {city}: {str(http_exc)}")
            raise

    except ValueError as val_exc:
        logging.error(f"Error processing data for {city}: {str(val_exc)}")
        raise

    except Exception as exc:
        logging.error(f"Unknown error for {city}: {str(exc)}")
        raise


def validate_data(data):
    # Check if the required fields are present
    if not data.get("city") or not data.get("temperature") or not data.get("description"):
        return False

    # Example validation: temperature should be within the range of -50 to +50 °C
    temp = data.get("temperature")
    if temp is None or not (-50 <= temp <= 50):
        return False

    # If all conditions are met, the data is valid
    return True





