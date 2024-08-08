In this example we implement a multi-agent Workflow. We have a single "Researcher" Agent that conducts research on a topic, and then fans out to multiple "Writer" Agents to write blog posts based on the research.

By splitting up our workloads across multiple Structures, we can parallelize the work and leverage the strengths of each Agent. The Researcher can focus on gathering data and insights, while the Writers can focus on crafting engaging narratives.
Additionally, this architecture opens us up to using services such as [Griptape Cloud](https://www.griptape.ai/cloud) to have each Agent run completely independently, allowing us to scale our Workflow as needed 🤯. To try out how this would work, you can deploy this example as multiple structures from our [Sample Structures](https://github.com/griptape-ai/griptape-sample-structures/tree/main/griptape-multi-agent-workflows) repo.


```python
--8<-- "docs/examples/src/multi_agent_workflow_1.py"
```
