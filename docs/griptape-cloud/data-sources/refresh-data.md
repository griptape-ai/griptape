# Refresh a Data Source

## Scheduled Refresh

By default your Data Source will not refresh automatically. When creating a Data Source, you can enable scheduled refresh and specify a [CRON expression](https://crontab.guru/). For example, if you wish your Data Source to refresh every day at midnight PDT you can use the following expression: `0 7 * * *`.

## Manual Refresh

If you wish to manually refresh a Data Source you can do so either via the `Refresh` button in the cloud console or by API using the `Data Source ID` on the `Config` tab and a [Griptape Cloud API Key](https://cloud.griptape.ai/configuration/api-keys).

The following shell commands will create a new data refresh job. You will need to specify your API key and data source id.

```shell
export GT_CLOUD_API_KEY=<your API key here>
export DATA_SOURCE_ID=<your data source id here>
curl -H "Authorization: Bearer ${GT_CLOUD_API_KEY}" --json '{}' https://cloud.griptape.ai/api/data-connectors/${DATA_SOURCE_ID}/data-jobs
```
