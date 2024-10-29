from griptape.drivers import LocalFileManagerDriver
from griptape.loaders import TextLoader

local_file_manager_driver = LocalFileManagerDriver()

loader = TextLoader(file_manager_driver=local_file_manager_driver)
text_artifact = loader.load("tests/resources/test.txt")

print(text_artifact.value)
