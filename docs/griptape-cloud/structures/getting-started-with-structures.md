# Getting Started with Structures

When building AI-powered software, prompting or chatting with an LLM directly will only take you so far. You'll want programmatic control over application logic and the flow of data. In other words, you'll want to run code.

Here are some examples:

- Ensuring agents perform specific tasks consistently.
- Providing access to a specific set of data to query.
- Accessing other APIs, services, and tools.
- Processing user inputs and query responses before passing to an LLM.
- Defining how an LLM's outputs should be formatted and delivered.
- Prescribing a series of tasks in a deterministic order.
- Connecting multiple application components together.

## How to create a Structure

Griptape Samples are a quick and easy way to get started with Structures. Several samples are available in the [Griptape Samples on GitHub](https://github.com/griptape-ai/griptape-sample-structures) for you to try. Of course, you can also [write your own custom structure and deploy this from GitHub](./create-structure.md) or follow a [Griptape Trade School](https://learn.griptape.ai/latest/courses/chatbot-rulesets/) course to build a simple rules-driven chatbot.

### Prerequisites:

For this example, you'll be able to compare outputs from OpenAI (GPT), Google (Gemini), or Anthropic (Claude) given the same input. You'll need API keys from at least one of those services to proceed.

You will also need a Griptape Cloud API key. Follow these steps to create one.

1. Navigate to the [API Keys](https://cloud.griptape.ai/configuration/api-keys) page in the Griptape Console.
1. Click *Create API key*.
1. Enter the name `GT_CLOUD_API_KEY`.
1. Click *Create* to submit the form.
1. Copy the key value. Save it somewhere so that you can paste it later.
1. Click *I have saved the key*.

### Creating, deploying and running a Structure

Follow these steps to create, deploy, and run a Structure. You can follow similar steps to deploy another sample or your own custom structure.

1. Navigate to the [Structures](https://cloud.griptape.ai/structures/) page in the Griptape Console.
1. Click *Create Structure*.
1. Select a Structure. For this example, choose *OpenAI vs. Google vs. Anthropic Model Comparison*.
1. (Optional) Give the Structure a name and description.
1. In the row labeled Key: `GT_CLOUD_API_KEY`, click the pencil (edit) icon.
1. Select *Create secret* in the dropdown menu, then paste in your Griptape Cloud API key
1. Click *Save* to store the key as a secret that will be encrypted and used in this Structure. For future Structures, you will be able to re-use the same key by selecting *Secret reference*.
1. Repeat the preceding three steps (5 , 6, and 7) for the row labeled Key: `OPENAI_API_KEY`, Key: `ANTHROPIC_API_KEY`, and/or Key: `GOOGLE_API_KEY` using the corresponding API keys. You only need to provide one of these unless you want to compare models against each other.
1. Click *Create* to submit the form.

### What's Happening?

Once you have created the Structure, it will automatically begin deploying to Griptape Cloud. This process should take just a minute or two. While deployment is in progress, you will be directed to the Structure detail page where you can observe and track the deployment status as well as other details such as the GitHub repository and invocation URL.

After deployment is complete, your Structure is ready to run!

### Running your sample Structure

You can run Structures directly from the Griptape Cloud web console, via API, or through third party software applications. For this example, we will use the sample that you deployed above.

Follow these steps to run your structure.

1. Navigate to the Structures screen.

1. Select the structure you created from the list.

1. Click the *Runs* tab.

1. Click *Create run*.

1. In the Arguments field, enter the following text. If you want to use a different model, replace the argument `openai` with `anthropic` or `claude`. Note that arguments must be entered one per line, so be sure to preserve the line breaks as shown here.

    ```bash
    -p
    openai
    -s
    software programming
    -a
    Genghis Khan
    ```

1. Click *Create* to submit the form.

The structure will then begin running. It should take just a few seconds. During this time, you will see the input arguments and environment variables you provided. When the run completes you will see the resulting output, and you can also access the run logs for debugging purposes.

For more on running Structures, visit [Running a Structure](./run-structure.md) to learn how to run your newly deployed Structure.
