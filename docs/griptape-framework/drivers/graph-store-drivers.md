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

The easiest way to start FalkorDB as a graph database is using the FalkorDB Docker image. To follow every step of this tutorial, launch the image as follows:

bash
docker run -p 6379:6379 -it --rm falkordb/falkordb:edge

```python
import os
from griptape.drivers.graph.falkordb_graph_store_driver import FalkorDBGraphStoreDriver

# Initialize the FalkorDB driver
falkordb_driver = FalkorDBGraphStoreDriver(
    url="redis://localhost:6379"
)

# Example node data for the first node
node_data_1 = {
    "id": "1",
    "label": "Person",
    "properties": {
        "name": "Alice",
        "age": 30  # Ensure all properties are of primitive types
    }
}

# Example node data for the second node
node_data_2 = {
    "id": "2",
    "label": "Person",
    "properties": {
        "name": "Bob",
        "age": 25  # Ensure all properties are of primitive types
    }
}

# Upsert nodes
falkordb_driver.upsert_node(node_data_1)
falkordb_driver.upsert_node(node_data_2)

# Upsert a triplet to represent a relationship
falkordb_driver.upsert_triplet("1", "FRIEND", "2")

# Query nodes
results = falkordb_driver.query("MATCH (n:Person) RETURN n")

# Print node properties
for result in results:
    node = result[0]
    print(f"Node ID: {node.id}")
    for key, value in node.properties.items():
        print(f"{key}: {value}")

# Directly query edges
edge_query = """
MATCH (n1:Entity {id: $subj})-[r:FRIEND]->(n2:Entity)
RETURN n1.id, type(r), n2.id
"""
edge_results = falkordb_driver.query(edge_query, params={"subj": "1"})
print("Edge Results:", edge_results)

# Query edges
edge_results = falkordb_driver.query("MATCH (a:Person)-[r:FRIEND]->(b:Person) RETURN a, r, b")

# Print edge properties
for edge_result in edge_results:
    start_node = edge_result[0]
    relationship = edge_result[1]
    end_node = edge_result[2]
    print(f"Start Node ID: {start_node.id}, Relationship: {relationship}, End Node ID: {end_node.id}")
```