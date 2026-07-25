# main.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, HttpUrl
import httpx
import time
from bs4 import BeautifulSoup
import re
from typing import Optional
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Page Pulse API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static files (frontend)
app.mount("/static", StaticFiles(directory="static"), name="static")

class AuditRequest(BaseModel):
    url: HttpUrl

class AuditResponse(BaseModel):
    success: bool
    url: str
    status: Optional[int] = None
    status_text: Optional[str] = None
    response_time: Optional[str] = None
    content_type: Optional[str] = None
    page_title: Optional[str] = None
    meta_description: Optional[str] = None
    h1_count: Optional[int] = None
    images_missing_alt: Optional[int] = None
    word_count: Optional[int] = None
    timestamp: Optional[str] = None
    error: Optional[str] = None

@app.get("/")
async def root():
    """Serve the frontend"""
    from fastapi.responses import FileResponse
    return FileResponse("static/index.html")

@app.post("/api/audit", response_model=AuditResponse)
async def audit_url(request: AuditRequest):
    """
    Audit a URL and return SEO and performance metrics
    """
    url = str(request.url)
    
    # Validate URL format
    if not url.startswith(('http://', 'https://')):
        return AuditResponse(
            success=False,
            url=url,
            error="URL must start with http:// or https://"
        )

    try:
        start_time = time.time()
        
        # Make HTTP request with timeout
        async with httpx.AsyncClient(
            timeout=10.0,
            follow_redirects=True,
            headers={
                'User-Agent': 'PagePulse-AuditBot/1.0',
                'Accept': 'text/html,application/xhtml+xml'
            }
        ) as client:
            response = await client.get(url)
            
        response_time = (time.time() - start_time) * 1000  # Convert to ms
        
        # Check if response is HTML
        content_type = response.headers.get('content-type', '')
        if 'text/html' not in content_type:
            return AuditResponse(
                success=False,
                url=url,
                status=response.status_code,
                status_text=response.reason_phrase,
                content_type=content_type,
                error="URL does not return HTML content"
            )
        
        # Parse HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract page title
        title_tag = soup.find('title')
        page_title = title_tag.get_text().strip() if title_tag else "No title found"
        
        # Extract meta description
        meta_tag = soup.find('meta', attrs={'name': 'description'})
        meta_description = meta_tag.get('content', '').strip() if meta_tag else "No meta description"
        
        # Count H1 tags
        h1_count = len(soup.find_all('h1'))
        
        # Count images missing alt text
        images = soup.find_all('img')
        images_missing_alt = sum(1 for img in images if not img.get('alt') or img.get('alt') == '')
        
        # Approximate word count (exclude HTML tags)
        text = soup.get_text()
        words = re.findall(r'\b\w+\b', text)
        word_count = len(words)
        
        return AuditResponse(
            success=True,
            url=url,
            status=response.status_code,
            status_text=response.reason_phrase,
            response_time=f"{response_time:.0f}ms",
            content_type=content_type,
            page_title=page_title,
            meta_description=meta_description,
            h1_count=h1_count,
            images_missing_alt=images_missing_alt,
            word_count=word_count,
            timestamp=time.strftime("%Y-%m-%d %H:%M:%S")
        )
        
    except httpx.TimeoutException:
        logger.error(f"Timeout for URL: {url}")
        return AuditResponse(
            success=False,
            url=url,
            error="Request timed out. The server took too long to respond."
        )
    
    except httpx.ConnectError:
        logger.error(f"Connection error for URL: {url}")
        return AuditResponse(
            success=False,
            url=url,
            error="Could not connect to the server. Please check the URL."
        )
    
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error for URL {url}: {e.response.status_code}")
        return AuditResponse(
            success=False,
            url=url,
            status=e.response.status_code,
            status_text=e.response.reason_phrase,
            error=f"Server responded with status {e.response.status_code}"
        )
    
    except Exception as e:
        logger.error(f"Unexpected error for URL {url}: {str(e)}")
        return AuditResponse(
            success=False,
            url=url,
            error="An unexpected error occurred. Please try again."
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)