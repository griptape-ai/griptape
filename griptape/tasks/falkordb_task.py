import redis
from griptape.artifacts import BaseArtifact, TextArtifact
from griptape.tasks import BaseTask
from redis.commands.graph import Graph


class FalkorDBTask(BaseTask):
    def __init__(self, graph_name: str = "falkordb") -> None:
        """
        Initialize FalkorDBTask with a default graph_name.
        """
        super().__init__()
        self.graph_name = graph_name
        self.client = None
        self.graph = None

    def connect(self, host: str, port: int) -> None:
        """
        Connect to Redis with the provided host and port.
        """
        self.client = redis.Redis(host=host, port=port, decode_responses=True)
        self.graph = Graph(self.client, self.graph_name)

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
        Executes the Cypher query from the input.
        """
        query = self.input.value
        if not self.graph:
            raise RuntimeError("Graph client is not connected.")
        try:
            result = self.graph.query(query)

            data = []
            for row in result.result_set:
                data.append([str(item) for item in row])

            formatted_result = f"Data: {data}\nStatistics: {result.statistics}"
            return TextArtifact(formatted_result)
        except Exception as e:
            return TextArtifact(f"Error executing query: {str(e)}")
