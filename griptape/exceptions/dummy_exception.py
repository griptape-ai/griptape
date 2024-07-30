class DummyError(Exception):
    def __init__(self, dummy_class_name: str, dummy_method_name: str) -> None:
        message = (
            f"You have attempted to use a {dummy_class_name}'s {dummy_method_name} method. "
            "This likely originated from using a `StructureConfig` without providing a Driver required for this feature."
        )

        super().__init__(message)
