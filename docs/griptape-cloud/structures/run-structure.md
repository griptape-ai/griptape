# Running a Structure

Once your Structure is created and deployed, you can run your Structure one of three ways outlined below. You view the output of any of your runs, no matter how you created them, in the `Runs` tab of your Structure.

## From the Cloud Console

In the cloud console, click on the name of the Structure you wish to run and then go to the `Test` tab. Here you can specify arguments to pass to your Structure run and any run-specific environment variables you need.

When passing arguments through the cloud console, pass each new argument on a new line. For example if your local code is ran with the inputs `-i input_file.txt` then the arguments you would pass in the cloud would be:

```
-i
input_file.txt
```

## From the API

You can run your Structure via the API using CURL or any other code that can make HTTP requests. You will need a [Griptape Cloud API Key](https://cloud.griptape.ai/configuration/api-keys) and the `Structure Invocation URL` which is located on the `Config` tab of your Structure. 

The example below will kick off a run with the args you pass as a json object.

```shell
export GT_CLOUD_API_KEY=<your API key here>
export INVOCATION_URL=<your structure invocation URL>
curl -H "Authorization: Bearer ${GT_CLOUD_API_KEY}" --json '{"args": ["arg1"], ""env_vars"": [{"name":"var1", "value": "value"}]}' ${INVOCATION_URL}
```

For more information on other Structure run APIs, check out the [StructureRuns API docs](../api/api-reference.md/#/StructureRuns).

## Using the Griptape Framework

You can use [StructureRunDrivers](../../griptape-framework/drivers/structure-run-drivers.md/#griptape-cloud) to run your Structure with Griptape.
