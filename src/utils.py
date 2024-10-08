from typing import Any
from collections.abc import Callable
from core import CPendingParallel
from decorators import cparallel


def to_parallel(func: Callable[..., Any], *args: Any, **kwargs: Any) -> CPendingParallel:
    return CPendingParallel(cparallel(func), *args, **kwargs)
