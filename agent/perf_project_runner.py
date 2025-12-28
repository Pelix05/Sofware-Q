import argparse
import subprocess
import shutil
import time
import json
import os
from pathlib import Path
import statistics
import threading

try:
    import psutil
except Exception:
    psutil = None


def run_command(cmd, cwd=None, timeout=None):
    try:
        proc = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=timeout)
        return proc.returncode, proc.stdout + proc.stderr
    except Exception as e:
        return -1, str(e)


def build_with_cmake(project_dir: Path, build_dir: Path):
    build_dir.mkdir(parents=True, exist_ok=True)
    rc, out = run_command(['cmake', '-S', str(project_dir), '-B', str(build_dir)], cwd=project_dir)
    if rc != 0:
        return False, out
    rc2, out2 = run_command(['cmake', '--build', str(build_dir), '-j', '4'], cwd=project_dir)
    return (rc2 == 0), (out + '\n' + out2)


def try_simple_compile(project_dir: Path, out_exe: Path):
    # Try to compile all .cpp files into a single exe using g++ if available
    cpp_files = list(project_dir.rglob('*.cpp'))
    if not cpp_files:
        return False, 'No .cpp sources found'
    gpp = shutil.which('g++') or shutil.which('clang++')
    if not gpp:
        return False, 'No g++/clang++ available in PATH'
    cmd = [gpp, '-O2', '-std=c++17', '-o', str(out_exe)] + [str(p) for p in cpp_files]
    rc, out = run_command(cmd, cwd=project_dir)
    return (rc == 0), out


def find_executables(project_dir: Path, build_dir: Path):
    exes = []
    # common locations
    for p in (build_dir, project_dir):
        if not p:
            continue
        # Windows .exe
        for f in p.rglob('*.exe'):
            exes.append(f)
        # UNIX style: files in bin or build output without extension
        for f in p.rglob('*'):
            try:
                if f.is_file() and os.access(str(f), os.X_OK) and f.suffix == '':
                    exes.append(f)
            except Exception:
                pass
    # unique
    uniq = []
    seen = set()
    for e in exes:
        if str(e.resolve()) not in seen:
            seen.add(str(e.resolve()))
            uniq.append(e)
    return uniq


def measure_run(exe_path: Path, timeout: int = 30):
    start = time.time()
    try:
        proc = subprocess.Popen([str(exe_path)], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    except Exception as e:
        return None, None, f'failed to start: {e}'

    peak_rss = 0
    if psutil:
        try:
            p = psutil.Process(proc.pid)
            while proc.poll() is None:
                mem = p.memory_info().rss
                if mem > peak_rss:
                    peak_rss = mem
                time.sleep(0.01)
            # one last check
            try:
                mem = p.memory_info().rss
                if mem > peak_rss:
                    peak_rss = mem
            except Exception:
                pass
        except Exception:
            # fallback: no psutil details
            proc.wait(timeout=timeout)
    else:
        try:
            proc.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            proc.kill()
    end = time.time()
    elapsed_ms = (end - start) * 1000.0
    out, err = '', ''
    try:
        out, err = proc.communicate(timeout=1)
        # ensure outputs are strings
        if isinstance(out, bytes):
            try:
                out = out.decode('utf-8', errors='replace')
            except Exception:
                out = str(out)
        if isinstance(err, bytes):
            try:
                err = err.decode('utf-8', errors='replace')
            except Exception:
                err = str(err)
    except Exception:
        pass
    return elapsed_ms, (peak_rss // 1024 if peak_rss else None), {'stdout': out, 'stderr': err, 'returncode': proc.returncode}


def run_benchmark_on_exe(exe_path: Path, runs=3, concurrency=1):
    runs_ms = []
    mems_kb = []
    outputs = []
    for i in range(runs):
        if concurrency <= 1:
            elapsed, peak_kb, meta = measure_run(exe_path)
            if elapsed is None:
                outputs.append({'error': meta})
                continue
            runs_ms.append(elapsed)
            if peak_kb:
                mems_kb.append(peak_kb)
            outputs.append(meta)
        else:
            # run `concurrency` processes in parallel and measure wall time
            threads = []
            results = [None] * concurrency

            def worker(idx):
                results[idx] = measure_run(exe_path)

            for t in range(concurrency):
                th = threading.Thread(target=worker, args=(t,))
                th.start()
                threads.append(th)
            for th in threads:
                th.join()
            # gather
            for res in results:
                if res and res[0] is not None:
                    runs_ms.append(res[0])
                    if res[1]:
                        mems_kb.append(res[1])
                    outputs.append(res[2])
                else:
                    outputs.append({'error': 'failed'})
    summary = {}
    if runs_ms:
        summary['cpu_bench_runs_ms'] = [round(x, 3) for x in runs_ms]
        summary['cpu_bench_ms'] = round(statistics.median(runs_ms), 3) if runs_ms else None
    if mems_kb:
        summary['mem_usage_kb'] = int(sum(mems_kb) / len(mems_kb))
    summary['details'] = outputs
    return summary


def run_load_test_on_exe(exe_path: Path, max_concurrency=8, step=1, runs=2):
    load = {}
    load['steps'] = []
    for c in range(1, max_concurrency + 1, step):
        try:
            summary = run_benchmark_on_exe(exe_path, runs=runs, concurrency=c)
            load['steps'].append({'concurrency': c, 'summary': summary})
        except Exception as e:
            load['steps'].append({'concurrency': c, 'error': str(e)})
    return load


def run_stress_test_on_exe(exe_path: Path, max_concurrency=32, timeout_per_try=30):
    stress = {'attempts': []}
    # escalate concurrency until failure or limit
    for c in [1, 2, 4, 8, 16, 24, 32]:
        if c > max_concurrency:
            break
        try:
            summary = run_benchmark_on_exe(exe_path, runs=1, concurrency=c)
            stress['attempts'].append({'concurrency': c, 'summary': summary})
            # detect failure: empty runs or returncode nonzero in details
            details = summary.get('details', [])
            failed = any((d.get('returncode') is None or d.get('returncode') != 0) for d in details if isinstance(d, dict))
            if failed:
                stress['conclusion'] = f'Failure observed at concurrency {c}'
                break
        except Exception as e:
            stress['attempts'].append({'concurrency': c, 'error': str(e)})
            stress['conclusion'] = f'Error at concurrency {c}: {e}'
            break
    return stress


def run_soak_test_on_exe(exe_path: Path, duration_s=60, concurrency=1):
    import time as _time
    soak = {'duration_s': duration_s, 'concurrency': concurrency, 'iterations': []}
    end_t = _time.time() + duration_s
    it = 0
    failures = 0
    latencies = []
    while _time.time() < end_t and it < 10000:
        it += 1
        res = run_benchmark_on_exe(exe_path, runs=1, concurrency=concurrency)
        st = res.get('single_thread') if isinstance(res.get('single_thread'), dict) else res
        runs_ms = st.get('cpu_bench_runs_ms') if st else None
        if runs_ms:
            latencies.extend(runs_ms)
        # detect failures
        details = st.get('details') if st and isinstance(st.get('details'), list) else []
        for d in details:
            if isinstance(d, dict) and (d.get('returncode') is None or d.get('returncode') != 0):
                failures += 1
        soak['iterations'].append({'iter': it, 'summary': res})
    if latencies:
        import statistics as _stats
        soak['avg_latency_ms'] = _stats.mean(latencies)
        soak['median_latency_ms'] = _stats.median(latencies)
    soak['failures'] = failures
    return soak


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--project', required=True, help='Path to uploaded project root')
    p.add_argument('--out', default='perf_report.json')
    p.add_argument('--runs', type=int, default=3)
    p.add_argument('--concurrency', type=int, default=1)
    p.add_argument('--modes', type=str, default='benchmark', help='Comma-separated modes: benchmark,load,stress,soak,concurrency,all')
    p.add_argument('--max-concurrency', type=int, default=8)
    p.add_argument('--load-step', type=int, default=1)
    p.add_argument('--soak-duration', type=int, default=60)
    p.add_argument('--soak-concurrency', type=int, default=1)
    args = p.parse_args()

    project = Path(args.project)
    if not project.exists():
        print('[!] Project path not found:', project)
        return

    build_dir = project / 'build_perf'
    perf = {}
    # Try CMake build first
    built = False
    built_out = ''
    if (project / 'CMakeLists.txt').exists():
        ok, out = build_with_cmake(project, build_dir)
        built = ok
        built_out = out
    # If not built and there are cpp files, try simple compile
    exe_candidates = []
    if not built:
        tmp_exe = project / 'project_single_exe.exe'
        ok2, out2 = try_simple_compile(project, tmp_exe)
        if ok2 and tmp_exe.exists():
            exe_candidates.append(tmp_exe)
            built = True
            built_out += '\n' + out2
    else:
        # find exe in build dir
        exe_candidates = find_executables(project, build_dir)

    # if none found, also search project root for exes
    if not exe_candidates:
        exe_candidates = find_executables(project, None)

    perf['build_succeeded'] = built
    perf['build_output'] = built_out
    perf['executables_found'] = [str(x) for x in exe_candidates]

    aggregate = {}
    modes = [m.strip().lower() for m in args.modes.split(',') if m.strip()]
    if 'all' in modes:
        modes = ['benchmark', 'load', 'stress', 'soak', 'concurrency']
    for exe in exe_candidates[:3]:  # limit to first 3 executables
        try:
            entry = {}
            if 'benchmark' in modes:
                entry['benchmark'] = run_benchmark_on_exe(exe, runs=args.runs, concurrency=1)
            if 'concurrency' in modes:
                entry['concurrency'] = run_benchmark_on_exe(exe, runs=args.runs, concurrency=args.concurrency)
            if 'load' in modes:
                entry['load'] = run_load_test_on_exe(exe, max_concurrency=args.max_concurrency, step=args.load_step, runs=2)
            if 'stress' in modes:
                entry['stress'] = run_stress_test_on_exe(exe, max_concurrency=max(8, args.max_concurrency))
            if 'soak' in modes:
                entry['soak'] = run_soak_test_on_exe(exe, duration_s=args.soak_duration, concurrency=args.soak_concurrency)
            aggregate[str(exe.name)] = entry
        except Exception as e:
            aggregate[str(exe.name)] = {'error': str(e)}

    perf['results'] = aggregate
    # Compute flattened top-level metrics for UI compatibility using first exe summary
    if exe_candidates:
        first = exe_candidates[0]
        first_summary = aggregate.get(first.name, {})
        # prefer benchmark -> concurrency -> fallback
        st = None
        if isinstance(first_summary.get('benchmark'), dict):
            st = first_summary.get('benchmark')
        elif isinstance(first_summary.get('concurrency'), dict):
            st = first_summary.get('concurrency')
        else:
            st = {}
        if st.get('cpu_bench_ms') is not None:
            perf['cpu_bench_ms'] = st.get('cpu_bench_ms')
        if st.get('cpu_bench_runs_ms') is not None:
            perf['cpu_bench_runs_ms'] = st.get('cpu_bench_runs_ms')
        if st.get('mem_usage_kb') is not None:
            perf['mem_usage_kb'] = st.get('mem_usage_kb')
        # multi-thread top-level
        mt = None
        if isinstance(first_summary.get('concurrency'), dict):
            mt = first_summary.get('concurrency')
        if mt and mt.get('cpu_bench_ms'):
            perf['mt_cpu_bench_ms'] = mt.get('cpu_bench_ms')

    # write to out file in project dir
    out_path = project / args.out
    with open(out_path, 'w', encoding='utf-8') as fo:
        json.dump(perf, fo, indent=2)
    print('[+] Wrote perf report to', out_path)


if __name__ == '__main__':
    main()
