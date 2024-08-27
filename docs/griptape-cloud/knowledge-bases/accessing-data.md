# Accessing Data in a Knowledge Base

You can `Search` or `Query` the Knowledge Base for information contained in your Data Sources. `Search` will return a natural language response while `Query` will return the individual entries. Use whichever one best fits your use case.

## From the UI

You can try out both actions from the UI on the `Test` tab of your Knowledge Base.

## From the API

You can enact both `Query` and `Search` via the API by hitting their respective endpoints using a [Griptape Cloud API Key](https://cloud.griptape.ai/configuration/api-keys) and the Knowledge Base ID found on the `Config` tab of your Knowledge Base. 

The following example commands will send the query string "test query string" and return the results from the Knowledge Base.

### Query

```shell
export GT_CLOUD_API_KEY=<your API key here>
export KNOWLEDGE_BASE_ID=<your knowledge base id here>
curl -H "Authorization: Bearer ${GT_CLOUD_API_KEY}" --json '{"query": "test query string"}' https://cloud.griptape.ai/api/knowledge-bases/${KNOWLEDGE_BASE_ID}/query
```

### Search

```shell
export GT_CLOUD_API_KEY=<your API key here>
export KNOWLEDGE_BASE_ID=<your knowledge base id here>
curl -H "Authorization: Bearer ${GT_CLOUD_API_KEY}" --json '{"query": "test query string"}' https://cloud.griptape.ai/api/knowledge-bases/${KNOWLEDGE_BASE_ID}/search
```

## Using the Griptape Framework

You can use [VectorStoreDrivers](../../griptape-framework/drivers/vector-store-drivers.md/#griptape-cloud-knowledge-base) to query your Knowledge Base with Griptape.
