from pydantic import BaseModel


class CityRequest(BaseModel):
    cities: list[str]
