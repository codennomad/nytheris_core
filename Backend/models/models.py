"""
Pydantic Models for Data Validation.

This module defines the pydantic models that are used for request and response data validation throunghout the application.
"""
from pydantic import BaseModel

class URLBase(BaseModel):
    """
    Base Model for a URL.
    Atributes:
        url(str): The URL to be processed.
    """
    url: str