from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver

from agent import server
from agent.utils.mcp_util import load_mcp_tools

async def run():
    config = {"configurable": {"thread_id": "1234" }}

    async with AsyncSqliteSaver.from_conn_string("../cai-coder-sqlite.db") as checkpointer:
        mcp_tools = await load_mcp_tools()
        agent = server.get_agent(checkpointer=checkpointer, mcptools=mcp_tools)

        while True:
            content = input("> ")
            if not content.strip():
                continue

            if content.strip().lower() == "exit":
                break

            async for chunk in agent.astream(
                    {"messages": [{"role": "user", "content": f"{content}"}]},
                    stream_mode=["messages"],
                    version="v2",
                    config= config
            ):
                if chunk["type"] == "messages":
                    token, metadata = chunk["data"]
                    print(token.content, end='', flush=True)

            print("\n")

if __name__ == "__main__":
    import asyncio
    asyncio.run(run())