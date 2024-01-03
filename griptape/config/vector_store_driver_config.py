from attrs import define, field


@define
class VectorStoreDriverConfig:
    args: dict = field()

    def __init__(self, *args: dict):
        self.__attrs_init__(*args)  # pyright: ignore
