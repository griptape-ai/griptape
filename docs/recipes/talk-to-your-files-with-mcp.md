[MCPTool](../griptape-framework/tools/official-tools/index.md#mcp) lets an Agent use the tools exposed by any [Model Context Protocol](https://modelcontextprotocol.io) server.
In this example, we'll connect it to MCP's reference [filesystem server](https://github.com/modelcontextprotocol/servers/tree/main/src/filesystem), limit that server to a folder of notes, and have an Agent read the notes and write a summary back to the same folder.

!!! important

    The filesystem server is started with `npx`, so [Node.js](https://nodejs.org) needs to be installed.

!!! tip

    The filesystem server can only touch the directories passed to it as arguments. Point it at the folders you want the Agent to see and nothing else.

```python
--8<-- "docs/recipes/src/talk_to_your_files_with_mcp_1.py"
```
