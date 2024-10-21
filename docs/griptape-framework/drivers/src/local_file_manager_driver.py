from griptape.drivers import LocalFileManagerDriver

local_file_manager_driver = LocalFileManagerDriver()

# Download File
file_contents = local_file_manager_driver.load_file("file_manager_driver_test_file.py")

print(file_contents)

# Upload File
response = local_file_manager_driver.save_file("file_manager_driver_test_file.py", file_contents)

print(response)
