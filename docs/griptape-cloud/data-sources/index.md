# Data Sources

Use [Data Sources](https://cloud.griptape.ai/data-sources) to connect and ingest your own data for use with your AI code.

## Create a Data Source

You can [Create a Data Source](https://cloud.griptape.ai/data-sources/create) by specifying the required configuration for your chosen data source.

If you do not see a data source coniguration you'd wish to use, you can submit a request via Discord or `hello@griptape.ai`.

## Refresh a Data Source

By default your Data Source will not refresh automatically. You can enable automatic refresh and specify a CRON expression when creating a Data Source.

For example, if you wish your Data Source to refresh every day at midnight you can use the following expression: `0 0 * * *`.

If you wish to manually refresh a data source you can do so either via the `Refresh` button on the UI or by API using the `Data Source ID` on the `Config` tab. You will need a [Griptape Cloud API Key](https://cloud.griptape.ai/configuration/api-keys) to make API calls.

```shell
curl -H "Authorization: Bearer ${GT_CLOUD_API_KEY}" --json '{}' https://cloud.griptape.ai/api/data-connectors/${data_source_id}/data-jobs
```
