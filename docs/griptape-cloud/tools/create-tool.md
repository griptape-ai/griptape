# Tools

You can host your [Griptape framework Tools](../../griptape-framework/tools/index.md) on Griptape Cloud. This allows you to run your Tools without needing to manage infrastructure.

## Create a Tool from a GitHub Repo

1. [Connect Your GitHub Account in your Griptape Cloud account](https://cloud.griptape.ai/account)
1. Install the [Griptape Cloud GitHub app to your GitHub account or organization](https://github.com/apps/griptape-cloud/installations/new/)
    - Be sure to allow the app access to `All Repositories` or select the specific repositories you need
1. Ensure your repository has a Tool Config YAML file
    - To learn more see [Tool Config YAML](tool-config.md)

You can now [create a Tool in the Griptape Cloud console](https://cloud.griptape.ai/tools/create/github-creation) by providing your GitHub repository information.

## Create a Tool from a ZIP

1. Ensure your Tool folder has a Tool Config YAML file
    - To learn more see [Tool Config YAML](tool-config.md)
1. Compress the entire Tool folder into a ZIP file
    - On Mac and Linux systems, this can be done with the 'zip' CLI command
    - On Windows systems, this can be done with the 'tar.exe' PowerShell command
1. Upload the created ZIP to a [Data Lake Bucket](../data-lakes/data-lakes.md) and note the Asset Name

You can now [create a Tool in the Griptape Cloud console](https://cloud.griptape.ai/tools/create/data-lake-creation) by providing your Bucket and Asset Name from above.

### Quickstart With Samples and Templates

To get started with Tools in the Cloud, deploy one of the [griptape-sample-tools from GitHub](https://github.com/griptape-ai/griptape-sample-tools/tree/main).
