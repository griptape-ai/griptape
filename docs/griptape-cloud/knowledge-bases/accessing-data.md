# Accessing Data in a Knowledge Base

You can `Search` or `Query` the Knowledge Base for information contained in your Data Sources. `Search` will return a natural language response while `Query` will return the individual entries. Use whichever one best fits your use case.

## From the Cloud Console

You can explore your data with a natural language question on the `Query` tab of your Knowledge Base. You can use *+ Add Schema Argument* to add schema arguments to query structured data in a Hybrid Knowledge Base. Selecting a *count* schema argument allows you to specify the number of results that you wish to return in the response to your query.

## From the API

You can enact both `Search` and `Query` via the API by hitting their respective endpoints using a [Griptape Cloud API Key](https://cloud.griptape.ai/configuration/api-keys) and the Knowledge Base ID found on the `Config` tab of your Knowledge Base.

The following example commands will send the string `"test question"` and return the results from the Knowledge Base.

### Search

```shell
export GT_CLOUD_API_KEY=<your API key here>
export KNOWLEDGE_BASE_ID=<your knowledge base id here>
curl -H "Authorization: Bearer ${GT_CLOUD_API_KEY}" --json '{"query": "test question"}' "https://cloud.griptape.ai/api/knowledge-bases/${KNOWLEDGE_BASE_ID}/search"
```

### Query

```shell
export GT_CLOUD_API_KEY=<your API key here>
export KNOWLEDGE_BASE_ID=<your knowledge base id here>
curl -H "Authorization: Bearer ${GT_CLOUD_API_KEY}" --json '{"query": "test question"}' "https://cloud.griptape.ai/api/knowledge-bases/${KNOWLEDGE_BASE_ID}/query"
```

## Using the Griptape Framework

You can use the [GriptapeCloudVectorStoreDriver](../../griptape-framework/drivers/vector-store-drivers.md/#griptape-cloud-knowledge-base) to query your Knowledge Base with Griptape.
