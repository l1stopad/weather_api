# Weather API

**Weather API** is an asynchronous service based on **FastAPI** that allows fetching weather information for cities, processing it via **Celery**, and storing the results in **JSON**. The API uses **Redis** as a message broker for task queuing.

---
## ✨ Features
- Fetch weather data for multiple cities simultaneously.
- Asynchronous request processing using Celery.
- Store results in JSON files, organized by region.
- Check task execution status.
- Handle errors for incorrect city names (logging and saving to files).

---
## 🛠️ Requirements
- **Docker**
- **Docker Compose**
- **Python 3.9+**
- **Celery**

---
## ⚙️ Setup & Installation

### 1. **Create a `.env` file** to store environment variables.

   ```ini
   API_KEY=your_openweathermap_api_key
   ```

### 2. **Run the application using Docker Compose**:

   ```sh
   docker-compose up --build
   ```

### 3. **Access the API**:
The API will be available at: [http://localhost:8000](http://localhost:8000)

### 4. **View Celery Worker logs**:

   ```sh
   docker logs weather-celery
   ```

---
## 🔍 API Endpoints

### 1. **POST `/weather`**
- **Description**: Creates a task to fetch weather data for multiple cities.
- **Example Request**:
  ```json
  {
    "cities": ["Kyiv", "London", "New York"]
  }
  ```
- **Example Response**:
  ```json
  {
    "task_id": "generated_task_id"
  }
  ```

### 2. **GET `/tasks/{task_id}`**
- **Description**: Checks the execution status of a task.
- **Example Response**:
  ```json
  {
    "task_id": "generated_task_id",
    "status": "completed",
    "result": {...}
  }
  ```

### 3. **GET `/results/{region}`**
- **Description**: Retrieves stored weather data for a specific region.
- **Example Response**:
  ```json
  {
    "region": "Europe",
    "data": [{...}, {...}]
  }
  ```

---
## 🔧 Celery: Configuration & Key Commands

### **1. Start Celery Worker**
Run Celery Worker to process tasks:

```sh
celery -A app.tasks worker --loglevel=info
```

### **2. Start Celery Beat (Task Scheduler)**
If you need scheduled task execution, start Celery Beat:

```sh
celery -A app.tasks beat --loglevel=info
```

### **3. Check Task Queue**
To check active tasks in the queue, use:

```sh
celery -A app.tasks inspect active
```

### **4. Clear Task Queue**
To remove all pending tasks:

```sh
celery -A app.tasks purge
```

---
## 🛠️ Troubleshooting Common Issues

### **1. Celery does not update results**
- Ensure Celery is using the correct `CELERY_RESULT_BACKEND=redis://redis:6379/0`.
- Add logging inside Celery tasks to track execution.

### **2. API does not detect new files**
- In `docker-compose.yml`, ensure **API** and **Celery Worker** share the same `volumes`:
  ```yaml
  volumes:
    - .:/app
  ```
- This ensures that both API and Celery work on the same file system.

### **3. Redis is not running**
- Check if Redis is running using `docker ps`.
- If Redis is not running, start it manually:
  ```sh
  docker-compose up redis
  ```

### **4. API does not retrieve task results**
- Use `task.update_state(state='SUCCESS', meta={'result': result})` to ensure Celery updates the task status.
- Verify that the `task_id` in the request matches the one passed to Celery via `apply_async`.

### **5. Celery Worker does not start**
- Check if all dependencies are installed.
- Use the command:
  ```sh
  docker logs weather-celery
  ```
  to view possible errors.
- Ensure Celery is started with the correct command in `docker-compose.yml`:
  ```yaml
  command: celery -A app.tasks worker --loglevel=info
  ```

---
## 📃 License
This project is distributed under the MIT License.

---
**🛠️ Ready to go!** Your Weather API is now set up and ready for use! 🚀

