import json
from typing import Dict

from langchain_core.tools import BaseTool
from langchain_mcp_adapters.client import MultiServerMCPClient

from agent.utils.common_util import find_project_root

def load_mcp_json():
    def read_file(file_path: str) -> str:
        """Read the contents of a file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            return content
        except Exception:
            raise

    mcp_path = str(find_project_root() / "mcp.json")
    mcp_json = read_file(mcp_path)
    mcp: Dict = json.loads(mcp_json)
    return mcp.get("mcpServers") or {}

async def load_mcp_tools() -> list[BaseTool]:
    client = MultiServerMCPClient(load_mcp_json())
    tools = await client.get_tools()
    return tools
