import uuid
from pathlib import Path
from agent import server

def test_agent_get_weather() -> None:
    config = {"configurable": {"thread_id": str(uuid.uuid4())  }}
    agent = server.get_agent()
    response = agent.invoke({"messages": [{"role": "user", "content": "what is the weather in shenzhen?"}]}, config=config)
    assert response["messages"][-1].content is not None

def test_agent_read_file() -> None:
    path = str(Path(__file__).parent / 'file/a.txt')
    content = f"What content in this path {path}"
    config = {"configurable": {"thread_id": str(uuid.uuid4())  }}
    agent = server.get_agent()
    response = agent.invoke({"messages": [{"role": "user", "content": content}]}, config=config)
    assert response["messages"][-1].content is not None
    print(response["messages"][-1].content)

def test_agent_write_file() -> None:
    path = str(Path(__file__).parent / 'file/c.txt')
    content = f"Help me write the content [I love you forever!] to {path}"
    config = {"configurable": {"thread_id": str(uuid.uuid4())  }}
    agent = server.get_agent()
    response = agent.invoke({"messages": [{"role": "user", "content": content}]}, config=config)
    assert response["messages"][-1].content is not None
    print(response["messages"][-1].content)

def test_agent_ls() -> None:
    path = str(Path(__file__).parent / 'file')
    content = f"What files are in this path {path}?"
    config = {"configurable": {"thread_id": str(uuid.uuid4())  }}
    agent = server.get_agent()
    response = agent.invoke({"messages": [{"role": "user", "content": content}]}, config=config)
    assert response["messages"][-1].content is not None
    print(response["messages"][-1].content)

def test_agent_bash_time() -> None:
    agent = server.get_agent()
    config = {"configurable": {"thread_id": str(uuid.uuid4())  }}
    response = agent.invoke({"messages": [{"role": "user", "content": "what time now in this computer?"}]}, config=config)
    assert response["messages"][-1].content is not None
    print(response["messages"][-1].content)


# test skill
def test_agent_load_skill_description():
    agent = server.get_agent()
    config = {"configurable": {"thread_id": str(uuid.uuid4())  }}
    response = agent.invoke({"messages": [{"role": "user", "content": "Tell me what skills you have without loading"}]}, config=config)
    assert response["messages"][-1].content is not None
    print(response["messages"][-1].content)


def test_agent_load_skill_content():
    agent = server.get_agent()
    config = {"configurable": {"thread_id": str(uuid.uuid4())  }}
    response = agent.invoke({"messages": [{"role": "user", "content": "Tell me what steps are involved in Python testing skills"}]}, config=config)
    assert response["messages"][-1].content is not None
    print(response["messages"][-1].content)