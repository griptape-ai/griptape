from griptape.loaders import CsvLoader
from griptape.utils import load_file, load_files

# Load a single CSV file
with open("tests/resources/cities.csv") as f:
    CsvLoader().load(f.read())
# You can also use the load_file utility function
CsvLoader().load(load_file("tests/resources/cities.csv"))

# Load multiple CSV files
with open("tests/resources/cities.csv") as cities, open("tests/resources/addresses.csv") as addresses:
    CsvLoader().load_collection([cities.read(), addresses.read()])
# You can also use the load_files utility function
CsvLoader().load_collection(list(load_files(["tests/resources/cities.csv", "tests/resources/addresses.csv"]).values()))
