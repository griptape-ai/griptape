import logging

from griptape.artifacts import TextArtifact
from griptape.structures import Pipeline
from griptape.tasks.falkordb_task import FalkorDBTask
from griptape.tasks.process_result_task import ProcessResultTask

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(message)s")

host = "localhost"  # Replace with actual value
port = 6379  # Replace with actual value

# Initialize Tasks
falkordb_task = FalkorDBTask(graph_name="falkordb")
falkordb_task.connect(host=host, port=port)
process_result_task = ProcessResultTask()

# Chain Tasks
falkordb_task >> process_result_task

# Create a Pipeline
pipeline = Pipeline(tasks=[falkordb_task, process_result_task])

# Run Task 1: Create a node
falkordb_task.context["input"] = TextArtifact(
    "CREATE (:Person {name: 'Alice', age: 30})"
)
pipeline.run()

# Run Task 2: Query the created node and process the result
falkordb_task.context["input"] = TextArtifact("MATCH (p:Person) RETURN p")
pipeline.run()

# Get the final result from the second task
result = process_result_task.output

if result:
    logging.info("Final Processed Result: %s", result.to_text())
else:
    logging.error("No output was produced by the task.")
