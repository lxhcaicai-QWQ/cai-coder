import uuid

from langchain_mcp_adapters.client import MultiServerMCPClient
from agent import server

async def test_agent_mcp_tools():

    client = MultiServerMCPClient(
        {
            "langchain_docs": {
                "transport": "http",  # HTTP-based remote server
                "url": "https://docs.langchain.com/mcp"
            }
        }
    )

    tools = await client.get_tools()
    agent = server.get_agent(mcptools=tools)
    config = {"configurable": {"thread_id": str(uuid.uuid4())  }}
    response = await agent.ainvoke({"messages": [{"role": "user", "content": "what is the LangGraph overview?"}]}, config=config)
    assert response["messages"][-1].content is not None
    print(response["messages"][-1].content)