In this example, we use a [Local File Manager Driver](../griptape-framework/drivers/file-manager-drivers.md) to access the `images` directory in the current working directory.
We then pass this Driver to a [File Manager Tool](../griptape-tools/official-tools/file-manager-tool.md) and an [Image Query Tool](../griptape-tools/official-tools/image-query-tool.md) to interact with the images in the directory.

Note that if you update the `workdir` on a [File Manager Driver](../griptape-framework/drivers/file-manager-drivers.md), it's important to pass that Driver to all the Tools that need to access the same directory.

```python
import os

import requests
from griptape.drivers import LocalFileManagerDriver
from griptape.engines import ImageQueryEngine
from griptape.loaders import ImageLoader
from griptape.structures import Agent
from griptape.tools import FileManagerTool, ImageQueryTool

# Create the images directory if it doesn't exist
images_dir = f"{os.getcwd()}/images"
os.makedirs(images_dir, exist_ok=True)

# Download an image from the web
image_url = "https://picsum.photos/200/300"
image_path = f"{images_dir}/image.jpg"
response = requests.get(image_url)
with open(image_path, "wb") as file:
    file.write(response.content)

driver = LocalFileManagerDriver(workdir=images_dir)
agent = Agent(
    tools=[
        FileManagerTool(file_manager_driver=driver),
        ImageQueryTool(image_query_engine=ImageQueryEngine(), image_loader=ImageLoader(file_manager_driver=driver)),
    ]
)

agent.run("What files are in the current directory?")
agent.run("What is in the file image.jpg?")
```
