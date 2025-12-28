#!/usr/bin/env python3
"""Lightweight performance tester for uploaded C/C++ workspaces.

Produces `perf_report.json` in the workspace with fields:
- cpu_bench_ms: median execution time (ms) of a small CPU-bound function
- mem_usage_kb: peak RSS during benchmark (KB) if psutil available
- load_test: {requests: N, concurrency: C, avg_latency_ms}

This is intentionally lightweight and safe to run on CI-like environments.
"""
from pathlib import Path
import time
import json
import statistics
import argparse
import subprocess
import os

try:
    import psutil
except Exception:
    psutil = None


def cpu_benchmark(iterations=1000000, repeats=5):
    def worker(n):
        s = 0
        for i in range(n):
            s += (i * 31) ^ (i >> 3)
        return s
    times = []
    for _ in range(repeats):
        t0 = time.perf_counter()
        worker(iterations)
        t1 = time.perf_counter()
        times.append((t1 - t0) * 1000.0)
    return statistics.median(times)


def mt_cpu_benchmark(iterations=300000, threads=4, repeats=3):
    import concurrent.futures
    def worker(n):
        s = 0
        for i in range(n):
            s += (i * 31) ^ (i >> 3)
        return s

    runs = []
    for _ in range(repeats):
        t0 = time.perf_counter()
        with concurrent.futures.ThreadPoolExecutor(max_workers=threads) as ex:
            futs = [ex.submit(worker, iterations) for _ in range(threads)]
            for f in futs:
                try:
                    f.result(timeout=30)
                except Exception:
                    pass
        t1 = time.perf_counter()
        runs.append((t1 - t0) * 1000.0)
    return statistics.median(runs)


def mem_snapshot_kb():
    if not psutil:
        return None
    p = psutil.Process()
    try:
        return int(p.memory_info().rss / 1024)
    except Exception:
        return None


def simple_load_test(commands, requests=20, concurrency=4):
    # Very small synthetic "load": run a command in subprocess many times concurrently
    # commands: list of shell command strings or a single command
    import concurrent.futures
    if isinstance(commands, str):
        cmd = commands
    else:
        cmd = commands[0] if commands else None
    if not cmd:
        return {'requests': 0, 'concurrency': 0, 'avg_latency_ms': None}

    def run_one(_):
        t0 = time.perf_counter()
        try:
            subprocess.run(cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=30)
            ok = True
        except Exception:
            ok = False
        t1 = time.perf_counter()
        return (ok, (t1 - t0) * 1000.0)

    latencies = []
    oks = 0
    with concurrent.futures.ThreadPoolExecutor(max_workers=concurrency) as ex:
        futures = [ex.submit(run_one, i) for i in range(requests)]
        for f in futures:
            ok, lat = f.result()
            if ok:
                oks += 1
            latencies.append(lat)
    avg = statistics.mean(latencies) if latencies else None
    return {'requests': requests, 'concurrency': concurrency, 'success': oks, 'avg_latency_ms': avg}


def detect_run_command(ws: Path):
    # Look for obvious runnable targets: scripts, make target, or simple binaries
    # Prefer a provided `perf_cmd.txt` in the workspace root which can specify the command to run.
    p = ws / 'perf_cmd.txt'
    if p.exists():
        try:
            return p.read_text(encoding='utf-8').strip()
        except Exception:
            return None
    # fallback: look for a simple executable in workspace root
    for f in ws.iterdir():
        if f.is_file() and os.access(str(f), os.X_OK):
            return str(f)
    return None


def io_benchmark(ws: Path, file_size_kb=1024, repeats=3):
    # write and read a temporary file of size ~file_size_kb KB
    import tempfile
    times = {'write_ms': [], 'read_ms': []}
    data = b'a' * 1024
    for _ in range(repeats):
        try:
            fd, p = tempfile.mkstemp(dir=str(ws))
            os.close(fd)
            t0 = time.perf_counter()
            with open(p, 'wb') as f:
                for i in range(file_size_kb):
                    f.write(data)
            t1 = time.perf_counter()
            times['write_ms'].append((t1 - t0) * 1000.0)
            t0 = time.perf_counter()
            with open(p, 'rb') as f:
                _ = f.read()
            t1 = time.perf_counter()
            times['read_ms'].append((t1 - t0) * 1000.0)
            try:
                os.remove(p)
            except Exception:
                pass
        except Exception:
            pass
    return {
        'write_ms_median': statistics.median(times['write_ms']) if times['write_ms'] else None,
        'read_ms_median': statistics.median(times['read_ms']) if times['read_ms'] else None,
        'file_size_kb': file_size_kb,
    }


def alloc_benchmark(iterations=2000000):
    # allocate and touch a list of small objects and measure time
    t0 = time.perf_counter()
    a = [i for i in range(1000)]
    for _ in range(int(iterations/1000)):
        a = [x+1 for x in a]
    t1 = time.perf_counter()
    # return time in ms and approximate memory delta as None (system dependent)
    return {'alloc_ms': (t1 - t0) * 1000.0}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--workspace', '-w', help='workspace to test', default='.')
    ap.add_argument('--out', '-o', help='output json file name', default='perf_report.json')
    args = ap.parse_args()

    ws = Path(args.workspace).resolve()
    outp = ws / args.out

    cpu_runs = []
    # multiple cpu runs to give a small distribution
    for r in range(3):
        cpu_runs.append(cpu_benchmark(iterations=1000000, repeats=3))
    cpu_ms = statistics.median(cpu_runs) if cpu_runs else None
    mem_kb = mem_snapshot_kb()

    # multi-threaded cpu bench
    mt_cpu = mt_cpu_benchmark(iterations=200000, threads=4, repeats=2)

    # io bench (write/read 1MB by default)
    io_res = io_benchmark(ws, file_size_kb=1024, repeats=2)

    # allocation micro-bench
    alloc_res = alloc_benchmark()

    cmd = detect_run_command(ws)
    if cmd:
        load = simple_load_test(cmd, requests=20, concurrency=4)
    else:
        load = {'requests': 0, 'concurrency': 0, 'avg_latency_ms': None}

    report = {
        'cpu_bench_ms': cpu_ms,
        'cpu_bench_runs_ms': cpu_runs,
        'mt_cpu_bench_ms': mt_cpu,
        'mem_usage_kb': mem_kb,
        'io_benchmark': io_res,
        'alloc_benchmark': alloc_res,
        'load_test': load,
    }
    try:
        outp.write_text(json.dumps(report, indent=2), encoding='utf-8')
        print('perf report written to', outp)
    except Exception as e:
        print('failed to write perf report:', e)

if __name__ == '__main__':
    main()
