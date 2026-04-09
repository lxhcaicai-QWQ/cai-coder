import os

from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import InMemorySaver

from .tools import (
    get_weather,
    read_file,
    write_file,
    ls,
    bash
)
from .prompt import construct_system_prompt

#==================================

BASE_URL = os.getenv("OPENAI_BASE_URL")      # 例如 https://api.your-service.com/v1
API_KEY = os.getenv("OPENAI_API_KEY")
MODEL_NAME = os.getenv("OPENAI_MODEL")

llm = ChatOpenAI(
    model=MODEL_NAME,           # 模型名，会透传给服务端
    base_url=BASE_URL,          # 自定义 base_url
    api_key=API_KEY,            # 你的 API key
    temperature=0.7
    # max_tokens=..., timeout=..., 其他参数也可以直接写
)

#==================================

memory = InMemorySaver()

def get_agent():
    return create_agent(
        model=llm,
        system_prompt=construct_system_prompt(),
        tools=[
            get_weather,
            read_file,
            write_file,
            ls,
            bash
        ],
        checkpointer=memory
    )