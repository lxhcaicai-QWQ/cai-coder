import os

from langchain.agents import create_agent
from langchain.agents.middleware import TodoListMiddleware, ToolRetryMiddleware, ModelRetryMiddleware
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import Checkpointer

from .middleware import SkillMiddleware
from .tools import (
    get_weather,
    read_file,
    write_file,
    ls,
    bash,
    http_request,
    http_get,
    http_post
)
from .prompt import construct_system_prompt

_REQUIRED_ENV_VARS = ("OPENAI_BASE_URL", "OPENAI_API_KEY", "OPENAI_MODEL")


def _check_env_vars() -> None:
    missing = [var for var in _REQUIRED_ENV_VARS if not os.getenv(var)]
    if missing:
        raise EnvironmentError(
            f"Missing required environment variable(s): {', '.join(missing)}. "
            "Please set them in .local.env or your shell environment."
        )


def _build_llm() -> ChatOpenAI:
    _check_env_vars()
    return ChatOpenAI(
        model=os.getenv("OPENAI_MODEL"),
        base_url=os.getenv("OPENAI_BASE_URL"),
        api_key=os.getenv("OPENAI_API_KEY"),
        temperature=0.7,
    )

def get_agent(checkpointer: Checkpointer = InMemorySaver()):
    return create_agent(
        model=_build_llm(),
        system_prompt=construct_system_prompt(),
        tools=[
            get_weather,
            read_file,
            write_file,
            ls,
            bash,
            http_request,
            http_get,
            http_post
        ],
        middleware=[
            SkillMiddleware(),
            TodoListMiddleware(),
            ToolRetryMiddleware(
                max_retries=3,
                initial_delay=1.0,  # 第一次重试前的初始延迟（以秒为单位）
                backoff_factor=2.0 # 指数退避乘数。每次重试等待 initial_delay * (backoff_factor ** retry_number) 秒。
            ),
            ModelRetryMiddleware(
                max_retries=3,
                initial_delay=1.0,  # 第一次重试前的初始延迟（以秒为单位）
                backoff_factor=2.0  # 指数退避乘数。每次重试等待 initial_delay * (backoff_factor ** retry_number) 秒。
            )
        ],
        checkpointer=checkpointer
    )
