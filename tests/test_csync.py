import pytest
import time
import math
import os
from csync import CSync, cparallel, cawait, to_parallel


@pytest.fixture(scope="session", autouse=True)
def check_free_threading():
    import sys

    if sys._is_gil_enabled():
        pytest.skip("These tests require the GIL to be disabled. Please use the free-threaded Python executable.")


@pytest.fixture
def csync():
    return CSync()


@cparallel
def cpu_intensive_task(duration):
    start_time = time.time()
    result = 0
    while time.time() - start_time < duration:
        result += math.sqrt(result + 1)
    return result


def test_parallel_execution(csync):
    num_tasks = os.cpu_count() or 4
    task_duration = 5

    def parallel_coroutine():
        tasks = [to_parallel(cpu_intensive_task, task_duration) for _ in range(num_tasks)]
        results = yield cawait(tasks)
        return results

    start_time = time.time()
    csync.run(parallel_coroutine()).result()
    total_time = time.time() - start_time

    assert total_time < (
        task_duration * 1.5
    ), f"Execution time ({total_time:.2f}s) suggests tasks might not be running in parallel"


def test_sequential_vs_parallel(csync):
    num_tasks = os.cpu_count() or 4
    task_duration = 2

    def sequential_coroutine():
        results = []
        for _ in range(num_tasks):
            result = yield cawait(to_parallel(cpu_intensive_task, task_duration))
            results.append(result)
        return results

    def parallel_coroutine():
        tasks = [to_parallel(cpu_intensive_task, task_duration) for _ in range(num_tasks)]
        results = yield cawait(tasks)
        return results

    start_time = time.time()
    csync.run(sequential_coroutine()).result()
    sequential_time = time.time() - start_time

    start_time = time.time()
    csync.run(parallel_coroutine()).result()
    parallel_time = time.time() - start_time

    speedup = sequential_time / parallel_time
    assert speedup > 1.5, f"Parallel execution should be significantly faster. Speedup: {speedup:.2f}x"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
