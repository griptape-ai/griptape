from __future__ import annotations
from concurrent import futures
from typing import Optional, TYPE_CHECKING, Any
from attr import define, field, Factory
from griptape import utils
from griptape.artifacts import TextArtifact, ListArtifact
from griptape.drivers import BaseGraphDriver
from griptape.utils import import_optional_dependency

if TYPE_CHECKING:
    from neo4j import Driver, Auth, Session, ManagedTransaction, Record
    from neo4j.graph import Node, Relationship


@define
class Neo4jGraphDriver(BaseGraphDriver):
    NODE_PROPS_QUERY = """
    CALL apoc.meta.data()
    YIELD label, other, elementType, type, property
    WHERE NOT type = "RELATIONSHIP" AND elementType = "node"
    WITH label AS nodeLabels, collect({property:property, type:type}) AS properties
    RETURN {labels: nodeLabels, properties: properties} AS output

    """

    RELATIONSHIP_PROPS_QUERY = """
    CALL apoc.meta.data()
    YIELD label, other, elementType, type, property
    WHERE NOT type = "RELATIONSHIP" AND elementType = "relationship"
    WITH label AS nodeLabels, collect({property:property, type:type}) AS properties
    RETURN {type: nodeLabels, properties: properties} AS output
    """

    RELATIONSHIPS_QUERY = """
    CALL apoc.meta.data()
    YIELD label, other, elementType, type, property
    WHERE type = "RELATIONSHIP" AND elementType = "node"
    UNWIND other AS other_node
    RETURN "(:" + label + ")-[:" + property + "]->(:" + toString(other_node) + ")" AS output
    """

    uri: str = field(kw_only=True)
    auth: Auth = field(kw_only=True)
    graph_db_hint: str = field(default="Neo4j with Cypher support", kw_only=True)
    neo4j_import = field(default=Factory(lambda: import_optional_dependency("neo4j")), kw_only=True)
    neo4j_driver: Driver = field(
        default=Factory(
            lambda self: self.neo4j_import.GraphDatabase.driver(self.uri, auth=self.auth),
            takes_self=True
        ),
        kw_only=True
    )
    session: Session = field(
        default=Factory(lambda self: self.neo4j_driver.session(), takes_self=True)
    )
    futures_executor: futures.Executor = field(default=Factory(lambda: futures.ThreadPoolExecutor()), kw_only=True)

    def __del__(self):
        self.neo4j_driver.close()

    def _raw_query(
            self, query: str, namespace: Optional[str] = None, params: Optional[dict] = None
    ) -> list[dict[str, Any]]:
        with self.neo4j_driver.session(database=namespace) as session:
            try:
                data = session.run(query, params)
                return [r.data() for r in data]
            except self.neo4j_import.exceptions.CypherSyntaxError as e:
                raise ValueError(f"Invalid Cypher syntax: {e}")

    def load_metadata(self, namespace: Optional[str] = None) -> dict:
        node_props = self._raw_query(self.NODE_PROPS_QUERY, namespace=namespace)
        relationships_props = self._raw_query(self.RELATIONSHIP_PROPS_QUERY, namespace=namespace)
        relationships = self._raw_query(self.RELATIONSHIPS_QUERY, namespace=namespace)

        return {
            "node_properties": [el["output"] for el in node_props],
            "relationships_properties": [el["output"] for el in relationships_props],
            "relationships": [el["output"] for el in relationships]
        }

    def query(self, query: str, namespace: Optional[str] = None) -> TextArtifact:
        with self.neo4j_driver.session(database=namespace) as session:
            return TextArtifact(session.execute_read(lambda tx: tx.run(query).data()))

    def load_artifacts(self, namespace: Optional[str] = None) -> ListArtifact:
        query = "MATCH (n) RETURN n"

        with self.neo4j_driver.session(database=namespace) as session:
            return session.execute_read(lambda tx: tx.run(query).data())

    def upsert_text_artifact(self, artifact: TextArtifact, namespace: Optional[str] = None) -> str:
        return self.create_node(artifact.name, artifact.to_dict(), namespace).element_id

    def upsert_text_artifacts(self, artifacts: list[TextArtifact], namespace: Optional[str] = None) -> list[str]:
        return utils.execute_futures_list(
            [
                self.futures_executor.submit(self.upsert_text_artifact, a, namespace)
                for a in artifacts
            ]
        )

    def create_node(self, label: str, properties: dict, namespace: Optional[str] = None) -> Node | None:
        def _create_node(tx: ManagedTransaction, l: str, ps: dict) -> Record:
            # We have to escape the label with backticks since some of the automatically-generated TextArtifact names
            # can start with a number. More info: https://neo4j.com/docs/cypher-manual/current/syntax/naming/
            query = f"CREATE (n:`{l}`) SET n = $properties RETURN n"
            result = tx.run(query, properties=ps)

            return result.single()

        with self.neo4j_driver.session(database=namespace) as session:
            node = session.write_transaction(_create_node, label, properties)

            return node[0] if node else None

    def create_relationship(
            self, node_id_1: str, node_id_2: str, relationship_type: str, namespace: Optional[str] = None
    ) -> Relationship | None:
        def _create_relationship(tx: ManagedTransaction, n_1: str, n_2: str, t: str) -> Record:
            query = "MATCH (node1), (node2) " \
                    f"WHERE ID(node1) = $n_1 AND ID(node2) = $n_2 " \
                    f"CREATE (node1)-[r:{t}]->(node2) " \
                    "RETURN r"

            result = tx.run(query, n_1=n_1, n_2=n_2)

            return result.single()

        with self.neo4j_driver.session(database=namespace) as session:
            relationship = session.write_transaction(_create_relationship, node_id_1, node_id_2, relationship_type)

            return relationship[0] if relationship else None
