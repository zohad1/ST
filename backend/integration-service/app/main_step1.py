# app/main_step1.py - Test basic imports
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Test imports one by one
try:
    from app.core.config import settings
    logger.info("✓ Config imported successfully")
except Exception as e:
    logger.error(f"✗ Config import failed: {e}")
    settings = None

# Create FastAPI app
app = FastAPI(
    title="TikTok Shop Integration Service - Step 1",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {
        "status": "running",
        "step": "1 - Testing basic imports",
        "config_loaded": settings is not None
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}