# tests/test_shortener_api.py
from fastapi.testclient import TestClient

def test_create_short_url_success(client: TestClient):
    """
    Tests the successful creation of a basic shortened URL.
    """
    # Dados que enviaremos para a API
    test_payload = {"url": "https://www.google.com"}

    # Fazendo a requisição para o endpoint
    response = client.post("/api/v1/shorten", json=test_payload)

    # Verificando os resultados
    assert response.status_code == 201 # Verifica se o status é '201 Created'
    
    response_data = response.json()
    assert "message" in response_data
    assert "short_url" in response_data
    assert "/r/" in response_data["short_url"] # Verifica se a URL curta foi formatada corretamente

def test_create_short_url_with_custom_alias(client: TestClient):
    """
    Tests the successful creation of a URL with a custom alias.
    """
    alias = "my-google"
    test_payload = {"url": "https://www.google.com", "custom_alias": alias}

    response = client.post("/api/v1/shorten", json=test_payload)

    assert response.status_code == 201
    
    response_data = response.json()
    assert alias in response_data["short_url"]

def test_create_short_url_with_conflicting_alias(client: TestClient):
    """
    Tests that the API returns a 409 Conflict error when a custom alias is already in use.
    """
    # Primeiro, criamos um link com um apelido customizado
    payload_1 = {"url": "https://www.google.com", "custom_alias": "conflict-test"}
    response_1 = client.post("/api/v1/shorten", json=payload_1)
    assert response_1.status_code == 201 # Garante que o primeiro foi criado

    # Agora, tentamos criar OUTRO link com o MESMO apelido
    payload_2 = {"url": "https://www.openai.com", "custom_alias": "conflict-test"}
    response_2 = client.post("/api/v1/shorten", json=payload_2)

    # Verificamos se a API retornou o erro correto
    assert response_2.status_code == 409 # Verifica se o status é '409 Conflict'
    assert "Custom alias already in use" in response_2.json()["detail"]