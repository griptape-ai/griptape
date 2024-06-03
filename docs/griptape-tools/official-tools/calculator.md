# Calculator

This tool enables LLMs to make simple calculations.

```python
from griptape.structures import Agent
from griptape.tools import Calculator

# Create an agent with the Calculator tool
agent = Agent(
    tools=[Calculator()]
)

# Run the agent with a task to perform the arithmetic calculation of \(10^5\)
agent.run("What is 10 raised to the power of 5?")
```
```
[09/08/23 14:23:51] INFO     Task bbc6002a5e5b4655bb52b6a550a1b2a5              
                             Input: What is 10 raised to the power of 5?        
[09/08/23 14:23:56] INFO     Subtask 3e9211a0f44c4277812ae410c43adbc9           
                             Thought: The question is asking for the result of  
                             10 raised to the power of 5. This is a mathematical
                             operation that can be performed using the          
                             Calculator tool.                                   
                                                                                
                             Action: {"name": "Calculator",     
                             "path": "calculate", "input": {"values":       
                             {"expression": "10**5"}}}                          
                    INFO     Subtask 3e9211a0f44c4277812ae410c43adbc9           
                             Response: 100000                                
[09/08/23 14:23:58] INFO     Task bbc6002a5e5b4655bb52b6a550a1b2a5              
                             Output: 10 raised to the power of 5 is 100000.  
```
