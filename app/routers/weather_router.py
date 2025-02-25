import json
import os
from fastapi import APIRouter, HTTPException
from app.tasks import fetch_weather_task
from app.utils import normalize_city, correct_typos
from app.models import CityRequest
from celery.result import AsyncResult
from app.tasks import app as celery_app
import uuid


router = APIRouter()


@router.post("/weather")
async def weather_data(request: CityRequest):
    task_id = str(uuid.uuid4())  # Generate a task_id
    # Clean and normalize city names
    cleaned_cities = [normalize_city(correct_typos(city)) for city in request.cities]

    # Start asynchronous task to process data
    fetch_weather_task.apply_async(args=[cleaned_cities, task_id], task_id=task_id)  # Pass task_id

    return {"task_id": task_id}


@router.get("/tasks/{task_id}")
async def get_task_status(task_id: str):
    # Create an AsyncResult instance with the given task_id
    task_result = AsyncResult(task_id, app=celery_app)

    # Check if the task exists by checking if it has a valid result
    if not task_result.result and task_result.status == "PENDING":
        raise HTTPException(status_code=404, detail=f"Task with ID {task_id} does not exist or has expired.")

    # Check the task's current status
    if task_result.ready():
        if task_result.status == "SUCCESS":
            return {"task_id": task_id, "status": "completed", "result": task_result.result}
        elif task_result.status == "FAILURE":
            return {"task_id": task_id, "status": "failed", "result": None, "error": str(task_result.result)}
        elif task_result.status == "PENDING":
            return {"task_id": task_id, "status": "pending", "result": None}
        else:
            return {"task_id": task_id, "status": "unknown", "result": None}
    else:
        # Task is still running
        return {"task_id": task_id, "status": "running", "result": None}


@router.get("/results/{region}")
async def get_results_by_region(region: str):
    # Path to the directory where weather data is stored
    file_path = f"weather_data/{region}"

    # Check if the region's directory exists
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail=f"Region '{region}' not found")

    # Logging to check if the directory exists and its contents
    print(f"Directory for region {region} exists: {os.path.exists(file_path)}")
    print(f"Files in directory: {os.listdir(file_path)}")

    # Get all JSON files in the region's directory and combine their data
    combined_weather_data = []
    for filename in os.listdir(file_path):
        if filename.endswith(".json"):
            try:
                with open(os.path.join(file_path, filename), 'r') as f:
                    data = json.load(f)
                    combined_weather_data.extend(data)  # Add all data from this file to the combined list
            except Exception as e:
                # Log any errors while reading a file
                print(f"Error reading {filename}: {str(e)}")

    if not combined_weather_data:
        raise HTTPException(status_code=404, detail=f"No weather data found for region {region}")

    return {"region": region, "data": combined_weather_data}
