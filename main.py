# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import httpx
import time
from html.parser import HTMLParser
import re
import logging
import os
from typing import Optional, Dict, Any

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Page Pulse API",
    version="1.0.0",
    description="URL auditing tool for SEO and performance metrics"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
try:
    if os.path.exists("static"):
        app.mount("/static", StaticFiles(directory="static"), name="static")
except Exception as e:
    logger.warning(f"Could not mount static files: {e}")

class AuditRequest(BaseModel):
    url: str

class SimpleHTMLParser(HTMLParser):
    """Custom HTML parser to extract needed data without lxml"""
    def __init__(self):
        super().__init__()
        self.title = None
        self.in_title = False
        self.meta_description = None
        self.h1_count = 0
        self.in_h1 = False
        self.images_missing_alt = 0
        self.text_content = []
        self.current_tag = None
        self.current_attrs = {}
        
    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        self.current_tag = tag
        self.current_attrs = attrs_dict
        
        if tag == 'title':
            self.in_title = True
        elif tag == 'h1':
            self.h1_count += 1
            self.in_h1 = True
        elif tag == 'img':
            alt = attrs_dict.get('alt', '')
            if not alt or alt.strip() == '':
                self.images_missing_alt += 1
        elif tag == 'meta':
            if attrs_dict.get('name') == 'description':
                self.meta_description = attrs_dict.get('content', '').strip()
    
    def handle_endtag(self, tag):
        if tag == 'title':
            self.in_title = False
        elif tag == 'h1':
            self.in_h1 = False
    
    def handle_data(self, data):
        if self.in_title and self.title is None:
            self.title = data.strip()
        if data.strip():
            self.text_content.append(data.strip())
    
    def get_word_count(self):
        """Calculate approximate word count from text content"""
        text = ' '.join(self.text_content)
        words = re.findall(r'\b\w+\b', text)
        return len(words)

@app.get("/")
async def root():
    """Serve the frontend"""
    try:
        if os.path.exists("static/index.html"):
            return FileResponse("static/index.html")
        else:
            return {"message": "Page Pulse is running!", "status": "ok"}
    except Exception as e:
        return {"message": "Page Pulse is running!", "status": "ok"}

@app.get("/health")
async def health():
    """Health check endpoint for Render"""
    return {
        "status": "healthy",
        "service": "Page Pulse",
        "version": "1.0.0",
        "python_version": os.getenv("PYTHON_VERSION", "3.11"),
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S %Z")
    }

@app.post("/api/audit")
async def audit_url(request: AuditRequest):
    """
    Audit a URL and return SEO and performance metrics
    """
    url = request.url.strip()
    
    # Validate URL format
    if not url.startswith(('http://', 'https://')):
        return {
            'success': False,
            'error': 'URL must start with http:// or https://'
        }
    
    try:
        start_time = time.time()
        
        # Get timeout from environment or use default
        timeout = float(os.getenv("TIMEOUT", "15.0"))
        
        async with httpx.AsyncClient(
            timeout=timeout,
            follow_redirects=True,
            headers={
                'User-Agent': 'PagePulse-AuditBot/1.0',
                'Accept': 'text/html,application/xhtml+xml'
            }
        ) as client:
            response = await client.get(url)
            
        response_time = (time.time() - start_time) * 1000
        
        # Check if response is HTML
        content_type = response.headers.get('content-type', '')
        if 'text/html' not in content_type:
            return {
                'success': False,
                'url': url,
                'status': response.status_code,
                'content_type': content_type,
                'error': 'URL does not return HTML content'
            }
        
        # Parse HTML using custom parser (no lxml!)
        parser = SimpleHTMLParser()
        parser.feed(response.text)
        
        return {
            'success': True,
            'url': url,
            'status': response.status_code,
            'status_text': response.reason_phrase or "OK",
            'response_time': f"{response_time:.0f}ms",
            'content_type': content_type,
            'page_title': parser.title or "No title found",
            'meta_description': parser.meta_description or "No meta description",
            'h1_count': parser.h1_count,
            'images_missing_alt': parser.images_missing_alt,
            'word_count': parser.get_word_count(),
            'timestamp': time.strftime("%Y-%m-%d %H:%M:%S %Z")
        }
        
    except httpx.TimeoutException:
        logger.error(f"Timeout for URL: {url}")
        return {
            'success': False,
            'url': url,
            'error': 'Request timed out. The server took too long to respond.'
        }
    
    except httpx.ConnectError:
        logger.error(f"Connection error for URL: {url}")
        return {
            'success': False,
            'url': url,
            'error': 'Could not connect to the server. Please check the URL.'
        }
    
    except Exception as e:
        logger.error(f"Unexpected error for URL {url}: {str(e)}")
        return {
            'success': False,
            'url': url,
            'error': f'Error: {str(e)}'
        }

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)