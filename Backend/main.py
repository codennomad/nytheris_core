
from fastapi import FastAPI
from Backend.routes import url as url_router

app = FastAPI(
    title="Encurtador de Links",
    description="Projeto para encurtar links.",
    version="1.0.0"
)


app.include_router(url_router.router)


@app.get("/", tags=["Root"])
def read_root():
    """
    Welcome endpoint.
    
    Returns a welcome message for the API.
    """
    return {"message": "Welcome to the URL Shortener API!"}