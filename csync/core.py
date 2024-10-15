import sys
import threading
from concurrent.futures import Future, ThreadPoolExecutor, as_completed
from typing import Any, Callable
import os

from .exceptions import CSyncExceptionError


class CSync:
    def __init__(self):
        if sys._is_gil_enabled():
            raise CSyncExceptionError(
                "CSync requires the GIL to be disabled. Please use the free-threaded Python executable."
            )
        self.executor = ThreadPoolExecutor(max_workers=os.cpu_count())

    def run(self, coroutine):
        future = Future()
        threading.Thread(target=self._run_wrapper, args=(coroutine, future)).start()
        return future

    def _run_wrapper(self, coroutine, future):
        try:
            result = self._run_coroutine(coroutine)
            future.set_result(result)
        except Exception as e:
            future.set_exception(e)

    def _run_coroutine(self, coroutine):
        try:
            value = None
            while True:
                try:
                    yielded = coroutine.send(value)
                    if isinstance(yielded, list) and all(isinstance(item, CPendingParallel) for item in yielded):
                        futures = [self.executor.submit(item.run) for item in yielded]
                        value = [future.result() for future in as_completed(futures)]
                    elif isinstance(yielded, CPendingParallel):
                        value = self.executor.submit(yielded.run).result()
                    else:
                        raise CSyncExceptionError(f"Unexpected yield value: {yielded}")
                except StopIteration as e:
                    return e.value
        except Exception as e:
            raise CSyncExceptionError(f"Error in coroutine execution: {str(e)}")


class CPendingParallel:
    def __init__(self, func: Callable[..., Any], *args: Any, **kwargs: Any):
        self.func = func
        self.args = args
        self.kwargs = kwargs

    def run(self):
        return self.func(*self.args, **self.kwargs)


def cawait(obj):
    if not isinstance(obj, (CPendingParallel, list)):
        raise CSyncExceptionError("Can only await CPendingParallel objects or lists of CPendingParallel objects")
    return obj
