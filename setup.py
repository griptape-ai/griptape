import pathlib
from warpspeed import VERSION
from setuptools import setup, find_packages

HERE = pathlib.Path(__file__).parent
README = (HERE / "README.md").read_text()

setup(
    name="warpspeed",
    version=VERSION,
    description="Python framework for AI workflows and pipelines.",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/usewarpspeed/warpspeed",
    author_email="hello@warpspeed.cc",
    author="Vasily Vasinov", 
    license="Apache 2.0",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "python-dotenv>=0.21",
        "openai>=0.27",
        "attrs>=22",
        "jinja2>=3.1",
        "jsonschema>=4",
        "marshmallow>=3",
        "marshmallow-enum>=1.5",
        "graphlib",
        "llama_index==0.4.23",
        "wikipedia",
        "tiktoken>=0.3",
        "gspread",
        "sqlalchemy>1",
        "rich>=13",
        "trafilatura",
        "requests",
        "googlesearch-python@git+https://github.com/usewarpspeed/googlesearch.git#egg=googlesearch-python",
        "stopit"
    ]
)
