"""
Cai-Coder API Client
"""
import requests
from typing import List, Dict, Any, AsyncGenerator
import json


class CaiCoderClient:
    """Client for interacting with Cai-Coder Web API"""

    def __init__(
        self,
        base_url: str = "http://localhost:8000",
        model: str = "cai-coder",
        stream: bool = False
    ):
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.stream = stream

    def health_check(self) -> bool:
        """Check if Cai-Coder API is healthy"""
        try:
            response = requests.get(f"{self.base_url}/health", timeout=5)
            return response.status_code == 200
        except Exception:
            return False

    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        session_id: str = "default",
        temperature: float = 0.7,
        max_tokens: int = None
    ) -> Dict[str, Any]:
        """
        Send chat completion request to Cai-Coder API

        Args:
            messages: List of message dicts with 'role' and 'content'
            session_id: Unique session identifier for conversation memory
            temperature: Sampling temperature (0.0 to 2.0)
            max_tokens: Maximum tokens to generate

        Returns:
            Response dict with 'content' and other metadata
        """
        try:
            payload = {
                "model": self.model,
                "messages": messages,
                "temperature": temperature,
                "stream": self.stream
            }

            if max_tokens:
                payload["max_tokens"] = max_tokens

            response = requests.post(
                f"{self.base_url}/v1/chat/completions",
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=60
            )

            response.raise_for_status()
            data = response.json()

            return {
                "content": data["choices"][0]["message"]["content"],
                "finish_reason": data["choices"][0]["finish_reason"],
                "usage": data.get("usage", {}),
                "id": data["id"]
            }

        except requests.RequestException as e:
            return {
                "error": f"API request failed: {str(e)}",
                "content": "抱歉，AI 服务暂时不可用，请稍后再试。"
            }
        except (KeyError, json.JSONDecodeError) as e:
            return {
                "error": f"Invalid API response: {str(e)}",
                "content": "抱歉，服务返回了异常响应。"
            }

    async def stream_chat_completion(
        self,
        messages: List[Dict[str, str]],
        session_id: str = "default",
        temperature: float = 0.7
    ) -> AsyncGenerator[str, None]:
        """
        Stream chat completion response from Cai-Coder API

        Args:
            messages: List of message dicts with 'role' and 'content'
            session_id: Unique session identifier
            temperature: Sampling temperature

        Yields:
            Content chunks as they arrive
        """
        try:
            payload = {
                "model": self.model,
                "messages": messages,
                "temperature": temperature,
                "stream": True
            }

            async with requests.AsyncRequest() as session:
                async with session.post(
                    f"{self.base_url}/v1/chat/completions",
                    json=payload,
                    headers={"Content-Type": "application/json"}
                ) as response:
                    response.raise_for_status()

                    async for line in response.aiter_lines():
                        if line.startswith("data: "):
                            data_str = line[6:]  # Remove "data: " prefix
                            if data_str == "[DONE]":
                                break
                            try:
                                data = json.loads(data_str)
                                delta = data.get("choices", [{}])[0].get("delta", {})
                                content = delta.get("content", "")
                                if content:
                                    yield content
                            except json.JSONDecodeError:
                                continue

        except Exception as e:
            yield f"\n\n[错误: 流式传输失败 - {str(e)}]"
