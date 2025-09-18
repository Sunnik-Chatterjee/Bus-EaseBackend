from fastapi import APIRouter, Query, Path
from app.services.bus_service import BusService
from app.common.response import APIResponse

router = APIRouter()

@router.get("/buses/search", response_model=APIResponse)
async def search_buses(
    start: str = Query(..., description="Start destination name"),
    end: str = Query(..., description="End destination name")
):
    """Search available buses between destinations"""
    result = BusService.search_buses(start, end)
    return result

@router.get("/buses/{bus_id}", response_model=APIResponse)
async def get_bus_details(
    bus_id: str = Path(..., description="Bus ID")
):
    """Get complete bus details and tracking info"""
    result = BusService.get_bus_details(bus_id)
    return result

@router.post("/buses/{bus_id}/location", response_model=APIResponse)
async def update_bus_location(
    bus_id: str = Path(..., description="Bus ID"),
    lat: float = Query(..., description="Latitude"),
    lng: float = Query(..., description="Longitude")
):
    """Update bus location from driver's app"""
    result = BusService.update_bus_location(bus_id, lat, lng)
    return result

@router.get("/buses/by-name/{bus_name}", response_model=APIResponse)
async def get_bus_by_name(
    bus_name: str = Path(..., description="Bus name to search")
):
    """Get ONLY last stop passed by bus name"""
    result = BusService.get_bus_by_name(bus_name)
    return result