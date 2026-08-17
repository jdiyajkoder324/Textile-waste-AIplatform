import logging
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.staticfiles import StaticFiles
from app.routes.analytics import router as analytics_router
from app.routes.notifications import router as notifications_router
from app.routes.reports2 import router as reports_router



from app.database import init_db

APP_NAME = "Textile Waste Intelligence Platform"
APP_VERSION = "2.0.0"

# Existing Milestone 1 routers (auth/user + waste CRUD)
from app.api.user import router as user_router
from app.routes.waste import router as waste_router

# Milestone 2 — single consolidated router (replaces the old broken
# material.py / recycling.py / reports.py / image_analysis.py / analysis.py /
# analyze.py files, which used flat imports incompatible with the app.* package)
from app.routes.textile_analysis import router as textile_analysis_router


from app.routes.sustainability_router import router as sustainability_router
        


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("textile_waste_platform")

app = FastAPI(
    title=APP_NAME,
    version=APP_VERSION,
    description=(
        "Textile Waste Intelligence Platform — Waste Batch Management (Milestone 1) "
        "and Material Recognition & Waste Classification (Milestone 2)."
    ),
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup_event():
    try:
        init_db()
        logger.info("Database tables verified/created successfully.")
    except Exception as exc:
        logger.error("Database initialization failed: %s", exc)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    logging.error("VALIDATION ERROR: %s", exc.errors())
    return JSONResponse(status_code=422, content={"detail": exc.errors()})


# --- Routers ---
app.include_router(user_router, prefix="/user", tags=["User"])
app.include_router(waste_router)
app.include_router(textile_analysis_router)
app.include_router(sustainability_router)
app.include_router(analytics_router)
app.include_router(notifications_router)
app.include_router(reports_router)

# Serve uploaded waste images at /uploads/...
os.makedirs("uploads/waste_images", exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")


@app.get("/", tags=["Health"])
def root():
    return {
        "success": True,
        "message": APP_NAME,
        "version": APP_VERSION,
        "docs_url": "/docs",
    }


@app.get("/api/health", tags=["Health"])
def health_check():
    return {"success": True, "message": "API is running successfully."}