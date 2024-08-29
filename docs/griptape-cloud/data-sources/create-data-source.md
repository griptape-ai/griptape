# Data Sources

Data Sources are the first step to Griptape's RAG pipeline. They allow you to bring your own data to ingest and transform. You can then make one or more Data Source available to your AI applications via [Knowledge Bases](../knowledge-bases/create-knowledge-base.md)

## Create a Data Source

You can [create a Data Source in the Griptape Cloud console](https://cloud.griptape.ai/data-sources/create) by specifying the required configuration for your chosen Data Source in the cloud console.

### Web Page

You can scrape and ingest a single, public web page by providing a URL. If you wish to scrape multiple pages, you must create multiple Data Sources. However, you can then add all of the pages to the same Knowledge Base if you wish to access all the pages together.

### Google Drive

You can ingest documents and spreadsheets stored in a Google Drive account. We support all standard file formats such as text, markdown, spreadsheets, and presentations.

### Confluence

You can connect to your personal or company Confluence by providing a URL, [Atlassian API Token](https://id.atlassian.com/manage-profile/security/api-tokens), and the email address for the token holder's account. Each Confluence Data Source can be limited to a single Space in Confluence by specifying the [specific URL for that Space](https://support.atlassian.com/confluence-cloud/docs/use-spaces-to-organize-your-work/).

### Structure (Experimental)

You can specify a [Structure](../structures/create-structure.md) to run as a Data Source as long as your Structure returns a [`TextArtifact` or `ListArtifact` from the Griptape Framework](../../griptape-framework/data/artifacts.md). You can use this as a way to build custom Data Sources.

## Other Data Source Types

If you do not see a Data Source configuration you'd wish to use, you can submit a request via [Discord](https://discord.gg/gnWRz88eym) or `hello@griptape.ai`.
