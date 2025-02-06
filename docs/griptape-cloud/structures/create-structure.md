# Creating a Structure from a GitHub Repo

For production use-cases, we recommend connecting Griptape Cloud to GitHub and storing the code for your Structures in one or more a GitHub repos.

1. [Connect Your GitHub Account in your Griptape Cloud account](https://cloud.griptape.ai/account)
1. Install the [Griptape Cloud GitHub app to your GitHub account or organization](https://github.com/apps/griptape-cloud/installations/new/)
    - Be sure to allow the app access to `All Repositories` or select the specific repositories you need
1. Ensure your repository has a Structure Config YAML file. If your repository contains multiple Structures, each Structure must have a separate Structure Config YAML file.
    - To learn more see [Structure Config YAML](structure-config.md)
1. Navigate to the [Create Stucture](https://cloud.griptape.ai/structures/create) page in the Griptape Console
1. Select *Griptape Structure from GitHub Repo*
1. Select the GitHub Organization, Repository and Branch that you wish to deploy from.
1. Specify the `structure_config.yaml` for this deployment
1. Optionally, Enable Webhook and/or add Environment Variables
1. Click *Create* to create your Structure using the configuration details that you have entered

You can now [create a Structure in the Griptape Cloud console](https://cloud.griptape.ai/structures/create) by providing your GitHub repository information.

### Quickstart With Samples and Templates

To get started with Structures in the Cloud, check out the [managed-structure-template on GitHub](https://github.com/griptape-ai/managed-structure-template) or deploy one of the [griptape-sample-structures from GitHub](https://github.com/griptape-ai/griptape-sample-structures/tree/main).
