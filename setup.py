import pathlib
from warpspeed import VERSION
from setuptools import setup, find_packages

HERE = pathlib.Path(__file__).parent
README = (HERE / "README.md").read_text()

setup(
    name="warpspeed",
    version=VERSION,
    description="LLM extensions framework",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/warpspeed-labs/warpspeed",
    author="Vasily Vasinov",
    author_email="vasinov@me.com",
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
        "marshmallow-oneofschema>=3",
        "marshmallow-enum>=1.5",
        "graphlib",
        "llama_index",
        "wikipedia",
        "tiktoken",
        "numpy"
    ]
)
