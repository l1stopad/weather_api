from fastapi import FastAPI
from app.routers.weather_router import router as weather_router


app = FastAPI()


app.include_router(weather_router, prefix="/weather", tags=["weather"])
