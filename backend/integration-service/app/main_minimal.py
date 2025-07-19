# app/main_minimal.py - Use this to test if basic setup works
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Create minimal FastAPI app
app = FastAPI(
    title="TikTok Shop Integration Service - Minimal",
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

# Root endpoint
@app.get("/")
async def root():
    return {
        "name": "TikTok Shop Integration Service",
        "version": "1.0.0",
        "status": "running (minimal mode)"
    }

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# Test endpoint
@app.get("/test")
async def test():
    return {"message": "If you see this, FastAPI is working!"}