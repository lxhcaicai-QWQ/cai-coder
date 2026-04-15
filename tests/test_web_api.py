from typing import List, Optional

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

def test_chat_completion():
    def chat_completion(
            messages: List[dict],
            model: str = "cai-coder",
            temperature: float = 0.7,
            max_tokens: Optional[int] = None,
            stream: bool = False
    ) -> dict:
        """
        Create a chat completion

        Args:
            messages: List of message dicts with 'role' and 'content'
            model: Model identifier
            temperature: Sampling temperature (0.0-2.0)
            max_tokens: Maximum tokens to generate
            stream: Whether to stream the response
        """
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "stream": stream
        }

        if max_tokens:
            payload["max_tokens"] = max_tokens

        response = client.post("/v1/chat/completions",json=payload,headers={"Content-Type": "application/json"})
        return response.json()

    # Chat completion
    messages = [
        {"role": "system", "content": "You are a helpful AI assistant."},
        {"role": "user", "content": "What is the capital of France?"}
    ]
    response = chat_completion(messages=messages)
    assert response["choices"][0]["message"]["content"] is not None
    assert response["model"] == "cai-coder"
    assert "chatcmpl" in response["id"]
    assert isinstance(response["created"], int)
    assert isinstance(response["usage"]["prompt_tokens"], int)
    assert isinstance(response["usage"]["completion_tokens"], int)
    assert isinstance(response["usage"]["total_tokens"], int)


