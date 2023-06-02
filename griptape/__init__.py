from os import environ
__path__ = __import__("pkgutil").extend_path(__path__, __name__)
environ["TRANSFORMERS_VERBOSITY"] = "error"
