"""
URL Shouter API Routes.

This module defines the APi endpoints for creating and managingn shortened URLs.
"""
import secrets
import string
from fastapi import APIRouter, HTTPException, status, Depends 
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session 
from redis import Redis

from Backend.models.models import URLBase, URLPasswordRequest 

from Backend.models.models import URL
from Backend.core.database import get_db
from Backend.core.cache import get_cache
from Backend.core.logger import log
from Backend.core import security
from Backend.core.messaging import publish_click_event


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
def create_short_url(url_data: URLBase, db: Session = Depends(get_db)):
    """
    Creates a new shortened URL.
    
    Receives a long URL, generate a unique short code, stores the mapping,
    and returns the shortened URl.
    """
    try:
        short_code: str
        if url_data.custom_alias:
            # --- LÓGICA PARA APELIDO CUSTOMIZADO ---
            log.info(f"Custom alias provided: '{url_data.custom_alias}'")
            # 1. Verificar se o apelido já está em uso
            existing_url = db.query(url_model.URL).filter(url_model.URL.short_code == url_data.custom_alias).first()
            if existing_url:
                log.warning(f"Custom alias '{url_data.custom_alias}' already exists.")
                # O código de status HTTP 409 Conflict é perfeito para isso.
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Custom alias already in use.")
            short_code = url_data.custom_alias
        else:
            # --- LÓGICA PADRÃO (FALLBACK) ---
            # Se nenhum apelido for fornecido, gere um aleatório.
            short_code = generate_unique_short_code(db)
            log.info(f"Generated random short code: '{short_code}'")

        hashed_password = None
        if url_data.password:
            hashed_password = security.hash_password(url_data.password)
            log.info(f"Password provided for '{short_code}'. Hashing it.")

        db_url = url_model.URL(
            original_url=url_data.url,
            short_code=short_code,
            password=hashed_password,
            max_clicks=url_data.max_clicks or 0
        )
        db.add(db_url)
        db.commit()
        db.refresh(db_url)

        base_url = "http://localhost:8000"
        shortened_url = f"{base_url}/r/{short_code}"

        return { "message": "URL shortened successfully!", "short_url": shortened_url }

    except HTTPException as http_exc:
        # Re-levanta exceções HTTP para que o FastAPI as capture corretamente
        raise http_exc
    except Exception as e:
        log.error(f"Error creating short URL: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Internal Server Error")
    

@router.get("/r/{short_code}")
def redirect_to_original_url(
    short_code: str,
    db: Session = Depends(get_db)
):
    """
    Redirects to the original URL after checking business rules.
    On success, it publishes a click event to RabbitMQ instead of
    updating the counter directly.
    """
    db_url = db.query(url_model.URL).filter(url_model.URL.short_code == short_code).first()

    if not db_url:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="URL not found")

    # --- LÓGICA DE VERIFICAÇÃO ---
    if db_url.max_clicks > 0 and db_url.current_clicks >= db_url.max_clicks:
        log.warning(f"URL '{short_code}' has reached its click limit.")
        raise HTTPException(status_code=410, detail="URL has expired")

    if db_url.password:
        log.warning(f"URL '{short_code}' is password protected.")
        raise HTTPException(status_code=401, detail="Password required to access this URL")

    # --- LÓGICA DE PUBLICAÇÃO ASSÍNCRONA ---
    # Em vez de 'db.commit()', publicamos o evento.
    if publish_click_event(short_code):
        log.info(f"Click event for '{short_code}' published successfully.")
    else:
        log.error(f"FAILED to publish click event for '{short_code}'.")

    return RedirectResponse(url=db_url.original_url, status_code=status.HTTP_307_TEMPORARY_REDIRECT)


@router.post("/verify/{short_code}", status_code=status.HTTP_200_OK)
def verify_password_and_get_url(
    short_code: str,
    request_data: URLPasswordRequest,
    db: Session = Depends(get_db)
):
    """
    Verifies the password for a protected URL. On success, it publishes
    a click event and returns the original URL.
    """
    db_url = db.query(url_model.URL).filter(url_model.URL.short_code == short_code).first()

    if not db_url:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="URL not found")

    if not db_url.password:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="This URL is not password-protected")

    if not security.verify_password(request_data.password, db_url.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid password")

    if db_url.max_clicks > 0 and db_url.current_clicks >= db_url.max_clicks:
        log.warning(f"URL '{short_code}' has reached its click limit even with correct password.")
        raise HTTPException(status_code=status.HTTP_410_GONE, detail="URL has expired")

    # --- LÓGICA DE PUBLICAÇÃO ASSÍNCRONA ---
    # Se tudo passou, publicamos o evento em vez de incrementar o clique aqui.
    if publish_click_event(short_code):
        log.info(f"Password verified for '{short_code}'. Publishing click event.")
    else:
        log.error(f"FAILED to publish click event for '{short_code}' after password verification.")

    return {"original_url": db_url.original_url}