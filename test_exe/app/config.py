import os
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

# Configuration settings
API_URL_OPENWEATHERMAP = "https://api.openweathermap.org/data/2.5/weather"
API_KEY_OPENWEATHERMAP = os.getenv('API_KEY_OPENWEATHERMAP')
