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
    description="RAG Expert Agent - Structure to invoke with natural language queries about the topic of Retrieval Augmented Generation",
    api_key=api_key,
    structure_id=structure_id,
    off_prompt=False,
)

# Set up an agent using the GriptapeCloudStructureRunClient tool
agent = Agent(
    tools=[structure_run_tool]
)

# Task: Ask the Griptape Cloud Hosted Structure about modular RAG
agent.run(
    "what is modular RAG?"
)
```
```
[05/02/24 11:36:16] INFO     ToolkitTask 0d99b986140a42c0828215cbc42156e8                                                                    
                             Input: what is modular RAG?                                                                                     
[05/02/24 11:36:24] INFO     Subtask b498fb971198476a83ba1a555ff4fb98                                                                        
                             Thought: To provide an explanation of what modular RAG (Retrieval Augmented Generation) is, I will use the      
                             GriptapeCloudStructureRunClient to execute a Structure Run that can provide information on this topic.          
                                                                                                                                             
                             Actions: [                                                                                                      
                               {                                                                                                             
                                 "name": "GriptapeCloudStructureRunClient",                                                                  
                                 "path": "execute_structure_run",                                                                            
                                 "input": {                                                                                                  
                                   "values": {                                                                                               
                                     "args": ["What is modular RAG?"]                                                                        
                                   }                                                                                                         
                                 },                                                                                                          
                                 "tag": "modular_rag_info"                                                                                   
                               }                                                                                                             
                             ]                                                                                                               
[05/02/24 11:37:28] INFO     Subtask b498fb971198476a83ba1a555ff4fb98                                                                        
                             Response: {'id': 'ea96fc6f92f9417880938ff59273be59', 'name': 'ea96fc6f92f9417880938ff59273be59', 'type':        
                             'TextArtifact', 'value': "Modular RAG is an advanced architecture that builds upon the foundational principles  
                             of Advanced and Naive RAG paradigms. It offers enhanced adaptability and versatility by incorporating diverse   
                             strategies to improve its components. Modular RAG introduces additional specialized components like the Search  
                             module for direct searches across various data sources, the RAG-Fusion module for expanding user queries into   
                             diverse perspectives, and the Memory module to guide retrieval using the LLM's memory. This approach supports   
                             both sequential processing and integrated end-to-end training across its components, illustrating progression   
                             and refinement within the RAG family."}                                                                         
[05/02/24 11:37:40] INFO     ToolkitTask 0d99b986140a42c0828215cbc42156e8                                                                    
                             Output: Modular RAG is an advanced architecture that builds upon the foundational principles of Advanced and    
                             Naive RAG paradigms. It offers enhanced adaptability and versatility by incorporating diverse strategies to     
                             improve its components. Modular RAG introduces additional specialized components like the Search module for     
                             direct searches across various data sources, the RAG-Fusion module for expanding user queries into diverse      
                             perspectives, and the Memory module to guide retrieval using the LLM's memory. This approach supports both      
                             sequential processing and integrated end-to-end training across its components, illustrating progression and    
                             refinement within the RAG family.                                                                               
Assistant: Modular RAG is an advanced architecture that builds upon the foundational principles of Advanced and Naive RAG paradigms. It offers enhanced adaptability and versatility by incorporating diverse strategies to improve its components. Modular RAG introduces additional specialized components like the Search module for direct searches across various data sources, the RAG-Fusion module for expanding user queries into diverse perspectives, and the Memory module to guide retrieval using the LLM's memory. This approach supports both sequential processing and integrated end-to-end training across its components, illustrating progression and refinement within the RAG family.
```