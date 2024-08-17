from __future__ import annotations

from concurrent import futures
from typing import TypeVar

T = TypeVar("T")


def execute_futures_dict(fs_dict: dict[str, futures.Future[T]]) -> dict[str, T]:
    futures.wait(fs_dict.values(), timeout=None, return_when=futures.ALL_COMPLETED)

    return {key: future.result() for key, future in fs_dict.items()}


def execute_futures_list(fs_list: list[futures.Future[T]]) -> list[T]:
    futures.wait(fs_list, timeout=None, return_when=futures.ALL_COMPLETED)

    return [future.result() for future in fs_list]


def execute_futures_list_dict(fs_dict: dict[str, list[futures.Future[T]]]) -> dict[str, list[T]]:
    execute_futures_list([item for sublist in fs_dict.values() for item in sublist])

    return {key: [f.result() for f in fs] for key, fs in fs_dict.items()}
