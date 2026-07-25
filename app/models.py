# app/models.py
from pydantic import BaseModel, HttpUrl
from typing import Optional

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