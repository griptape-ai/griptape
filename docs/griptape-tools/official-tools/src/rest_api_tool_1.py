from griptape.configs import Defaults
from griptape.configs.drivers import DriversConfig
from griptape.drivers import OpenAiChatPromptDriver
from griptape.memory.structure import ConversationMemory
from griptape.structures import Pipeline
from griptape.tasks import ToolkitTask
from griptape.tools import RestApiTool

Defaults.drivers_config = DriversConfig(
    prompt_driver=OpenAiChatPromptDriver(model="gpt-4o", temperature=0.1),
)

posts_client = RestApiTool(
    base_url="https://jsonplaceholder.typicode.com",
    path="posts",
    description="Allows for creating, updating, deleting, patching, and getting posts. Can also be used to access subresources.",
    request_body_schema={
        "title": str,
        "body": str,
        "userId": int,
    },
)

comments_client = RestApiTool(
    base_url="https://jsonplaceholder.typicode.com",
    path="comments",
    description="Allows for getting comments for a post.",
    request_query_params_schema={
        "postId": str,
    },
)

pipeline = Pipeline(
    conversation_memory=ConversationMemory(),
)

pipeline.add_tasks(
    ToolkitTask(
        "Output the title of post 1.",
        tools=[posts_client],
    ),
    ToolkitTask(
        "Create a post for user 1 with title 'My First Post' and body 'Hello world!'.",
        tools=[posts_client],
    ),
    ToolkitTask(
        "Update post 1 with a new body: 'Hello universe!'.",
        tools=[posts_client],
    ),
    ToolkitTask(
        "Patch post 1 with a new title: 'My First Post, A Journey'.",
        tools=[posts_client],
    ),
    ToolkitTask(
        "Delete post 1.",
        tools=[posts_client],
    ),
    ToolkitTask(
        "Output the body of all the comments for post 1.",
        tools=[posts_client],
    ),
    ToolkitTask(
        "Get the comments for post 1.",
        tools=[comments_client],
    ),
)

pipeline.run()
