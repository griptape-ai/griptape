# Getting Started with Vector Knowledge Bases

## How to create a Vector Knowledge Base

Follow these steps to create a Vector Knowledge Base. For this example, we will use the fully-managed Griptape Cloud vector store. If you are using EDB Postgres or another type of Postgres instance as your vector store, select the pgvector option.

1. Navigate to the [Knowledge Bases](https://cloud.griptape.ai/knowledge-bases) page in the Griptape Cloud Console.
1. Click *Create Knowledge Base*.
1. Select the Griptape Cloud Vector Knowledge Base type.
1. Give your Knowledge Base a name and a description (optional).
1. Select the Data Source(s) you want to include in the Knowledge Base.
1. Click *Create* to submit the form.

> ### Pro Tip:
>
> You can add a Data Source to as many Vector Knowledge Bases (KBs) as you want. For example, you can include a Frequently Asked Questions Data Source in both a New Employee Onboarding KB and a Customer Support Playbook KB.

## What's happening?

Once you have created the Vector Knowledge Base, we will automatically begin the process of upserting your data to a database. This process is known as a Knowledge Base job. It typically takes just a few moments.

While the job is in progress, you will be directed to the Knowledge Base detail page where you can observe the job status as well as view and edit Knowledge Base details such as the name, description, and Data Sources to be included.

## How to use a Vector Knowledge Base

When your Vector Knowledge Base is ready, the data it contains becomes available for applications to retrieve via Griptape Assistants, or Structures such as Agents.

> ### Pro Tip:
>
> You can perform a test query by selecting the Query tab and entering some information that you know is in your data. The result will be a 'raw' response that contains the embedded text and other query parameters. This feature is useful for testing and debugging.

The next step of using your Vector Knowledge Base is connecting it to an application, such as a chat Assistant, that can retrieve your data and use it to generate useful responses.

Follow these steps to create and use a simple chat Assistant.

1. Navigate to the [Assistants](https://cloud.griptape.ai/assistants) page in the Griptape Cloud Console.
1. Click *Create Assistant*.
1. Give your Assistant a name and description (optional).
1. Select your Vector Knowledge Base from the *Knowledge Bases* dropdown menu.
1. Click *Create* to submit the form.

You will be directed to the Assistant chat screen. Type a message to start a conversation thread with your new Assistant. Try asking it something about your data!

> ### Pro Tip:
>
> Add a Ruleset to provide your Assistant with instructions and guidance for how it should behave.

For more information about different Knowledge Base types, see [Knowledge Base Types](./knowledge-base-types.md)
