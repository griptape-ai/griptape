The following example script ingests a Web page (a blog post),
stores its chunked contents on Astra DB through the Astra DB vector store driver,
and finally runs a RAG process to answer a question specific to the topic of the
Web page.

This script requires that a vector collection has been created in the Astra database
(with name `"griptape_test_collection"` and vector dimension matching the embedding being used, i.e. 1536 in this case).

_Note:_ Besides the [Astra DB](../griptape-framework/drivers/vector-store-drivers.md#astra-db) extra,
this example requires the `drivers-web-scraper-trafilatura`
Griptape extra to be installed as well.


```python
--8<-- "docs/examples/src/query_webpage_astra_db_1.py"
```
