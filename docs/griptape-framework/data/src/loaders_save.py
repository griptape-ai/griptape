from griptape.drivers.file_manager.local import LocalFileManagerDriver
from griptape.loaders import TextLoader

loader = TextLoader(file_manager_driver=LocalFileManagerDriver())

data = loader.load("tests/resources/test.txt")

data.value = data.value.replace("foo", "bar")

loader.save("tests/resources/test.txt", data)
