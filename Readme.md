
# Weather API

This is a FastAPI-based weather API that allows you to fetch weather information for cities, process weather data asynchronously with Celery, and store the results in JSON format. It integrates with Redis as a message broker for task queuing.

## Features
- Fetch weather data for multiple cities.
- Asynchronous processing of weather data with Celery.
- Stores results in JSON files, organized by region.
- Supports status checking for tasks.
- Handles errors for invalid cities (incorrect city names are logged and saved separately).

## Requirements
- Docker
- Docker Compose
- Python 3.9+

## Setup and Installation

1. **Create a `.env` file** for environment variables. The file should include the following:

   ```
   API_KEY=your_openweathermap_api_key
   ```

2. **Build and run the application using Docker Compose**:

   ```bash
   docker-compose up --build
   ```

3. **Access the API**: The API will be available at [http://localhost:8000](http://localhost:8000).

4. **Access Celery worker logs**: The Celery worker logs can be accessed at:

   ```bash
   docker logs weather-celery
   ```

## API Endpoints

### 1. POST `/weather`
- **Description**: Start the task to fetch weather data for multiple cities.
- **Request Body**:
  ```json
  {
    "cities": ["City1", "City2", "City3"]
  }
  ```
- **Response**:
  ```json
  {
    "task_id": "generated_task_id"
  }
  ```

### 2. GET `/tasks/{task_id}`
- **Description**: Check the status of a task.
- **Response**:
  ```json
  {
    "task_id": "generated_task_id",
    "status": "completed",
    "result": {...}
  }
  ```

### 3. GET `/results/{region}`
- **Description**: Fetch the weather data for a specific region.
- **Response**:
  ```json
  {
    "region": "Europe",
    "data": [{...}, {...}]
  }
  ```

## Troubleshooting
- **If the API does not show the latest files**: Ensure the volumes are correctly mounted, and Docker containers are properly configured to share files between the Celery worker and the API.
# Weather Data Processing API with FastAPI, Celery, and Redis

## Common Issues and Solutions

### 1. **Issue: Celery tasks not updating the results correctly**
   **Problem**: Sometimes, Celery workers may not update the status or results correctly, causing the API to not reflect the latest changes.
   **Solution**:
   - Ensure that the task results are being stored properly in the backend (in this case, Redis).
   - Make sure you're using the correct Celery result backend (`CELERY_RESULT_BACKEND=redis://redis:6379/0`).
   - Double-check that the task is not failing silently. Add logging inside your Celery task to monitor the progress and detect any errors.

### 2. **Issue: New files are not being detected by the API**
   **Problem**: When new weather data is saved by the Celery worker, the API container cannot detect the newly created files.
   **Solution**:
   - This issue often arises because Docker volumes are not shared properly between containers. In your case, Celery is writing files to the local filesystem, but the API cannot access them.
   - **Fix**: Ensure that the volumes in the `docker-compose.yml` file are set up correctly to allow file sharing between containers.
     - Example:
       ```yaml
       volumes:
         - .:/app
       ```
   - This ensures that the API container can access files written by Celery as both services are mounted to the same volume.

### 3. **Issue: The API is not able to read from the mounted volume**
   **Problem**: The API may not be able to access the files even though the Docker volume is set up.
   **Solution**:
   - Make sure the permissions on the shared directory are correct. If necessary, set the correct file access permissions for the API container.
   - You may need to rebuild the containers after changing the `docker-compose.yml` file to ensure the volume is mounted correctly.

### 4. **Issue: Redis container is not running**
   **Problem**: Celery workers and the API rely on Redis for message queuing and task result storage. If Redis is not running, the tasks will fail.
   **Solution**:
   - Make sure that Redis is properly started and running in your Docker container. You can check its status by running `docker ps` and looking for the Redis container.
   - Check if there are any connectivity issues between the services (API, Celery, Redis). You may want to add debugging logs in the `weather-api` and `celery` services to confirm they can connect to Redis.

### 5. **Issue: Task fails with HTTP errors (404 or 500)**
   **Problem**: Tasks that involve fetching weather data from an external API may fail due to HTTP errors like 404 (city not found) or 500 (server error).
   **Solution**:
   - Handle the HTTP status errors in your task to ensure that failed tasks don't crash the worker. You can log the error and handle specific status codes, like 404 for a city not found.
   - Implement retries for transient errors or HTTP 500, so the task can try again after a short delay.
   - Example code for handling HTTP errors:
     ```python
     except httpx.HTTPStatusError as http_exc:
         if http_exc.response.status_code == 404:
             logging.error(f"City not found: {city}")
         else:
             logging.error(f"HTTP error: {str(http_exc)}")
         raise
     ```

### 6. **Issue: Task result is not updated in the API**
   **Problem**: The API may not reflect the result of the Celery task if the task is not properly updating its state in Redis.
   **Solution**:
   - Ensure that the Celery task updates its state with the `update_state` method after completing. Use `task.update_state(state='SUCCESS', meta={'result': result})` to ensure the task result is stored and accessible.
   - Verify that the task ID used to check for the task status in the API matches the one passed to Celery when calling `apply_async`.

### 7. **Issue: API is showing an empty list of weather data**
   **Problem**: The API might show an empty list of weather data even though the Celery task has completed successfully.
   **Solution**:
   - Verify that the results data from the Celery task is being saved in the correct directory. If you use directories for regions, make sure the path and filenames are correct.
   - Check that the directory and files have the proper permissions and are accessible from the API container.

### 8. **Issue: Celery worker crashes or doesn't start**
   **Problem**: The Celery worker may fail to start due to misconfiguration or missing dependencies.
   **Solution**:
   - Ensure that the `celery` command in your `docker-compose.yml` is correct. It should look like:
     ```yaml
     command: celery -A app.tasks worker -P gevent --loglevel=info
     ```
   - Check the logs of the Celery container using `docker logs weather-celery` to see any error messages or misconfigurations.
   - Ensure that all required dependencies (like `gevent` for concurrency) are installed in your container environment.

### 9. **Issue:
