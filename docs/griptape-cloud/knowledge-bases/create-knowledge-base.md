# Knowledge Bases

Knowledge Bases are way to organize and access your data ingested from [Data Sources](../data-sources/create-data-source.md). You can specify multiple Data Sources per Knowledge Base in order to access data ingested from different sources all in one place.

## Creating a Vector Knowledge Base

You can create a Griptape Cloud Vector Knowledge Base on the [Create Knowledge Base](https://cloud.griptape.ai/knowledge-bases/create) page in Griptape Cloud console. When doing so, you will asked provide a name and to select the Data Sources that you wish to include in your new Knowledge Base. Once created, you can [access your data](accessing-data.md).

If you wish to provide your own Postgres & pgvector endpoint, you will be prompted to provide your database Connection String and Password, as well as to select the Data Sources that you wish to use to populate this Knowledge Base.

## Creating a Hybrid Knowledge Base

To create a Griptape Cloud Hybrid Knowledge Base, select the Griptape Cloud card in the Hybrid Knowledge Base section on the [Create Knowledge Base](https://cloud.griptape.ai/knowledge-bases/create) page in Griptape Cloud console. You will be prompted to provide a name and to select the Data Sources that you wish to include in your Knowledge Base. The final step is the verify the field mappings and confirm which columns are structured columns and which columns contain unstructued data. We attempt to determine which columns are of which type, but you can modify the mappings if you see any columns that have been incorrectly mapped.
