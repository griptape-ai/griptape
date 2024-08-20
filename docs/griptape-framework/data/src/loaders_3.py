from pathlib import Path

from griptape.loaders import CsvLoader
from griptape.utils import load_file, load_files

# Load a single CSV file
CsvLoader().load(Path("tests/resources/cities.csv").read_text())
# You can also use the load_file utility function
CsvLoader().load(load_file("tests/resources/cities.csv"))

# Load multiple CSV files
CsvLoader().load_collection(
    [Path("tests/resources/cities.csv").read_text(), Path("tests/resources/addresses.csv").read_text()]
)
# You can also use the load_files utility function
CsvLoader().load_collection(list(load_files(["tests/resources/cities.csv", "tests/resources/addresses.csv"]).values()))
