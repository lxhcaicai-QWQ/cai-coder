import json
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


def test_chat_completion_stream():
    def chat_completion_stream(
        messages: List[dict],
        model: str = "cai-coder",
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ):
        """
        Create a streaming chat completion

        Yields chunks of the response as they arrive.
        """
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "stream": True
        }

        if max_tokens:
            payload["max_tokens"] = max_tokens

        with client.stream("POST", "/v1/chat/completions", json=payload, headers={"Content-Type": "application/json"}) as response:
            for line in response.iter_lines():
                # print(line, end="", flush=True)

                if line.startswith('data: '):
                    data = line[6:]  # Remove 'data: ' prefix
                    if data == '[DONE]':
                        break
                    completion_chunk = json.loads(data)
                    assert completion_chunk["model"] == "cai-coder"
                    assert "chatcmpl" in completion_chunk["id"]
                    assert completion_chunk["choices"][0] is not None





    messages = [
        {"role": "system", "content": "You are a helpful AI assistant."},
        {"role": "user", "content": "What is the capital of France?"}
    ]
    chat_completion_stream(messages=messages)


def test_openai_client():
    from openai import OpenAI
    from agent import webapp
    from tenacity import sleep
    import threading

    """Start the FastAPI service in a background thread"""
    def run():
        webapp.start(host="localhost", port=8888)

    thread = threading.Thread(target=run, daemon=True)
    thread.start()
    sleep(2)

    try:
        openai_client = OpenAI(
            base_url="http://localhost:8888/v1",
            api_key="dummy-key"  # API key is not used but required by library
        )


        messages = [
            {"role": "system", "content": "You are a helpful AI assistant."},
            {"role": "user", "content": "how are you!"}
        ]

        response = openai_client.chat.completions.create(
            model="cai-coder",
            messages=messages,
            temperature=0.7
        )
        print(f"Response: {response.choices[0].message.content}")
    except Exception as e:
        print(f"Error: {e}")
        raise e