# csync

library for true parallelism in python, utilizing the power of free-threading(PEP 703), bootstrapped by [Strappa](https://github.com/buabaj/strappa)

## Performance

In my performance tests, CSync demonstrated significant speedups for CPU-bound tasks:

**A parallel program executed ~8 times faster than its sequential counterpart.**

This impressive result showcases the power of true parallelism enabled by CSync and Python's free-threading mode.

## Requirements

- Python 3.13 or later, built with the `--disable-gil` option (typically `python3.13t` or `python3.13t.exe`)

## Key Concepts

- **CSync**: The main class that manages parallel execution of coroutines.
- **cparallel**: A decorator for marking functions that should be executed in parallel.
- **cawait**: A function used within coroutines to yield control and wait for parallel tasks.
- **to_parallel**: A utility function to create parallel tasks from regular functions.

## Basic Usage

Here's a simple example of how to use CSync:

```python
import time
from csync import CSync, cparallel, cawait, to_parallel

@cparallel
def some_cpu_intensive_task(task_id, duration):
    print(f"Starting task {task_id}")
    start_time = time.time()
    result = 0
    while time.time() - start_time < duration:
        result += 1
    print(f"Task {task_id} completed in {time.time() - start_time:.2f} seconds")
    return result

def main():
    csync = CSync()
    num_tasks = 4
    task_duration = 2

    def parallel_coroutine():
        tasks = [to_parallel(some_cpu_intensive_task, i, task_duration) for i in range(num_tasks)]
        results = yield cawait(tasks)
        return results

    start_time = time.time()
    results = csync.run(parallel_coroutine()).result()
    total_time = time.time() - start_time

    print(f"\nAll tasks completed in {total_time:.2f} seconds")
    print(f"Results: {results}")

if __name__ == "__main__":
    main()
```

To run this script:

```bash
python3.13t your_script.py
```

## Important Notes

1. CSync requires the use of the free-threaded Python executable (python3.13t).
2. The free-threading mode in Python 3.13 is experimental and may have limitations or unexpected behaviors.
3. Not all Python libraries may be compatible with the free-threaded mode. Ensure that any third-party libraries you use are compatible.
4. While CSync allows for true parallelism, it's important to design your code carefully to avoid common concurrency issues like race conditions and deadlocks.

## Considerations

The performance benefits of CSync are most noticeable for CPU-bound tasks. I/O-bound tasks may not see significant improvements and might be better served by Python's built-in asyncio library.
