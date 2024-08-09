from pathlib import Path

from griptape.structures import Agent
from griptape.tools import FileManager

# Initialize the FileManager tool with the current directory as its base
file_manager_tool = FileManager()

# Add the tool to the Agent
agent = Agent(tools=[file_manager_tool])

# Directly create a file named 'sample1.txt' with some content
filename = "sample1.txt"
content = "This is the content of sample1.txt"

Path(filename).write_text(filename)

# Now, read content from the file 'sample1.txt' using the agent's command
agent.run("Can you get me the sample1.txt file?")
