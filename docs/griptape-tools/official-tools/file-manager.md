# FileManager

This tool enables LLMs to save and load files.

```python
from griptape.structures import Agent
from griptape.tools import FileManager

# Initialize the FileManager tool with the current directory as its base
file_manager_tool = FileManager()

# Add the tool to the Agent
agent = Agent(
    tools=[file_manager_tool]
)

# Directly create a file named 'sample1.txt' with some content
filename = "sample1.txt"
content = "This is the content of sample1.txt"

with open(filename, "w") as f:
    f.write(content)

# Now, read content from the file 'sample1.txt' using the agent's command
agent.run("Can you get me the sample1.txt file?")
```
```
[09/12/23 12:07:56] INFO     Task 16a1ce1847284ae3805485bad7d99116              
                             Input: Can you get me the sample1.txt file?        
[09/12/23 12:08:04] INFO     Subtask ddcf48d970ce4edbbc22a46b2f83ec4f           
                             Thought: The user wants the content of the file    
                             named "sample1.txt". I can use the FileManager tool
                             with the activity "load_files_from_disk" to load   
                             the file from the disk.                            
                                                                                
                             Action: {"name": "FileManager",    
                             "path": "load_files_from_disk", "input":       
                             {"values": {"paths": ["sample1.txt"]}}}            
                    INFO     Subtask ddcf48d970ce4edbbc22a46b2f83ec4f           
                             Response:                                       
                             [BlobArtifact(id='a715cc1bc6724bf28566a5b3c343b6ed'
                             , name='sample1.txt', type='BlobArtifact',         
                             value=b'This is the content of sample1.txt',       
                             dir='')]                                           
[09/12/23 12:08:10] INFO     Task 16a1ce1847284ae3805485bad7d99116              
                             Output: The content of the file "sample1.txt" is   
                             "This is the content of sample1.txt". 
```