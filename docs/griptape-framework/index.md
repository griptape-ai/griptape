# Griptape: A Python Framework for Building Generative AI Applications

Griptape is a Python framework designed to simplify the development of generative AI applications. It offers a set of straightforward, flexible abstractions for working with areas such as Large Language Models (LLMs), Retrieval-Augmented Generation (RAG), and much more.

1. **Technology-agnostic**: Griptape is designed to work with any capable LLM, data store, and backend through the abstraction of Drivers.
1. **Minimal prompt engineering**: It’s much easier to reason about code written in Python, not natural languages. Griptape aims to default to Python in most cases unless absolutely necessary.

## Why Consider a Framework?

If you're just beginning to experiment with generative AI, it's often best to start by building simple applications from scratch. However, as your project grows in complexity, a framework like Griptape can provide structure and best practices that help you maintain clarity and scalability.

Griptape strives to be transparent about the underlying AI techniques it uses. Nevertheless, having some foundational knowledge of LLMs and related technology will be helpful when building more sophisticated applications.

## Prerequisites

### 1. OpenAI API Key

By default, Griptape uses [OpenAI](https://openai.com/) for LLM interactions. We’ll learn how to change this via [Prompt Drivers](./drivers/prompt-drivers.md) later. For now:

1. Obtain an [OpenAI API key](https://platform.openai.com/api-keys).
1. Set it as an environment variable:
    ```bash
    export OPENAI_API_KEY="your-api-key"
    ```

!!! info

    Drivers are a primary building block of Griptape and Prompt Drivers handle all the details when prompting the model with input.

    Prompt Drivers are model agnostic, letting you switch out LLM providers without changing application code.

!!! tip

    To securely and easily manage environment variables, check out tools like [python-dotenv](https://pypi.org/project/python-dotenv/) or [mise](https://mise.jdx.dev/environments/).

### 2. Install Griptape

Griptape can be installed via multiple methods. Below are two popular approaches:

#### Using Uv

[uv](https://docs.astral.sh/uv/) is a fast, user-friendly dependency manager. If you've used [poetry](https://python-poetry.org/), `uv` is a similar project but with a focus on simplicity and speed.

1. [Install `uv`](https://docs.astral.sh/uv/getting-started/installation/).

1. Initialize a new project:

    ```bash
    uv init griptape-quickstart
    ```

1. Change into the new directory:

    ```bash
    cd griptape-quickstart
    ```

1. Add Griptape as a dependency:

    ```bash
    uv add griptape[all]
    ```

1. A [virtual environment](https://docs.astral.sh/uv/pip/environments/#python-environments) will be automatically created. Activate it:

    ```bash
    source .venv/bin/activate
    ```

    !!! note

        If you use another shell (like `fish`), this command may differ.

    !!! tip

        If you’re using [mise](https://mise.jdx.dev/), you can configure it to automatically [activate your virtual environment](https://mise.jdx.dev/lang/python.html#automatic-virtualenv-activation).

#### Using Pip

If `uv` isn’t your style, you can always install Griptape using `pip`:

```bash
pip install "griptape[all]" -U
```

#### Installing Extras

Griptape provides "extras" that enable specific features and third-party integrations. If you're new to Griptape, consider installing `[all]` to unlock its full functionality. This ensures you have everything you need right from the start.

However, for a more streamlined setup or if you only need certain features, you have two primary options:

1. **Core Dependencies**: These provide the minimal, foundational set of libraries for Griptape to run most default features.

1. **Extras**: These are additional, vendor-specific drivers (e.g., for Anthropic or Pinecone). Any driver requiring an extra will indicate this in the documentation.

For a core-only installation:

```bash
uv add griptape
```

To install specific extras—such as Anthropic and Pinecone drivers—use:

```bash
uv add "griptape[drivers-prompt-anthropic,drivers-vector-pinecone]"
```

## Prompt Task

With everything set up, let’s start building! One of Griptape’s core abstractions is a [Task](./structures/tasks.md). We'll start with a [Prompt Task](./structures/tasks.md#prompt-task) to prompt the LLM with some text.

Create a file named `app.py` and add:

=== "Code"

    ```python
    --8<-- "docs/griptape-framework/src/index_1.py"
    ```

=== "Logs"

    ```text
    --8<-- "docs/griptape-framework/logs/index_1.txt"
    ```

Then run:

```bash
python app.py
```

!!! tip

    Whenever you see a “Logs” tab in the Griptape documentation, you can click it to view logs and outputs.

If you got a response from the model, congrats! You’ve created your first generative AI application with Griptape.
This introductory guide sticks to the [Prompt Task](./structures/tasks.md#prompt-task), but Griptape supports a wide range of [Tasks](./structures/tasks.md). Explore them to see what else you can do.

## Changing Models

!!! info

    This example briefly demonstrates swapping out the underlying model. If you’d prefer to continue using the default OpenAI integration, feel free to skip ahead.

Griptape’s “Prompt Drivers” make switching model providers simple. For instance, to use [Anthropic](https://www.anthropic.com/), follow the same steps you used for the OpenAI key, but this time set an [Anthropic API key](https://console.anthropic.com/settings/keys):

```bash
export ANTHROPIC_API_KEY="your-api-key"
```

Then import [Anthropic Prompt Driver](./drivers/prompt-drivers.md#anthropic) and pass it to your Task:

=== "Code"

    ```python
    --8<-- "docs/griptape-framework/src/index_2.py"
    ```

=== "Logs"

    ```text
    --8<-- "docs/griptape-framework/logs/index_2.txt"
    ```

Run the script again to see a similar output. Notice you didn’t have to change any of the application-level logic; you only changed the driver.

For the remainder of this guide, we’ll revert to the [OpenAI Chat Prompt Driver](https://docs.griptape.ai/stable/griptape-framework/drivers/prompt-drivers.mdopenai-chat):

=== "Code"

    ```python
    --8<-- "docs/griptape-framework/src/index_3.py"
    ```

=== "Logs"

    ```text
    --8<-- "docs/griptape-framework/logs/index_3.txt"
    ```

If you’d like to keep using Anthropic, be sure to adjust code accordingly.

## Templating

Griptape uses the popular [Jinja](https://jinja.palletsprojects.com/en/stable/) templating engine to help create dynamic prompts. Let’s adapt our Prompt Task to utilize a Jinja template:

=== "Code"

    ```python
    --8<-- "docs/griptape-framework/src/index_4.py"
    ```

=== "Logs"

    ```text
    --8<-- "docs/griptape-framework/logs/index_4.txt"
    ```

Here, `{{ args }}` is rendered at runtime, allowing you to dynamically insert data into the prompt.

!!! info

    `args` is a special attribute added to the Task’s context. Depending on the type of Task, it may also have access to additional context variables.

For static, key-value data, we can add `context` to our Task:

=== "Code"

    ```python
    --8<-- "docs/griptape-framework/src/index_5.py"
    ```

=== "Logs"

    ```text
    --8<-- "docs/griptape-framework/logs/index_5.txt"
    ```

These two methods allow you to build more versatile, data-driven prompts. Next, we’ll discuss steering the LLM’s output using Griptape’s Rule system.

## Rules

LLMs can be unpredictable. Getting them to follow specific instructions can be challenging. Griptape addresses this by providing [Rules and Rulesets](./structures/rulesets.md), which offer a structured approach to steering the model’s output.

For example, we can create a simple Rule that gives the LLM a name:

=== "Code"

    ```python
    --8<-- "docs/griptape-framework/src/index_6.py"
    ```

=== "Logs"

    ```text
    --8<-- "docs/griptape-framework/logs/index_6.txt"
    ```

!!! info

    Rules are placed in the LLM’s [system prompt](https://promptengineering.org/system-prompts-in-large-language-models/), which typically yields the highest likelihood that the model will adhere to them.
    even so, LLMs still sometimes have minds of their own and will not follow Rules 100% of time

!!! tip

    While we typically recommend you stick to Rule-based steering, you can always [override the system prompt](./structures/rulesets.md#overriding-system-prompts) with a custom one.
    Though pay close attention to the discussed tradeoffs that come with this approach.

Multiple rules can be grouped into `Ruleset`s. Let’s refactor our code to use more than one Ruleset:

=== "Code"

    ```python
    --8<-- "docs/griptape-framework/src/index_7.py"
    ```

=== "Logs"

    ```text
    --8<-- "docs/griptape-framework/logs/index_7.txt"
    ```

!!! info

    Providing a `rules` list automatically creates a default `Ruleset`. This is great for getting started, but we recommend explicitly defining `Ruleset`s for more complex applications.

Griptape also includes a specialized Rule, [JsonSchemaRule](./structures/rulesets.md#json-schema), which inserts a JSON Schema into the system prompt, ensuring the LLM attempts to return structured, machine-readable data:

=== "Code"

    ```python
    --8<-- "docs/griptape-framework/src/index_8.py"
    ```

=== "Logs"

    ```text
    --8<-- "docs/griptape-framework/logs/index_8.txt"
    ```

!!! note

    The `typing.cast` usage is optional, but helps satisfy our type-checker, [pyright](https://github.com/microsoft/pyright). We’re actively working to improve Griptape’s type hints to avoid clunky casts like this.

Now let’s explore an even more robust way to enforce structured outputs.

## Structured Output

While a `JsonSchemaRule` can encourage the LLM to return structured data, it doesn’t provide guarantees, especially for complex schemas. For stronger enforcement, Griptape’s Prompt Drivers support [Structured Output](./drivers/prompt-drivers.md#structured-output).

Structured Output uses the LLM provider’s built-in API features to produce outputs in a well-defined schema. It also simplifies parsing, so you can work directly with Python objects rather than manual JSON parsing.

Let’s update our Task to use Structured Output:

=== "Code"

    ```python
    --8<-- "docs/griptape-framework/src/index_9.py"
    ```

=== "Logs"

    ```text
    --8<-- "docs/griptape-framework/logs/index_9.txt"
    ```

The LLM response is not only formatted correctly, but automatically parsed into a Python object.

!!! tip

    You can use either [pydantic](https://docs.pydantic.dev/latest/) or [schema](https://github.com/keleshev/schema) to define your schemas. We recommend pydantic for its ease of use.

!!! info

    If your chosen model provider doesn’t natively support structured output, Griptape employs multiple [fallback strategies](./drivers/prompt-drivers.md#prompttask). The final fallback is the `JsonSchemaRule`, which you saw earlier.

Now that we can generate structured responses, let’s make our Task more conversational using Griptape’s memory features.

## Conversation Memory

By default, each LLM call is stateless. If you want the model to recall previous interactions, use [Conversation Memory](./structures/conversation-memory.md). It tracks Task run history, providing context for the current run.

=== "Code"

    ```python
    --8<-- "docs/griptape-framework/src/index_10.py"
    ```

=== "Logs"

    ```text
    --8<-- "docs/griptape-framework/logs/index_10.txt"
    ```

!!! tip

    You can customize where the conversation is stored by providing a [Conversation Memory Driver](./drivers/conversation-memory-drivers.md).

With that set up, the LLM will now remember our previous exchanges. Let’s move on to enabling the model to perform external actions through Tools.

## Tools

LLMs themselves cannot browse the internet or perform external actions. You can enable these abilities via [Tools](./tools/index.md). A “Tool” is simply a Python class, and any method marked with the `@activity` decorator becomes available to the LLM.

Griptape comes with a collection of built-in Tools. Below is an example that uses a web search and scrape Tool:

=== "Code"

    ```python
    --8<-- "docs/griptape-framework/src/index_11.py"
    ```

=== "Logs"

    ```text
    --8<-- "docs/griptape-framework/logs/index_11.txt"
    ```

!!! info

    Many built-in Tools either provide general-purpose functions (e.g., [CalculatorTool](./tools/official-tools/index.md#calculator)) or are Driver-based to support exchanging external providers (e.g., [WebSearchTool](./tools/official-tools/index.md#web-search)).

Tools are a powerful method for extending the LLM’s capabilities. Consider [writing your own Tools](./tools/custom-tools/index.md) to enable more specialized functionality.

At this point, we have a Task that can handle real-world operations. Now let’s look at orchestrating multiple Tasks.

## Structures

So far, we’ve only worked with individual Tasks. As your app becomes more complex, you may want to organize multiple Tasks that execute in sequence or in parallel.

Griptape provides three Structures:

- **Agent**: A lightweight wrapper around a single `PromptTask`. Great for quick usage but still under the hood is just a `PromptTask`.
- **Pipeline**: Executes Tasks in a specific, linear order.
- **Workflow**: Creates highly parallel [DAGs](https://en.wikipedia.org/wiki/Directed_acyclic_graph), allowing you to fan out and converge Tasks.

Of the three, `Workflow` is generally the most versatile. `Agent` and `Pipeline` can be handy in certain scenarios but are less frequently needed if you’re comfortable just orchestrating Tasks directly.

Let’s place our `project-research` Task into a `Workflow` so multiple Tasks can run in parallel:

=== "Code"

    ```python
    --8<-- "docs/griptape-framework/src/index_12.py"
    ```

=== "Logs"

    ```text
    --8<-- "docs/griptape-framework/logs/index_12.txt"
    ```

!!! warning

    Unlike `PromptTask.run()`, calling `Workflow.run()` returns the `Workflow` instance itself. To see final results, use `Workflow.output`.

!!! info

    Rulesets applied to a Structure are inherited by all child Tasks.

!!! note

    Notice that we've removed the explicit Conversation Memory setup. Structures automatically handle memory for their child Tasks.

A `Workflow` can handle complex branching and merging of Tasks. Next, we’ll look at automatically summarizing large amounts of text with minimal code changes.

!!! info

    Much of Griptape's current documentation uses Structures. In particular, the `Agent` Structure.
    We are in the process of updating the documentation to include more Task-centric examples.
    Until then, know that an `Agent` is nothing more than a Structure with a single Task, usually a `PromptTask`.

## Engines

Griptape’s Engines provide higher-level patterns for common generative AI tasks. A typical example is summarizing text that may exceed the LLM’s input limits. Griptape’s [PromptSummaryEngine](./engines/summary-engines.md) automatically chunks text and merges the partial summaries into a final result.

!!! question

    *Couldn’t we just feed all the text into the LLM and say “summarize”?*

    Yes, but LLMs have a token limit. `PromptSummaryEngine` helps you handle text that goes beyond that limit by processing it in smaller parts.

    The role of an Engine is to provide you with a higher-level abstraction that simplifies common tasks ([summary](./engines/summary-engines.md), [RAG](./engines/rag-engines.md), [evals](./engines/eval-engines.md), [extraction](./engines/extraction-engines.md)).

### Directly Using PromptSummaryEngine

Engines can be used standalone or integrated into Tasks. To illustrate, let’s summarize the outputs of our Workflow:

=== "Code"

    ```python
    --8<-- "docs/griptape-framework/src/index_13.py"
    ```

=== "Logs"

    ```text
    --8<-- "docs/griptape-framework/logs/index_13.txt"
    ```

This produces a concise summary. But one strength of a Workflow is its ability to fan out and converge results. Let’s remove the direct `PromptSummaryEngine` usage and use a built-in summary Task instead.

### TextSummaryTask

The [TextSummaryTask](./structures/tasks.md#text-summary-task) leverages the `PromptSummaryEngine` behind the scenes. We’ll have our project-research Tasks converge into one summary Task:

=== "Code"

    ```python
    --8<-- "docs/griptape-framework/src/index_14.py"
    ```

=== "Logs"

    ```text
    --8<-- "docs/griptape-framework/logs/index_14.txt"
    ```

!!! info

    `{{ parents_output_text }}` is an automatic context variable that contains the text output of all parent Tasks in the Workflow.

!!! info

    Notice we assign `child_ids` to our parallel `PromptTask`s and set an `id` on the `TextSummaryTask`. This ensures the Workflow correctly connects their outputs.

Finally, let’s visualize our Workflow:

=== "Code"

    ```python
    --8<-- "docs/griptape-framework/src/index_15.py"
    ```

=== "Logs"

    ```text
    --8<-- "docs/griptape-framework/logs/index_15.txt"
    ```

Visit the printed URL in your logs to view a diagram illustrating the Workflow’s structure:

![Workflow Diagram](https://mermaid.ink/svg/Z3JhcGggVEQ7CglQcm9qZWN0LVJlc2VhcmNoLURqYW5nby0tPiBTdW1tYXJ5OwoJUHJvamVjdC1SZXNlYXJjaC1GbGFzay0tPiBTdW1tYXJ5OwoJUHJvamVjdC1SZXNlYXJjaC1GYXN0YXBpLS0+IFN1bW1hcnk7CglQcm9qZWN0LVJlc2VhcmNoLUxpdGVzdGFyLS0+IFN1bW1hcnk7CglTdW1tYXJ5Ow==)

## Conclusion and Next Steps

That’s it—you’ve built your first generative AI application with Griptape, exploring:

- Simple and advanced Task usage
- Dynamic prompt creation with Jinja templating
- Structured output for more reliable data handling
- Conversation memory for stateful interactions
- Tools for extending LLM capabilities
- Parallel Task orchestration with Workflows
- Text summarization using Engines

This is just the tip of the iceberg. For topic-based guides, continue exploring the Griptape documentation.
For more detailed guides, demos, and advanced techniques, check out [Griptape Tradeschool](https://learn.griptape.ai/latest/).
