from typing import Callable, Awaitable

from langchain.agents.middleware import AgentMiddleware, ModelRequest, ModelResponse
from langchain_core.messages import SystemMessage

from agent.memory.manager import MemoryManager
from agent.memory.templates import MEMORY_CONTEXT_PROMPT


class MemoryMiddleware(AgentMiddleware):
    """Middleware that injects memory context (L2 + L3 summary) into the system prompt."""

    def __init__(self, memory_manager: MemoryManager):
        self.memory_manager = memory_manager

    def wrap_model_call(
        self,
        request: ModelRequest,
        handler: Callable[[ModelRequest], ModelResponse],
    ) -> ModelResponse:
        memory_context = self.memory_manager.get_memory_context()
        if not memory_context.strip():
            return handler(request)

        addendum = MEMORY_CONTEXT_PROMPT + memory_context
        new_content = list(request.system_message.content_blocks) + [
            {"type": "text", "text": addendum}
        ]
        new_system_message = SystemMessage(content=new_content)
        modified_request = request.override(system_message=new_system_message)
        return handler(modified_request)

    async def awrap_model_call(
        self,
        request: ModelRequest,
        handler: Callable[[ModelRequest], Awaitable[ModelResponse]],
    ) -> ModelResponse:
        memory_context = self.memory_manager.get_memory_context()
        if not memory_context.strip():
            return await handler(request)

        addendum = MEMORY_CONTEXT_PROMPT + memory_context
        new_content = list(request.system_message.content_blocks) + [
            {"type": "text", "text": addendum}
        ]
        new_system_message = SystemMessage(content=new_content)
        modified_request = request.override(system_message=new_system_message)
        return await handler(modified_request)