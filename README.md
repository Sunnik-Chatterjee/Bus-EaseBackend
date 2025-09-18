# BusEase Backend API

Smart Bus Tracking System Backend built with FastAPI and MongoDB.

## Features

- 🚌 Real-time bus tracking
- 📍 Smart route-based bus search
- 🗺️ GPS-based location updates
- 📱 RESTful API for mobile/web apps

## API Endpoints

- `GET /api/buses/search?start=...&end=...` - Search buses
- `GET /api/buses/{bus_id}` - Get bus details
- `GET /api/buses/by-name/{name}` - Get bus by name
- `POST /api/buses/{bus_id}/location` - Update bus location

## Tech Stack

- **Backend**: FastAPI, Python 3.11+
- **Database**: MongoDB Atlas
- **Deployment**: Render
