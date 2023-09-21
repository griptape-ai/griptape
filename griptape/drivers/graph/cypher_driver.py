from typing import Optional
from attr import define, field
from griptape.drivers import BaseGraphDriver
import neo4j
#add to requirements ^

@define
class CypherDriver(BaseGraphDriver):
    uri: str = field(kw_only=True)
    username: str = field(kw_only=True)
    password: str = field(kw_only=True)
    _driver: Optional[neo4j.Driver] = field(init=False, default=None)

    def __attrs_post_init__(self):
        try:
            self._driver = neo4j.GraphDatabase.driver(self.uri, auth=(self.username, self.password))
            self._driver.verify_connectivity()
        except neo4j.exceptions.ServiceUnavailable:
            raise ValueError("Could not connect to Neo4j database. Please ensure that the URL is correct.")
        except neo4j.exceptions.AuthError:
            raise ValueError("Authentication error. Please ensure that the username and password are correct.")

    def execute_query(self, query: str) -> Optional[list[BaseGraphDriver.NodeResult]]:
        try:
            with self._driver.session() as session:
                results = session.run(query)
                return [BaseGraphDriver.NodeResult(properties=record.data()) for record in results]
        except neo4j.exceptions.CypherSyntaxError as e:
            raise ValueError(f"Generated Cypher Statement is not valid\n{e}")
        finally:
            self._driver.close()

    # def execute_query_raw(self, query: str) -> Optional[list[dict[str, any]]]:
    #     try:
    #         with self._driver.session() as session:
    #             results = session.run(query)
    #             return [record.data() for record in results]
    #     except neo4j.exceptions.CypherSyntaxError as e:
    #         raise ValueError(f"Generated Cypher Statement is not valid\n{e}")
    #     finally:
    #         self._driver.close()
    #
    # def get_schema(self) -> str:
    #     node_properties_query = """
    #     CALL apoc.meta.data()
    #     YIELD label, other, elementType, type, property
    #     WHERE NOT type = "RELATIONSHIP" AND elementType = "node"
    #     WITH label AS nodeLabels, collect({property:property, type:type}) AS properties
    #     RETURN {labels: nodeLabels, properties: properties} AS output
    #     """
    #
    #     results = self.execute_query_raw(node_properties_query)
    #     schema = "\n".join([str(result["output"]) for result in results])
    #     return schema