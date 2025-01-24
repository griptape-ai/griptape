from griptape.drivers.file_manager.local import LocalFileManagerDriver

local_file_manager_driver = LocalFileManagerDriver()

# Download File
file_contents = local_file_manager_driver.load_file("tests/resources/test.txt")

print(file_contents)

# Upload File
response = local_file_manager_driver.save_file("tests/resources/test.txt", file_contents.value)

print(response)
