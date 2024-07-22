## Overview

Griptape provides a way to build drivers for graph databases where graph data can be stored and queried. Every graph store driver implements the following methods:

- `upsert_node()` for updating or inserting a new node into graph databases.
- `upsert_node_artifacts()` for updating or inserting multiple nodes into graph databases.
- `upsert_edge()` for updating and inserting new edges between nodes in graph databases.
- `query_nodes()` for querying nodes in graph databases.
- `query_edges()` for querying edges in graph databases.

Each graph driver extends the `BaseGraphStoreDriver`, which provides additional utility methods to manage graph structures.

!!! info
    When working with graph database indexes with Griptape drivers, ensure that your schema supports the required node and edge properties. Check the documentation for your graph database on how to create and manage graph schemas.

## FalkorDB

!!! info
    This driver requires the `drivers-graph-falkordb` [extra](../index.md#extras).

The [FalkorDBGraphStoreDriver](../../reference/griptape/drivers/graph/falkordb_graph_store_driver.md) supports the [FalkorDB graph database](https://www.falkordb.com/).

Here is an example of how the driver can be used to load and query information in a FalkorDB cluster:

```python
import os
from griptape.drivers.graph import FalkorDBGraphStoreDriver

# Initialize the FalkorDB driver
falkordb_driver = FalkorDBGraphStoreDriver(
    url=os.environ["FALKORDB_URL"],
    api_key=os.environ["FALKORDB_API_KEY"]
)

# Example node data
node_data = {
    "id": "1",
    "label": "Person",
    "properties": {
        "name": "Alice",
        "age": 30
    }
}

# Upsert a node
falkordb_driver.upsert_node(node_data)

# Query nodes
results = falkordb_driver.query_nodes("MATCH (n:Person) RETURN n")

for result in results:
    print(result)
```