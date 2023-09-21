from typing import Optional
from attr import define, field
from griptape.drivers import BaseGraphDriver
import neo4j
#add neo4j to poetry.lock requirements? ^

@define
class CypherDriver(BaseGraphDriver):
    uri: str = field(kw_only=True)
    username: str = field(kw_only=True)
    password: str = field(kw_only=True)
    MAX_SCHEMA_SIZE: int = 6000
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

    def get_schema(self) -> str:
        schema_query = """
        CALL db.schema.visualization()
        """
        with self._driver.session() as session:
            results = session.run(schema_query)
            schema_str = "\n".join([str(record.data()) for record in results])
            self._driver.close()

            if len(schema_str) > self.MAX_SCHEMA_SIZE:
                raise ValueError("The retrieved schema is too large to handle.")

            return schema_str
