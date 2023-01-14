import pathlib
import galaxybrain
from setuptools import setup, find_packages

HERE = pathlib.Path(__file__).parent
README = (HERE / "README.md").read_text()

setup(
    name="galaxybrain",
    version=galaxybrain.VERSION,
    description="LLM extensions framework",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/vasinov/galaxybrain",
    author="Vasily Vasinov",
    author_email="vasinov@me.com",
    license="Apache 2.0",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "python-dotenv>=0.21",
        "openai>=0.26",
        "attrs>=22",
        "jinja2>=3.1"
    ]
)