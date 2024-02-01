class NopException(Exception):
    def __init__(self, nop_class_name: str, nop_method_name: str):
        message = f"You have attempted to use a {nop_class_name}'s {nop_method_name} method. "
        "This likely originated from a vendor-specific config that does not provide an implementation of this functionality. "

        super().__init__(message)
