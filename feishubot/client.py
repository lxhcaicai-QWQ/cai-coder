"""
cai-coder Web API 客户端
"""
import httpx
import json
from typing import List, Dict, Any, Optional
from config import FeishuBotConfig


class CaiCoderClient:
    """cai-coder Web API 客户端"""

    def __init__(self):
        self.api_url = FeishuBotConfig.CAICODER_API_URL
        self.api_key = FeishuBotConfig.CAICODER_API_KEY
        self.session_history: Dict[str, List[Dict[str, str]]] = {}

    def _build_headers(self) -> Dict[str, str]:
        """构建请求头"""
        headers = {
            "Content-Type": "application/json"
        }
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers

    def _build_messages(self, session_id: str, user_message: str) -> List[Dict[str, str]]:
        """构建消息列表（包含历史消息）"""
        messages = []

        # 添加系统提示
        messages.append({
            "role": "system",
            "content": "你是一个 AI 编程助手，可以帮助用户解决编程问题、编写代码、调试程序等。"
        })

        # 添加历史消息
        if session_id in self.session_history:
            messages.extend(self.session_history[session_id])

        # 添加当前用户消息
        messages.append({
            "role": "user",
            "content": user_message
        })

        return messages

    async def chat(
        self,
        session_id: str,
        user_message: str,
        stream: bool = False
    ) -> str:
        """
        与 cai-coder 对话

        Args:
            session_id: 会话 ID（用于记忆上下文）
            user_message: 用户消息
            stream: 是否使用流式响应

        Returns:
            助手回复
        """
        try:
            # 构建请求
            request_data = {
                "model": "cai-coder",
                "messages": self._build_messages(session_id, user_message),
                "stream": stream
            }

            # 发送请求
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    self.api_url,
                    headers=self._build_headers(),
                    json=request_data
                )
                response.raise_for_status()

                # 解析响应
                result = response.json()

                # 提取助手回复
                assistant_message = result["choices"][0]["message"]["content"]

                # 更新会话历史
                self._update_history(session_id, user_message, assistant_message)

                return assistant_message

        except httpx.HTTPError as e:
            print(f"调用 cai-coder API 失败: {e}")
            return f"抱歉，调用 cai-coder API 时出错：{str(e)}"
        except Exception as e:
            print(f"处理消息时出错: {e}")
            return f"抱歉，处理消息时出错：{str(e)}"

    def _update_history(self, session_id: str, user_message: str, assistant_message: str):
        """
        更新会话历史

        Args:
            session_id: 会话 ID
            user_message: 用户消息
            assistant_message: 助手回复
        """
        # 初始化会话历史
        if session_id not in self.session_history:
            self.session_history[session_id] = []

        # 添加消息对
        self.session_history[session_id].append({
            "role": "user",
            "content": user_message
        })
        self.session_history[session_id].append({
            "role": "assistant",
            "content": assistant_message
        })

        # 限制历史长度（最多保留最近 20 条消息）
        if len(self.session_history[session_id]) > 20:
            self.session_history[session_id] = self.session_history[session_id][-20:]

    def clear_session(self, session_id: str):
        """清除会话历史"""
        if session_id in self.session_history:
            del self.session_history[session_id]

    def get_all_sessions(self) -> List[str]:
        """获取所有会话 ID"""
        return list(self.session_history.keys())
