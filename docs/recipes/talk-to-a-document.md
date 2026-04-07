Some LLM providers, such as [Anthropic](https://docs.anthropic.com/en/api/messages#body-messages-content) and [Amazon Bedrock](https://docs.aws.amazon.com/bedrock/latest/APIReference/API_runtime_DocumentBlock.html), offer the ability to pass documents directly to the LLM.

In this example, we pass a PDF document to the Agent using Anthropic's document message content format. The Agent then uses the document to answer questions about the paper.

We use [Task hooks](../griptape-framework/structures/tasks.md#hooks) to add and remove a log filter to truncate the logs before printing the large document content.

```python
--8<-- "docs/recipes/src/talk_to_a_document.py"
```

```
[12/23/24 09:37:47] INFO     PromptTask cc77e4c193c84a5986a4e02e56614d6b
                             Input: Document: application/pdf

                             What is the title and who are the authors of this paper?
[12/23/24 09:37:57] INFO     PromptTask cc77e4c193c84a5986a4e02e56614d6b
                             Output: The title of this paper is "Attention Is All You Need" and the authors are:

                             Ashish Vaswani, Noam Shazeer, Niki Parmar, Jakob Uszkoreit, Llion Jones, Aidan N. Gomez, Łukasz Kaiser, and Illia
                             Polosukhin.

                             The paper is from Google Brain, Google Research, and the University of Toronto. It introduces the Transformer model
                             architecture for sequence transduction tasks like machine translation.
```
