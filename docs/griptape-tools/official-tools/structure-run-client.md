# StructureRunClient

The StructureRunClient Tool provides a way to run Structures via a Tool.
It requires you to provide a [Structure Run Driver](../../griptape-framework/drivers/structure-run-drivers.md) to run the Structure in the desired environment.

```python
import os

from griptape.drivers import GriptapeCloudStructureRunDriver
from griptape.structures import Agent
from griptape.tools import StructureRunClient

base_url = os.environ["GRIPTAPE_CLOUD_BASE_URL"]
api_key = os.environ["GRIPTAPE_CLOUD_API_KEY"]
structure_id = os.environ["GRIPTAPE_CLOUD_STRUCTURE_ID"]

structure_run_tool = StructureRunClient(
    description="RAG Expert Agent - Structure to invoke with natural language queries about the topic of Retrieval Augmented Generation",
    driver=GriptapeCloudStructureRunDriver(
        base_url=base_url,
        api_key=api_key,
        structure_id=structure_id,
    ),
    off_prompt=False,
)

# Set up an agent using the StructureRunClient tool
agent = Agent(tools=[structure_run_tool])

# Task: Ask the Griptape Cloud Hosted Structure about modular RAG
agent.run("what is modular RAG?")
```
```
[05/02/24 13:50:03] INFO     ToolkitTask 4e9458375bda4fbcadb77a94624ed64c
                             Input: what is modular RAG?
[05/02/24 13:50:10] INFO     Subtask 5ef2d72028fc495aa7faf6f46825b004
                             Thought: To answer this question, I need to run a search for the term "modular RAG". I will use the StructureRunClient action to execute a
                             search structure.
                             Actions: [
                               {
                                 "name": "StructureRunClient",
                                 "path": "run_structure",
                                 "input": {
                                   "values": {
                                     "args": "modular RAG"
                                   }
                                 },
                                 "tag": "search_modular_RAG"
                               }
                             ]
[05/02/24 13:50:36] INFO     Subtask 5ef2d72028fc495aa7faf6f46825b004
                             Response: {'id': '87fa21aded76416e988f8bf39c19760b', 'name': '87fa21aded76416e988f8bf39c19760b', 'type': 'TextArtifact', 'value': 'Modular
                             Retrieval-Augmented Generation (RAG) is an advanced approach that goes beyond the traditional RAG paradigms, offering enhanced adaptability
                             and versatility. It involves incorporating diverse strategies to improve its components by adding specialized modules for retrieval and
                             processing capabilities. The Modular RAG framework allows for module substitution or reconfiguration to address specific challenges, expanding
                             flexibility by integrating new modules or adjusting interaction flow among existing ones. This approach supports both sequential processing
                             and integrated end-to-end training across its components, illustrating progression and refinement within the RAG family.'}
[05/02/24 13:50:44] INFO     ToolkitTask 4e9458375bda4fbcadb77a94624ed64c
                             Output: Modular Retrieval-Augmented Generation (RAG) is an advanced approach that goes beyond the traditional RAG paradigms, offering enhanced
                             adaptability and versatility. It involves incorporating diverse strategies to improve its components by adding specialized modules for
                             retrieval and processing capabilities. The Modular RAG framework allows for module substitution or reconfiguration to address specific
                             challenges, expanding flexibility by integrating new modules or adjusting interaction flow among existing ones. This approach supports both
                             sequential processing and integrated end-to-end training across its components, illustrating progression and refinement within the RAG family.
```
