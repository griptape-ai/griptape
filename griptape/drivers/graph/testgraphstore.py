import unittest
from falkordb_graph_store_driver import FalkorDBGraphStoreDriver

class TestFalkorDBGraphStoreDriver(unittest.TestCase):
    def setUp(self):
        self.url = "redis://localhost:6379"
        self.database = "falkor"
        self.node_label = "Entity"
        self.driver = FalkorDBGraphStoreDriver(url=self.url, database=self.database, node_label=self.node_label)

    def test_connect(self):
        self.assertIsNotNone(self.driver.client)
        print("test_connect passed")

    def test_upsert_triplet(self):
        subj = "test_subject"
        rel = "test_relation"
        obj = "test_object"
        self.driver.upsert_triplet(subj, rel, obj)
        # Verify triplet is upserted
        triplets = self.driver.get(subj)
        self.assertTrue(any(obj in triplet for triplet in triplets))
        print("test_upsert_triplet passed")

    def test_get_triplets(self):
        subj = "test_subject"
        rel = "test_relation"
        obj = "test_object"
        self.driver.upsert_triplet(subj, rel, obj)
        triplets = self.driver.get(subj)
        self.assertEqual(len(triplets), 1)
        self.assertEqual(triplets[0][1], obj)
        print("test_get_triplets passed")

    def test_get_rel_map(self):
        subj = "test_subject"
        rel = "test_relation"
        obj = "test_object"
        self.driver.upsert_triplet(subj, rel, obj)
        subjs = [subj]
        rel_map = self.driver.get_rel_map(subjs=subjs)
        self.assertIn(subj, rel_map)
        print("test_get_rel_map passed")

    def test_delete_triplet(self):
        subj = "test_subject"
        rel = "test_relation"
        obj = "test_object"
        self.driver.upsert_triplet(subj, rel, obj)
        self.driver.delete(subj, rel, obj)
        # Verify triplet is deleted
        triplets = self.driver.get(subj)
        self.assertFalse(any(obj in triplet for triplet in triplets))
        print("test_delete_triplet passed")

    def test_refresh_schema(self):
        self.driver.refresh_schema()
        self.assertIn("Properties", self.driver.schema)
        self.assertIn("Relationships", self.driver.schema)
        print("test_refresh_schema passed")

    def test_get_schema(self):
        schema = self.driver.get_schema(refresh=True)
        self.assertIn("Properties", schema)
        self.assertIn("Relationships", schema)
        print("test_get_schema passed")

    def test_query(self):
        query = "MATCH (n) RETURN n LIMIT 1"
        result = self.driver.query(query)
        self.assertIsNotNone(result)
        print("test_query passed")

if __name__ == '__main__':
    unittest.main()
