"""
Pydantic Models for Data Validation.

This module defines the pydantic models that are used for request and response data validation throunghout the application.
"""
from pydantic import BaseModel, Field
from typing import Optional
from sqlalchemy import Column, Integer, String, DateTime, func, Index
from Backend.core.database import Base

class URLBase(BaseModel):
    """
    Base Model for a URL.
    Atributes:
        url(str): The URL to be processed.
    """
    url: str
    password: Optional[str] = None
    max_clicks: Optional[int] = 0
    custom_alias: Optional[str] = Field(None, max_length=30, pattern=r'^[a-zA-Z0-9_-]+$')
    
class URL(Base):
    """
    SQLAlchemy ORM model for a shortened URL.
    """
    __tablename__="urls"
    
    id = Column(Integer, primary_key=True, index=True)
    short_code = Column(String, unique=True, index=True, nullable=False)
    original_url = Column(String, nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    password = Column(String, nullable=True)
    max_clicks = Column(Integer, default=0)
    current_clicks = Column(Integer, default=0, nullable=False)
    
# Adiciona um índice explícito para a coluna short_code para otimizar buscas.
Index("ix_urls_short_code", "short_code", unique=True)


class URLPasswordRequest(BaseModel):
    """Model for the password submission request."""
    password: str