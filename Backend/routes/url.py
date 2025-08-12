"""
URL Shouter API Routes.

This module defines the APi endpoints for creating and managingn shortened URLs.
"""
import secrets
import string
from fastapi import APIRouter, HTTPException, status
from fastapi.responses import RedirectResponse

from Backend.models.models import URLBase
from Backend.core.logger import log
from Backend.core.alerter import send_telegram_alert


router = APIRouter(
    tags=["URL Shortener"],
    prefix="/api/v1"
)

db_url = {}

def generate_unique_short_code(length: int = 6) -> str:
    """Generate a random, unique Short code."""
    character = string.ascii_letters + string.digits
    while True:
        short_code = "".join(secrets.choice(character) for _ in range(length))
        if short_code not in db_url:
            return short_code
        
        
@router.post("/shorten", status_code=status.HTTP_201_CREATED)
async def create_short_url(url_data: URLBase):
    """
    Creates a new shortened URL.
    
    Receives a long URL, generate a unique short code, stores the mapping,
    and returns the shortened URl.
    """
    log.info(f"Received request to shorten URL: {url_data.url}")
    short_code = generate_unique_short_code()
    db_url[short_code] = url_data.url
    
    base_url = "http://127.0.0.1:8000"
    shortened_url = f"{base_url}/r/{short_code}"
    
    log.info(f"Successfully created short_code '{short_code}' for URL '{url_data.url}'")
    
    return {
        "original_url": url_data.url,
        "shortened_url": shortened_url
    }
    

@router.get("/r/{short_code}")
async def redirect_to_original_url(short_code: str):
    """
    Redirects to the original URL.
    
    Looks up the short code in the dabase and, if found, returns an
    HTTP 307 Temporary Redirect to the original URL. if not found,
    it returns a 404 Not found error.
    """
    log.info(f"Redirect request for short_code: {short_code}")
    original_url = db_url.get(short_code)
    
    if not original_url:
        log.warning(f"Short_code not found: {short_code}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Short URL not found."
        )
        
        log.info(f"Redirecting {short_code} to {original_url}")
        return RedirectResponse(
            url=original_url,
            status_code=status.HTTP_307_TEMPORARY_REDIRECT
        )