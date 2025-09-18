from fastapi import FastAPI
from app.routes.bus_route import router as bus_router

app = FastAPI(title="BusEase API")

app.include_router(bus_router, prefix="/api")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
