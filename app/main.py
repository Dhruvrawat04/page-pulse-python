# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.models import AuditRequest
from app.audit import PageAuditor
import logging
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Page Pulse API",
    version="1.0.0",
    description="URL auditing tool for SEO and performance metrics"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
try:
    app.mount("/static", StaticFiles(directory="static"), name="static")
except Exception as e:
    logger.warning(f"Static files not mounted: {e}")

# Initialize auditor
auditor = PageAuditor(timeout=float(os.getenv("TIMEOUT", "15.0")))

@app.get("/")
async def root():
    """Serve the frontend"""
    try:
        return FileResponse("static/index.html")
    except Exception:
        return {"error": "Frontend not found", "status": "error"}

@app.get("/health")
async def health():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Page Pulse",
        "version": "1.0.0"
    }

@app.post("/api/audit")
async def audit_url(request: AuditRequest):
    """Audit a URL and return SEO metrics"""
    result = await auditor.audit(str(request.url))
    return result

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)