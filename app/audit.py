# app/audit.py
import time
import re
from typing import Dict, Any
import httpx
from bs4 import BeautifulSoup
import logging

logger = logging.getLogger(__name__)

class PageAuditor:
    """Core auditing logic - separated for testing"""
    
    def __init__(self, timeout: float = 15.0):
        self.timeout = timeout
        self.headers = {
            'User-Agent': 'PagePulse-AuditBot/1.0',
            'Accept': 'text/html,application/xhtml+xml'
        }
    
    async def fetch_page(self, url: str) -> httpx.Response:
        """Fetch the page content"""
        async with httpx.AsyncClient(
            timeout=self.timeout,
            follow_redirects=True,
            headers=self.headers
        ) as client:
            return await client.get(url)
    
    def parse_html(self, html: str, url: str) -> Dict[str, Any]:
        """Parse HTML and extract SEO metrics"""
        # ✅ Using html.parser - works on Render without issues!
        soup = BeautifulSoup(html, 'html.parser')
        
        # Extract title
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
        
        # Word count
        text = soup.get_text()
        words = re.findall(r'\b\w+\b', text)
        word_count = len(words)
        
        return {
            'page_title': page_title,
            'meta_description': meta_description,
            'h1_count': h1_count,
            'images_missing_alt': images_missing_alt,
            'word_count': word_count
        }
    
    def is_html_response(self, content_type: str) -> bool:
        """Check if response is HTML"""
        return 'text/html' in content_type.lower()
    
    async def audit(self, url: str) -> Dict[str, Any]:
        """Perform complete audit"""
        try:
            start_time = time.time()
            response = await self.fetch_page(url)
            response_time = (time.time() - start_time) * 1000
            
            content_type = response.headers.get('content-type', '')
            
            # Check if HTML
            if not self.is_html_response(content_type):
                return {
                    'success': False,
                    'url': url,
                    'status': response.status_code,
                    'status_text': response.reason_phrase,
                    'content_type': content_type,
                    'error': 'URL does not return HTML content'
                }
            
            # Parse HTML
            parsed_data = self.parse_html(response.text, url)
            
            return {
                'success': True,
                'url': url,
                'status': response.status_code,
                'status_text': response.reason_phrase,
                'response_time': f"{response_time:.0f}ms",
                'content_type': content_type,
                'timestamp': time.strftime("%Y-%m-%d %H:%M:%S %Z"),
                **parsed_data
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
        
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error for URL {url}: {e.response.status_code}")
            return {
                'success': False,
                'url': url,
                'status': e.response.status_code,
                'status_text': e.response.reason_phrase,
                'error': f'Server responded with status {e.response.status_code}'
            }
        
        except Exception as e:
            logger.error(f"Unexpected error for URL {url}: {str(e)}")
            return {
                'success': False,
                'url': url,
                'error': 'An unexpected error occurred. Please try again.'
            }