import urllib.request

import pandas as pd

from griptape.loaders import DataFrameLoader

urllib.request.urlretrieve("https://people.sc.fsu.edu/~jburkardt/data/csv/cities.csv", "cities.csv")

DataFrameLoader().load(pd.read_csv("cities.csv"))

urllib.request.urlretrieve("https://people.sc.fsu.edu/~jburkardt/data/csv/addresses.csv", "addresses.csv")

DataFrameLoader().load_collection([pd.read_csv("cities.csv"), pd.read_csv("addresses.csv")])
