# tests/conftest.py
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from Backend.main import app
from Backend.core.database import Base, get_db

# --- Configuração do Banco de Dados de Teste ---
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:" # Usa um DB SQLite em memória
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Cria as tabelas no DB em memória antes de rodar os testes
Base.metadata.create_all(bind=engine)

# --- Fixture para Sobrescrever a Dependência do DB ---
@pytest.fixture(scope="function")
def db_session_override():
    """
    Fixture to override the 'get_db' dependency and use the in-memory test database.
    """
    connection = engine.connect()
    transaction = connection.begin()
    db = TestingSessionLocal(bind=connection)

    yield db

    db.close()
    transaction.rollback()
    connection.close()

@pytest.fixture(scope="function")
def client(db_session_override):
    """
    Pytest fixture to provide a test client for the API.
    This client uses the isolated, in-memory database for its requests.
    """
    # Sobrescreve a dependência get_db com nossa sessão de teste
    app.dependency_overrides[get_db] = lambda: db_session_override

    with TestClient(app) as test_client:
        yield test_client

    # Limpa a sobrescrita depois que o teste termina
    app.dependency_overrides.clear()