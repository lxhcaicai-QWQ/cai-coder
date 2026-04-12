import os

from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import InMemorySaver

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


memory = InMemorySaver()


def get_agent():
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
        middleware=[SkillMiddleware()],
        checkpointer=memory
    )
