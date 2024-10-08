import sys
import threading
from concurrent.futures import Future

from exceptions import CSyncExceptionError


class CSync:
    def __init__(self):
        self.thread_local = threading.local()
        self.thread_local.current_task = None
        if sys._is_gil_enabled():
            raise CSyncExceptionError(
                "CSync requires the GIL to be disabled. Please use the free-threaded Python executable."
            )

    def run(self, coroutine):
        future = Future()

        def wrapper():
            try:
                self.thread_local.current_task = coroutine
                result = self._run_coroutine(coroutine)
                future.set_result(result)
            except Exception as e:
                future.set_exception(e)
            finally:
                self.thread_local.current_task = None

        threading.Thread(target=wrapper).start()
        return future

    def _run_coroutine(self, coroutine):
        try:
            while True:
                try:
                    yielded = next(coroutine)
                    if isinstance(yielded, CPendingParallel):
                        result = yielded.run()
                        coroutine.send(result)
                    else:
                        raise CSyncExceptionError(f"Unexpected yield value: {yielded}")

                except StopIteration as e:
                    return e.value
        except Exception as e:
            raise CSyncExceptionError(f"Error in coroutine execution: {str(e)}")


class CPendingParallel:
    def __init__(self, func, *args, **kwargs):
        self.func = func
        self.args = args
        self.kwargs = kwargs

    def run(self):
        return self.func(*self.args, **self.kwargs)


def cawait(obj):
    if not isinstance(obj, CPendingParallel):
        raise CSyncExceptionError("Can only await CPendingParallel objects")
    return (yield obj)
