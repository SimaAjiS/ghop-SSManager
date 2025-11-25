from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
from . import settings
from .routers import tables, devices

app = FastAPI(title="Master Table Manager API")


@app.get("/")
def root():
    """Root endpoint - API health check."""
    return {
        "message": "Master Table Manager API is running",
        "docs": "/docs",
        "api_prefix": "/api",
    }


# Mount static files for chip appearance images
CHIP_APPEARANCES_DIR = os.path.join(settings.DATA_DIR, "chip_appearances")
if os.path.exists(CHIP_APPEARANCES_DIR):
    app.mount(
        "/static/chip_appearances",
        StaticFiles(directory=CHIP_APPEARANCES_DIR),
        name="chip_appearances",
    )

# CORS configuration
origins = [
    "http://localhost:5173",  # Vite default port
    "http://127.0.0.1:5173",
    "http://localhost:5174",  # Alternative Vite port
    "http://127.0.0.1:5174",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(tables.router, prefix="/api", tags=["tables"])
app.include_router(devices.router, prefix="/api", tags=["devices"])
