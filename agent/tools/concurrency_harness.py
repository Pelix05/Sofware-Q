import threading
import time
import json
import argparse

# Simple concurrency harness that runs named tasks in separate threads and
# reports completion. Designed to be robust and deterministic in reporting
# what finished (order may vary). It prints 'ALL_DONE' JSON at the end.


def worker(task_id, sleep_time, results):
    # simulate some work
    time.sleep(sleep_time)
    msg = f"Task {task_id} done"
    print(msg)
    results.append(task_id)


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--tasks', type=int, default=3)
    p.add_argument('--stagger', type=float, default=0.1)
    args = p.parse_args()

    tasks = args.tasks
    stagger = args.stagger
    threads = []
    results = []

    for i in range(tasks):
        # vary sleep times slightly so ordering is non-deterministic but predictable
        t = threading.Thread(target=worker, args=(i, stagger * (i % 3 + 1), results))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    # Print a final structured summary so tests can assert all tasks completed
    summary = { 'ALL_DONE': sorted(results) }
    print('SUMMARY_JSON:' + json.dumps(summary))
    # also exit 0 to indicate runtime success
    raise SystemExit(0)
