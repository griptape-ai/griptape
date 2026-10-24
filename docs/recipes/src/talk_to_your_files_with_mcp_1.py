import tempfile
from pathlib import Path

from griptape.structures import Agent
from griptape.tools.mcp.sessions import StdioConnection
from griptape.tools.mcp.tool import MCPTool

# Create a small folder of notes for the Agent to work with.
notes_dir = Path(tempfile.mkdtemp()).resolve()
(notes_dir / "standup-monday.md").write_text("- Shipped the login page\n- Blocked on API keys for staging\n")
(notes_dir / "standup-tuesday.md").write_text("- Got the staging API keys\n- Started on password reset\n")

# Launch MCP's reference filesystem server, limited to the notes folder.
# https://github.com/modelcontextprotocol/servers/tree/main/src/filesystem
filesystem_connection: StdioConnection = {  # pyright: ignore[reportAssignmentType]
    "transport": "stdio",
    "command": "npx",
    "args": ["-y", "@modelcontextprotocol/server-filesystem", str(notes_dir)],
}

# MCPTool asks the server for its tools and turns each one into an activity.
filesystem_tool = MCPTool(connection=filesystem_connection)
print("Activities from the server:", [filesystem_tool.activity_name(a) for a in filesystem_tool.activities()])

agent = Agent(tools=[filesystem_tool])
agent.run(f"Read every note in {notes_dir}, then write a three line summary of the week to {notes_dir / 'summary.md'}.")

print((notes_dir / "summary.md").read_text())
