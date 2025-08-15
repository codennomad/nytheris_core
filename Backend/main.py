"""
Main Application File.
This file initializes the FastAPI application, includes the API routers,
and configures CORS middleware.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware # <-- 1. Adicione este import
from Backend.routes import url as url_router

# --- App Initialization ---
app = FastAPI(
    title="Encurtador de Links",
    description="Projeto moderno para encurtar links com FastAPI.",
    version="1.0.0"
)

# --- CORS Middleware Configuration ---
# 2. Adicione este bloco de código
origins = [
    "*", # Permite todas as origens. Em produção, restrinja isso!
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"], # Permite todos os métodos (GET, POST, etc)
    allow_headers=["*"], # Permite todos os cabeçalhos
)

# --- Include Routers ---
app.include_router(url_router.router)

# --- Root Endpoint ---
@app.get("/", tags=["Root"])
def read_root():
    """Welcome endpoint."""
    return {"message": "Welcome to the URL Shortener API!"}