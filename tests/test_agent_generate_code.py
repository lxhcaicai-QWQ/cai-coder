from pathlib import Path

from agent import server


def test_agent_generate_code() -> None:
    path = str(Path(__file__).parent / 'snake-game')
    agent = server.get_agent()
    response = agent.invoke({"messages": [{"role": "user", "content": f"帮我写个HTML的贪吃蛇游戏，代码放在{path}"}]})
    assert response["messages"][-1].content is not None
    print(response["messages"][-1].content)