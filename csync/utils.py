from typing import Any, Callable
from .core import CPendingParallel
from .decorators import cparallel


def to_parallel(func: Callable[..., Any], *args: Any, **kwargs: Any) -> CPendingParallel:
    @cparallel
    def wrapper():
        return func(*args, **kwargs)

    return CPendingParallel(wrapper)
