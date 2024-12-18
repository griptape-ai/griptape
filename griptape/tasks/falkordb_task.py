from griptape.tasks import BaseTask
from griptape.artifacts import TextArtifact, BaseArtifact
import redis
from redis.commands.graph import Graph


class FalkorDBTask(BaseTask):
    def __init__(self, graph_name="falkordb", host="localhost", port=6379, password=None):
        super().__init__()
        self.client = redis.Redis(
            host=host,
            port=port,
            password=password,
            decode_responses=True
        )
        self.graph = Graph(self.client, graph_name)

    @property
    def input(self) -> BaseArtifact:
        """
        Returns the input artifact, ensuring it's a valid TextArtifact.
        """
        artifact = self.context.get("input")
        if artifact and isinstance(artifact, TextArtifact):
            return artifact
        raise ValueError("Input must be a TextArtifact")

    def try_run(self) -> BaseArtifact:
        """
        Executes the Cypher query from the input and returns the result as a TextArtifact.
        """
        query = self.input.value  # Extract the query string from the input artifact
        try:
            result = self.graph.query(query)

            data = []
            for row in result.result_set:
                data.append([str(item) for item in row])

            formatted_result = f"Data: {data}\nStatistics: {result.statistics}"
            return TextArtifact(formatted_result)
        except Exception as e:
            return TextArtifact(f"Error executing query: {str(e)}")
