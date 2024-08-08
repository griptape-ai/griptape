This example shows how to use one `Agent` to load content into `TaskMemory` and get that content from another `Agent` using `TaskMemoryClient`.

The first `Agent` uses a remote vector store (`MongoDbAtlasVectorStoreDriver` in this example) to handle memory operations. The second `Agent` uses the same instance of `TaskMemory` and the `TaskMemoryClient` with the same `MongoDbAtlasVectorStoreDriver` to get the data.

The `MongoDbAtlasVectorStoreDriver` assumes that you have a vector index configured where the path to the content is called `vector`, and the number of dimensions set on the index is `1536` (this is a commonly used number of dimensions for embedding models).

`asker` uses the same instance of `TaskMemory` as `loader` so that `asker` has access to the `namespace_storages` that `loader` has set.

```python
--8<-- "docs/examples/src/multiple_agent_shared_memory_1.py"
```
