from pydantic import BaseModel
from typing import List, Dict

class BusModel(BaseModel):
    _id: str
    bus_number: str
    stops: List[str]   # List of stop IDs
    current_location: Dict[str, float]
    status: str
