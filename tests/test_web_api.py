from fastapi.testclient import TestClient

from agent.webapp import app

client = TestClient(app)


def test_get_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

def test_list_models():
    response = client.get("/v1/models")
    assert response.status_code == 200
    assert response.json() == {
        "object": "list",
        "data": [
            {
                "id": "cai-coder",
                "object": "model",
                "created": 1687882410,
                "owned_by": "cai-coder"
            }
        ]
    }