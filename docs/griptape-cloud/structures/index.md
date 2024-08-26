# Structures

Use [Structures](https://cloud.griptape.ai/structures) to host any python code in the cloud in seconds.

## Create a Structure

1. First [Connect Your GitHub Account](https://cloud.griptape.ai/account)
1. Install the [Griptape Cloud GitHub app](https://github.com/apps/griptape-cloud/installations/new/) to any account or organization you'd like to pull code in from
    1. Be sure to allow the app access to `All Repositories` or select the specific repositories you need

You can then [create a Structure](https://cloud.griptape.ai/structures/create) by providing your GitHub repository information. Make sure that your repository has a [Structure Config YAML](structure-config.md).

### Quickstart With Samples and Templates

To get started with Structures in the Cloud, check out the [managed-structure-template](https://github.com/griptape-ai/managed-structure-template) or deploy one of the [griptape-sample-structures](https://github.com/griptape-ai/griptape-sample-structures/tree/main).

## Run a Structure

Once your Structure is created and deployed, you can run your Structure one of three ways outlined below. In order to view the output of any of your runs, no matter how you created them, you can view them in the `Runs` tab of your Structure.

### From the UI

In the UI, click on the name of the Structure you wish to run and then go to the `Test` tab. Here you can specify arguments to pass to your Structure run and any run-specific environment variables you need.

When passing arguments through the UI, pass each new argument on a new line. For example if your local code could be ran with the inputs `-i input_file.txt` then the arguments you would pass in the cloud would be:

```
-i
input_file.txt
```

### From the API

You can run your Structure via the API using CURL or any other code that can make HTTP requests. You will need a [Griptape Cloud API Key](https://cloud.griptape.ai/configuration/api-keys) and the `Structure Invocation URL` which is located on the `Config` tab of your Structure.

```shell
curl -H "Authorization: Bearer ${GT_CLOUD_API_KEY}" --json '{"args": ["arg1"], "env": {"var1":"value1"}}' ${INVOCATION_URL}
```

For more information on other Structure run APIs, check out the [StructureRuns API docs](api/api-reference/#/StructureRuns).

### Using the Griptape Framework

You can use [StructureRunDrivers](../../griptape-framework/drivers/structure-run-drivers/#griptape-cloud) in the Griptape Framework to run your code.