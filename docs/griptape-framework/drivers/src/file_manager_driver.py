from griptape.drivers import LocalFileManagerDriver
from griptape.loaders import TextLoader

local_file_manager_driver = LocalFileManagerDriver()

loader = TextLoader(file_manager_driver=local_file_manager_driver)
text_artifact = loader.load("file_manager_driver_test_file.py")

print(text_artifact.value)
