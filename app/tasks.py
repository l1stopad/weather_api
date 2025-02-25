import logging
from celery import Celery
import httpx
import asyncio
from app.services import get_weather_data
from app.utils import split_by_region
import json
import os

app = Celery('tasks', broker='redis://redis:6379/0')

app.conf.update(
    task_acks_late=True,
    task_track_started=True,
    task_serializer='json',
    result_backend='redis://redis:6379/0',
    result_serializer='json'
)


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# @app.task(bind=True)
# def fetch_weather_task(self, cities, task_id):
#     results = {}  # Порожній словник для результатів
#
#     # Створюємо цикл подій для цього завдання
#     loop = asyncio.new_event_loop()
#     asyncio.set_event_loop(loop)
#
#     async def process_city_data(city):
#         weather_data = await get_weather_data(city)
#         if weather_data.get("error") == "Incorrect":
#             # Додаємо регіон incorrect_cities, якщо його ще немає
#             if "Incorrect" not in results:
#                 results["Incorrect"] = []
#             results["Incorrect"].append({"city": city, "error": "City not found"})
#         else:
#             region = split_by_region(city)
#             if region not in results:
#                 results[region] = []
#             results[region].append(weather_data)
#
#     # Створюємо завдання для кожного міста
#     tasks = [loop.create_task(process_city_data(city)) for city in cities]
#
#     try:
#         loop.run_until_complete(asyncio.gather(*tasks))
#
#         # Зберігаємо результати в файли
#         for region, data in results.items():
#             file_path = f"weather_data/{region}/task_{task_id}.json"
#             os.makedirs(os.path.dirname(file_path), exist_ok=True)
#             with open(file_path, "w") as f:
#                 json.dump(data, f)
#
#         self.update_state(state="SUCCESS", meta={"results": results})
#         logger.info(f"Task {task_id} completed successfully.")
#
#     except Exception as e:
#         # У разі помилки, оновлюємо статус на 'FAILURE'
#         self.update_state(state="FAILURE", meta={"error": str(e)})
#         logger.error(f"Task {task_id} failed: {str(e)}")
#         return {"status": "failed", "error": str(e)}
#
#     return results

@app.task(bind=True)
def fetch_weather_task(self, cities, task_id):
    results = {}  # Empty dictionary to store the results for each region and incorrect cities

    # Create a new event loop for this task
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)  # Set the new event loop for the current thread

    async def process_city_data(city):
        # Fetch weather data asynchronously for each city
        weather_data = await get_weather_data(city)

        # If the city has an error (incorrect city name, etc.), add it to the "Incorrect" region
        if weather_data.get("error") == "Incorrect":
            # Add the "Incorrect" region if it doesn't exist in results
            if "Incorrect" not in results:
                results["Incorrect"] = []
            # Add the city and its error message to the "Incorrect" region
            results["Incorrect"].append({"city": city, "error": "City not found"})
        else:
            # If the city data is valid, determine its region and store the data in the appropriate region
            region = split_by_region(city)
            if region not in results:
                results[region] = []
            results[region].append(weather_data)

    # Create tasks for each city and process them asynchronously
    tasks = [loop.create_task(process_city_data(city)) for city in cities]

    try:
        # Run the tasks until they are completed
        loop.run_until_complete(asyncio.gather(*tasks))

        # After all tasks are done, save the results into files
        for region, data in results.items():
            file_path = f"weather_data/{region}/task_{task_id}.json"
            os.makedirs(os.path.dirname(file_path), exist_ok=True)  # Create the directory if it doesn't exist
            with open(file_path, "w") as f:
                json.dump(data, f)  # Save the region data to a JSON file

        # Update the Celery task state to "SUCCESS" and log the task completion
        self.update_state(state="SUCCESS", meta={"results": results})
        logger.info(f"Task {task_id} completed successfully.")

    except Exception as e:
        # If there was an error during the task execution, update the state to "FAILURE"
        self.update_state(state="FAILURE", meta={"error": str(e)})
        logger.error(f"Task {task_id} failed: {str(e)}")
        return {"status": "failed", "error": str(e)}

    # Return the results dictionary containing the weather data or errors
    return results