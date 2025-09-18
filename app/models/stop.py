from pydantic import BaseModel

class StopModel(BaseModel):
    _id: str
    name: str
    lat: float
    lng: float
