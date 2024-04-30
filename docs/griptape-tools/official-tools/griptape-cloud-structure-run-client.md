# GriptapeCloudStructureRunClient

The GriptapeCloudStructureRunClient tool provides a way to interact with the Griptape Cloud Structure Run API. It can be used to execute a Structure Run and retrieve the results.

```python
from griptape.tools import GriptapeCloudStructureRunClient
from griptape.structures import Agent
import os

api_key = os.environ["GRIPTAPE_CLOUD_API_KEY"]
structure_id = os.environ["GRIPTAPE_CLOUD_STRUCTURE_ID"]

# Create the GriptapeCloudStructureRunClient tool
structure_run_tool = GriptapeCloudStructureRunClient(
    description="Danish Baker Agent - Structure to invoke with natural language queries about Danish pastries",
    api_key=api_key,
    structure_id=structure_id,
    off_prompt=False,
)

# Set up an agent using the GriptapeCloudStructureRunClient tool
agent = Agent(
    tools=[structure_run_tool]
)

# Task: Ask the Griptape Cloud Hosted Structure about new Danish pastries
agent.run(
    "What are the new pastries?"
)
```
```
[04/29/24 20:46:14] INFO     ToolkitTask 3b3f31a123584f05be9bcb02a58dddb6                                                                    
                             Input: what are the new pastries?                                                                               
[04/29/24 20:46:23] INFO     Subtask 2740dcd92bdf4b159dc7a7fb132c98f3                                                                        
                             Thought: To find out about new pastries, I need to use the Danish Baker Agent Structure. I will execute a run of
                             this Structure with the query "what are the new pastries".                                                      
                                                                                                                                             
                             Actions: [                                                                                                      
                               {                                                                                                             
                                 "name": "GriptapeCloudStructureRunClient",                                                                  
                                 "path": "execute_structure_run",                                                                            
                                 "input": {                                                                                                  
                                   "values": {                                                                                               
                                     "args": ["what are the new pastries"]                                                                   
                                   }                                                                                                         
                                 },                                                                                                          
                                 "tag": "query_new_pastries"                                                                                 
                               }                                                                                                             
                             ]                                                                                                               
[04/29/24 20:47:01] INFO     Subtask 2740dcd92bdf4b159dc7a7fb132c98f3                                                                        
                             Response: {'id': '4a329cbd09ad42e0bd265e9ba4690400', 'name': '4a329cbd09ad42e0bd265e9ba4690400', 'type':        
                             'TextArtifact', 'value': 'Ah, my friend, I am glad you asked! We have been busy in the bakery, kneading dough   
                             and sprinkling sugar. Our new pastries include the "Copenhagen Cream Puff", a delightful puff pastry filled with
                             sweet cream and dusted with powdered sugar. We also have the "Danish Delight", a buttery croissant filled with  
                             raspberry jam and topped with a drizzle of white chocolate. And let\'s not forget the "Nordic Nutella Twist", a 
                             flaky pastry twisted with Nutella and sprinkled with chopped hazelnuts. I promise, each bite will transport you 
                             to a cozy Danish bakery!'}                                                                                      
[04/29/24 20:47:07] INFO     ToolkitTask 3b3f31a123584f05be9bcb02a58dddb6                                                                    
                             Output: The new pastries include the "Copenhagen Cream Puff," which is a puff pastry filled with sweet cream and
                             dusted with powdered sugar; the "Danish Delight," a buttery croissant filled with raspberry jam and topped with 
                             white chocolate; and the "Nordic Nutella Twist," a flaky pastry twisted with Nutella and sprinkled with chopped 
                             hazelnuts.                                                                                                      
Assistant: The new pastries include the "Copenhagen Cream Puff," which is a puff pastry filled with sweet cream and dusted with powdered sugar; the "Danish Delight," a buttery croissant filled with raspberry jam and topped with white chocolate; and the "Nordic Nutella Twist," a flaky pastry twisted with Nutella and sprinkled with chopped hazelnuts.
```