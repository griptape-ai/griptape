from griptape.tools.mcp.sessions import StdioConnection
from griptape.tools.mcp.tool import MCPTool
from griptape.structures import Agent

# Create a Connection to the MCP server.
# This example uses MCP's everything demo server: https://github.com/modelcontextprotocol/servers/tree/main/src/everything
everything_connection: StdioConnection = {
        "transport": "stdio",
        "command": "npx",
        "args": [
                "-y",
                "@modelcontextprotocol/server-everything"
        ]
}

# Create a tool configured to use the MCP server.
mcp_tool = MCPTool(
        connection=everything_connection
)

Agent(tools=[mcp_tool]).run("Add 17 and 25 together and return the result.")
