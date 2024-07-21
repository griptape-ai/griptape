import warnings


def deprecation_warn(message: str, stacklevel: int = 2) -> None:
    warnings.simplefilter("always", DeprecationWarning)
    warnings.warn(message, category=DeprecationWarning, stacklevel=stacklevel)
    warnings.simplefilter("default", DeprecationWarning)
