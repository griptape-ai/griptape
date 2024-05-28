# Qdrant Vector Store Driver

The implementation of a custom `QdrantVectorStoreDriver` for use with the Griptape framework. The driver allows you to interact with a Qdrant vector store for managing vector data.

## Usage

### QdrantVectorStoreDriver Class

The `QdrantVectorStoreDriver` class provides methods for interacting with a Qdrant vector store. Below is a description of its main methods:

#### `__attrs_post_init__(self)`

Initializes the Qdrant client and ensures the collection exists with the correct configuration.

#### `delete_vector(self, ids: Optional[List[str]] = None, **kwargs: Any) -> Any`

Deletes vectors by their IDs from the specified collection.

#### `query(self, query: str, count: Optional[int] = None, include_vectors: bool = False, **kwargs: Any) -> List[BaseVectorStoreDriver.QueryResult]`

Queries the vector store using a text query and returns the results. It converts the query text to a vector and searches the collection.

#### `upsert_vector(self, texts: Iterable[TextArtifact], ids: Optional[Sequence[str]] = None, metadata: Optional[Sequence[Dict[str, Any]]] = None, batch_size: int = BATCH_SIZE, **kwargs: Any) -> None`

Inserts or updates vectors in the collection. It splits the texts into batches and upserts them into the Qdrant collection.

#### `_create_collection(self, model: str) -> None`

Creates a new collection in the Qdrant vector store with the specified configuration. If `force_recreate` is set to `True`, it will recreate the collection.

#### `_create_batches(self, texts: Iterable[TextArtifact], ids: Optional[Sequence[str]] = None, metadata: Optional[Sequence[Dict[str, Any]]] = None, batch_size: int = BATCH_SIZE) -> Generator[Tuple[List[str], List[rest.PointStruct]], None, None]`

Splits the texts into batches and creates point structures for insertion into the Qdrant collection.


## Acknowledgements

 - [HuggingFace](https://huggingface.co/) For out of the world LLMs and `transformer` package
 - [Qdrant](https://qdrant.tech/) for high-performant vector similarity search technology.
 - [Superteams](https://www.superteams.ai/) for providing GPUs with GCP
