from griptape.structures import Agent
from griptape.tools import ComputerTool

# Initialize the ComputerTool tool
computer = ComputerTool()

# Create an agent with the ComputerTool tool
agent = Agent(tools=[computer])

# Create a file using the shell command
filename = "my_new_file.txt"
agent.run(f"Run this shell command for me: touch {filename}")

# Add content to the file using the shell command
content = "This is the content of the file."
agent.run(f"Run this shell command for me: echo '{content}' > {filename}")

# Output the contents of the file using the shell command
agent.run(f"Run this shell command for me: cat {filename}")
