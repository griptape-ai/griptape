from griptape.drivers import OpenAiImageQueryDriver
from griptape.engines import ImageQueryEngine
from griptape.structures import Agent
from griptape.tools import ImageQueryTool

# Create an Image Query Driver.
driver = OpenAiImageQueryDriver(model="gpt-4o")

# Create an Image Query Engine configured to use the driver.
engine = ImageQueryEngine(
    image_query_driver=driver,
)

# Create an Image Query Tool configured to use the engine.
tool = ImageQueryTool(
    image_query_engine=engine,
)

# Create an agent and provide the tool to it.
Agent(tools=[tool]).run("Describe the weather in the image tests/resources/mountain.png in one word.")
