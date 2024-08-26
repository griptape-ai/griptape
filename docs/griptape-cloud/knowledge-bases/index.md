# Knowledge Bases

Use [Knowledge Bases](https://cloud.griptape.ai/knowledge-bases) to prep your data ingested from [Data Sources](../data-sources/index.md) for retrieval.

## Create a Knowledge Base

You can [create a Knowledge Base](https://cloud.griptape.ai/knowledge-bases/create) by specifying which Data Sources you wish to include.

## Search or Query a Knowledge Base

Once created you can `Search` or `Query` the Knowledge Base for information contained in your Data Sources. `Search` will return a natural language response while `Query` will return the individual entries. Use whichever one best fits your use case.

### From the UI

You can try out both actions from the UI on the `Test` tab of your Knowledge Base.

### From the API

You can enact both `Query` and `Search` via the API by hitting their respective endpoints using a [Griptape Cloud API Key](https://cloud.griptape.ai/configuration/api-keys) and the Knowledge Base ID found on the `Config` tab of your Knowledge Base.

#### Query

```shell
curl -H "Authorization: Bearer ${GT_CLOUD_API_KEY}" --json '{"query": "test query string"}' https://cloud.griptape.ai/api/knowledge-bases/${knowledge-base-id}/query
```

#### Search

```shell
curl -H "Authorization: Bearer ${GT_CLOUD_API_KEY}" --json '{"query": "test query string"}' https://cloud.griptape.ai/api/knowledge-bases/${knowledge-base-id}/search
```

### Using the Griptape Framework

You can use [VectorStoreDrivers](../../griptape-framework/drivers/vector-store-drivers/#griptape-cloud-knowledge-base) in the Griptape Framework to run your code.
