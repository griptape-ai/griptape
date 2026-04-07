from pathlib import Path

from griptape.loaders import CsvLoader

# Load a single CSV file
CsvLoader().load("tests/resources/cities.csv")
# You can also pass a Path object
CsvLoader().load(Path("tests/resources/cities.csv"))

# Load multiple CSV files
CsvLoader().load_collection([Path("tests/resources/cities.csv"), "tests/resources/addresses.csv"])
