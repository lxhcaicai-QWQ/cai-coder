from pathlib import Path
from agent import server

def test_agent_get_weather() -> None:
    agent = server.get_agent()
    response = agent.invoke({"messages": [{"role": "user", "content": "what is the weather in shenzhen?"}]})
    assert response["messages"][-1].content is not None

def test_agent_read_file() -> None:
    path = str(Path(__file__).parent / 'file/a.txt')
    content = f"What content in this path {path}"
    agent = server.get_agent()
    response = agent.invoke({"messages": [{"role": "user", "content": content}]})
    assert response["messages"][-1].content is not None
    print(response["messages"][-1].content)

def test_agent_write_file() -> None:
    path = str(Path(__file__).parent / 'file/c.txt')
    content = f"Help me write the content [I love you forever!] to {path}"
    agent = server.get_agent()
    response = agent.invoke({"messages": [{"role": "user", "content": content}]})
    assert response["messages"][-1].content is not None
    print(response["messages"][-1].content)

def test_agent_ls() -> None:
    path = str(Path(__file__).parent / 'file')
    content = f"What files are in this path {path}?"
    agent = server.get_agent()
    response = agent.invoke({"messages": [{"role": "user", "content": content}]})
    assert response["messages"][-1].content is not None
    print(response["messages"][-1].content)

def test_agent_bash_time() -> None:
    agent = server.get_agent()
    response = agent.invoke({"messages": [{"role": "user", "content": "what time now in this computer?"}]})
    assert response["messages"][-1].content is not None
    print(response["messages"][-1].content)