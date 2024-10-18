from griptape.drivers import LocalFileManagerDriver


local_file_manager_driver = LocalFileManagerDriver()

# Download File
file_contents = local_file_manager_driver.try_load_file("local_file_manager_driver_test_file.py")

print(file_contents.decode())

# Upload File
response = local_file_manager_driver.try_save_file("local_file_manager_driver_test_file.py", file_contents)

print(response)
