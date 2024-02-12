class DummyException(Exception):
    def __init__(self, dummy_class_name: str, dummy_method_name: str):
        message = f"You have attempted to use a {dummy_class_name}'s {dummy_method_name} method. "
        "This likely originated from a vendor-specific config that does not provide an implementation of this functionality. "

        super().__init__(message)
