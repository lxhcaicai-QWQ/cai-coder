import uuid

from agent import server
from agent.utils.mcp_util import load_mcp_json, load_mcp_tools


def test_load_mcp():
    mcp_tools = load_mcp_json()
    assert mcp_tools.get("langchain_docs") == {
        "transport": "http",  # HTTP-based remote server
        "url": "https://docs.langchain.com/mcp"
    }

async def test_agent_mcp_tools():

    mcp_tools = await load_mcp_tools()
    agent = server.get_agent(mcptools=mcp_tools)
    config = {"configurable": {"thread_id": str(uuid.uuid4())  }}
    response = await agent.ainvoke({"messages": [{"role": "user", "content": "How to use langchain deep agents in a simple way?"}]}, config=config)
    assert response["messages"][-1].content is not None
    print(response["messages"][-1].content)