from agent import server

def test_agent_get_weather() -> None:
    agent = server.get_agent()
    response = agent.invoke({"messages": [{"role": "user", "content": "what is the weather in shenzhen?"}]})
    assert response["messages"][-1].content != None