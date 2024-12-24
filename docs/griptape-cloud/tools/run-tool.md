# Running a Tool

Once your Tool is created and deployed, you can run your Tool one of three ways outlined below.

## From the Cloud Console

Go to the `Test` tab of your Tool to open the generated OpenAPI spec. From there, the Swagger UI can be used to create test requests.

## From the API

The API route for Tool activities is in the form of `https://cloud.griptape.ai/api/tools/{tool_id}/activities/{activity_name}`, where `tool_id` is the resource UUID of your created Tool, and `activity_name` is the name of the activity as defined in your `BaseTool` class. The activity routes will only accept an http POST method.

To fetch the OpenAPI schema, the route is `https://cloud.griptape.ai/api/tools/{tool_id}/openapi`.

```bash
export GT_CLOUD_API_KEY="<your API key here>"
export GT_CLOUD_TOOL_ID="<your tool ID here>"
export TOOL_ACTIVITY_URL="https://api.griptape.com/v1/tools/${GT_CLOUD_TOOL_ID}/activities/my_activity"

response=$(curl -X POST -H "Authorization: Bearer ${GT_CLOUD_API_KEY}" --json '{"my_key": "my_value"}' ${TOOL_ACTIVITY_URL})
echo "my_activity response: ${response}"
```

## Using the Griptape Framework

The Griptape framework provides a [`GriptapeCloudToolTool`](../../griptape-tools/official-tools/griptape-cloud-tool-tool.md) for interacting with your deployed Tools. Simply pass your Tool resource UUID as the `tool_id` kwarg, and the schema and activity methods will be dynamically set on the Tool.
