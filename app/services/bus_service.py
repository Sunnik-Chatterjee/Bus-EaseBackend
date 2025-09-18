from app.config import db
from app.common.response import ResponseHelper
import math
from datetime import datetime

class BusService:
    @staticmethod
    def search_buses(start_name, end_name):
        """Search buses where both start and destination stops are upcoming (not yet reached)"""
        
        # Find stop IDs from stop names
        start_stop = db.stops.find_one({"stop_name": start_name})
        end_stop = db.stops.find_one({"stop_name": end_name})
        
        if not start_stop or not end_stop:
            return ResponseHelper.error_response(
                "Start or end destination not found"
            )
        
        start_stop_id = start_stop["stop_id"]
        end_stop_id = end_stop["stop_id"]
        
        # Find buses that have both stops
        buses = db.buses.find({
            "predefined_stops": {"$all": [start_stop_id, end_stop_id]}
        })
        
        valid_buses = []
        
        for bus in buses:
            # Check if route is valid (start comes before end in predefined order)
            if BusService.is_valid_route_order(bus, start_stop_id, end_stop_id):
                # Check if both stops are upcoming (bus hasn't reached start stop yet)
                if BusService.are_stops_upcoming(bus, start_stop_id):
                    last_stop_data = db.stops.find_one({"stop_id": bus.get("last_stop_passed")})
                    
                    bus_info = {
                        "bus_id": bus["bus_id"],
                        "bus_number": bus["bus_number"],
                        "bus_name": bus.get("bus_name", "Unknown"),
                        "last_stop_passed": {
                            "stop_id": bus.get("last_stop_passed"),
                            "name": last_stop_data["stop_name"] if last_stop_data else "Not started"
                        },
                        "status": bus.get("status", "inactive"),
                        "current_location": bus.get("current_location")
                    }
                    valid_buses.append(bus_info)
        
        return ResponseHelper.success_response(
            message=f"Found {len(valid_buses)} available buses",
            data={
                "total_buses": len(valid_buses),
                "search_params": {
                    "start_destination": start_name,
                    "end_destination": end_name
                },
                "buses": valid_buses
            }
        )
    
    @staticmethod
    def is_valid_route_order(bus, start_stop_id, end_stop_id):
        """Check if start stop comes before destination stop in predefined route order"""
        predefined_stops = bus["predefined_stops"]
        
        try:
            start_index = predefined_stops.index(start_stop_id)
            end_index = predefined_stops.index(end_stop_id)
            return start_index < end_index  # Start must come before destination
        except ValueError:
            return False
    
    @staticmethod
    def are_stops_upcoming(bus, start_stop_id):
        """Check if start stop is upcoming (bus hasn't reached it yet)"""
        
        last_stop_passed = bus.get("last_stop_passed")
        predefined_stops = bus["predefined_stops"]
        
        # If bus hasn't started, all stops are upcoming
        if not last_stop_passed:
            return True
        
        try:
            start_index = predefined_stops.index(start_stop_id)
            last_stop_index = predefined_stops.index(last_stop_passed)
            
            # Start stop is upcoming if bus hasn't reached it yet
            return last_stop_index < start_index
        except ValueError:
            return False
    
    @staticmethod
    def calculate_distance(lat1, lng1, lat2, lng2):
        """Calculate distance between two GPS coordinates using Haversine formula"""
        R = 6371  # Earth's radius in kilometers
        
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lng = math.radians(lng2 - lng1)
        
        a = (math.sin(delta_lat/2) * math.sin(delta_lat/2) + 
             math.cos(lat1_rad) * math.cos(lat2_rad) * 
             math.sin(delta_lng/2) * math.sin(delta_lng/2))
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        
        return R * c * 1000  # Return distance in meters
    
    @staticmethod
    def find_last_stop_passed(current_lat, current_lng, predefined_stops):
        """Find the last stop the bus has passed based on current GPS location"""
        STOP_THRESHOLD = 200  # 200 meters threshold
        
        last_stop_index = -1
        
        for i, stop_id in enumerate(predefined_stops):
            stop_data = db.stops.find_one({"stop_id": stop_id})
            if not stop_data:
                continue
                
            distance = BusService.calculate_distance(
                current_lat, current_lng,
                stop_data["location"]["lat"],
                stop_data["location"]["lng"]
            )
            
            # If bus is within threshold of this stop, consider it passed
            if distance <= STOP_THRESHOLD:
                last_stop_index = i
        
        return last_stop_index
    
    @staticmethod
    def update_bus_location(bus_id, lat, lng):
        """Update bus location from driver's app"""
        bus = db.buses.find_one({"bus_id": bus_id})
        
        if not bus:
            return ResponseHelper.error_response(
                f"Bus with ID '{bus_id}' not found"
            )
        
        # Calculate which stop the bus has passed
        last_stop_index = BusService.find_last_stop_passed(lat, lng, bus["predefined_stops"])
        
        # Determine last stop passed
        last_stop_passed = None
        if last_stop_index >= 0 and last_stop_index < len(bus["predefined_stops"]):
            last_stop_passed = bus["predefined_stops"][last_stop_index]
        
        # Update database
        update_data = {
            "current_location": {"lat": lat, "lng": lng},
            "last_updated": datetime.utcnow()
        }
        
        if last_stop_passed:
            update_data["last_stop_passed"] = last_stop_passed
        
        result = db.buses.update_one(
            {"bus_id": bus_id},
            {"$set": update_data}
        )
        
        if result.modified_count > 0:
            # Get upcoming stops
            upcoming_stops = []
            if last_stop_index >= 0:
                remaining_stops = bus["predefined_stops"][last_stop_index + 1:]
                for stop_id in remaining_stops[:3]:
                    stop_data = db.stops.find_one({"stop_id": stop_id})
                    if stop_data:
                        upcoming_stops.append({
                            "stop_id": stop_id,
                            "name": stop_data["stop_name"]
                        })
            
            return ResponseHelper.success_response(
                message="Location updated successfully",
                data={
                    "bus_id": bus_id,
                    "bus_number": bus["bus_number"],
                    "updated_location": {"lat": lat, "lng": lng},
                    "last_stop_passed": last_stop_passed,
                    "upcoming_stops": upcoming_stops,
                    "updated_at": datetime.utcnow().isoformat()
                }
            )
        else:
            return ResponseHelper.error_response("Failed to update bus location")
    
    @staticmethod
    def get_bus_details(bus_id):
        """Get detailed information about a specific bus for user app/web"""
        bus = db.buses.find_one({"bus_id": bus_id})
        
        if not bus:
            return ResponseHelper.error_response(
                f"Bus with ID '{bus_id}' not found"
            )
        
        # Get all stops with their details
        all_stops = []
        last_stop_index = -1
        
        if bus.get("last_stop_passed"):
            try:
                last_stop_index = bus["predefined_stops"].index(bus["last_stop_passed"])
            except ValueError:
                last_stop_index = -1
        
        for i, stop_id in enumerate(bus["predefined_stops"]):
            stop_data = db.stops.find_one({"stop_id": stop_id})
            
            # Calculate distance from bus to this stop
            distance_to_stop = 0
            if bus.get("current_location") and stop_data:
                distance_to_stop = BusService.calculate_distance(
                    bus["current_location"]["lat"],
                    bus["current_location"]["lng"],
                    stop_data["location"]["lat"],
                    stop_data["location"]["lng"]
                )
            
            stop_info = {
                "stop_id": stop_id,
                "name": stop_data["stop_name"] if stop_data else "Unknown",
                "location": stop_data["location"] if stop_data else None,
                "order": i + 1,
                "distance_from_bus": f"{distance_to_stop:.0f}m" if distance_to_stop else "N/A",
                "status": "passed" if i <= last_stop_index else "upcoming"
            }
            all_stops.append(stop_info)
        
        return ResponseHelper.success_response(
            message=f"Bus details for {bus['bus_number']}",
            data={
                "bus_info": {
                    "bus_id": bus["bus_id"],
                    "bus_number": bus["bus_number"],
                    "status": bus.get("status", "inactive"),
                    "current_location": bus.get("current_location"),
                    "last_updated": bus.get("last_updated").isoformat() if bus.get("last_updated") else None
                },
                "last_stop_passed": bus.get("last_stop_passed"),
                "all_stops": all_stops,
                "total_stops": len(all_stops)
            }
        )
    
    @staticmethod
    def get_bus_by_name(bus_name):
        """Get ONLY last stop passed by bus name - simple response"""
        bus = db.buses.find_one({"bus_name": bus_name})
        
        if not bus:
            return ResponseHelper.error_response(
                f"Bus with name '{bus_name}' not found"
            )
        
        # Check if bus has started journey
        if not bus.get("last_stop_passed"):
            return ResponseHelper.success_response(
                message="Bus haven't start journey",
                data=None
            )
        
        # Bus has started - get last stop details
        last_stop_data = db.stops.find_one({"stop_id": bus["last_stop_passed"]})
        
        return ResponseHelper.success_response(
            message="Last stop found",
            data={
                "stop_id": bus["last_stop_passed"],
                "name": last_stop_data["stop_name"] if last_stop_data else "Unknown Stop",
                "location": last_stop_data["location"] if last_stop_data else None
            }
        )
