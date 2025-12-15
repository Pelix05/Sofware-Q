import subprocess
import re
from pathlib import Path
import argparse
import sys
import shutil
import json
import os
import hashlib

BASE_DIR = Path(__file__).resolve().parent.parent
REPORT_FILE = Path(__file__).resolve().parent / "analysis_report_cpp.txt"
SNIPPET_FILE = Path(__file__).resolve().parent / "snippets" / "bug_snippets_cpp.txt"
SNIPPET_FILE.parent.mkdir(exist_ok=True)


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument('--repo-dir', type=str, help='Optional path to cpp_project root to analyze')
    return p.parse_args()


def find_qt_prefix():
    # Best-effort detection of common Qt installation roots. Returns a Path
    # suitable for passing to -DCMAKE_PREFIX_PATH or None if not found.
    cand_roots = []
    # Environment variables that sometimes point to Qt installs
    for ev in ("QTDIR", "QT_DIR", "Qt6_DIR", "Qt5_DIR"):
        v = os.environ.get(ev)
        if v:
            cand_roots.append(Path(v))

    # Common Windows install locations
    cand_roots += [Path(r) for r in (
        "C:/Qt",
        "C:/Program Files/Qt",
        "C:/msys64/mingw64/qt6",
        "C:/msys64/mingw64/qt5",
        "C:/msys64/mingw64",
    )]

    # Check each candidate for a cmake dir like lib/cmake/Qt6 or lib/cmake/Qt5
    for root in cand_roots:
        try:
            if not root:
                continue
            # direct check: lib/cmake/Qt6 or lib/cmake/Qt5
            if (root / "lib" / "cmake" / "Qt6").exists() or (root / "lib" / "cmake" / "Qt5").exists():
                return root
            # sometimes the Qt install layout uses <version> directories under root
            for sub in root.iterdir() if root.exists() else []:
                if (sub / "lib" / "cmake" / "Qt6").exists() or (sub / "lib" / "cmake" / "Qt5").exists():
                    return sub
        except Exception:
            continue
    return None


def run_command(cmd, cwd=None):
    # Accept either a string (runs via shell) or a list (runs without shell)
    try:
        if isinstance(cmd, (list, tuple)):
            result = subprocess.run(cmd, shell=False, capture_output=True, text=True, cwd=cwd)
        else:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=cwd)
        return (result.stdout or "") + (result.stderr or "")
    except FileNotFoundError as e:
        return f"[!] Command not found: {e}\n"
    except Exception as e:
        return f"[!] Command execution failed: {e}\n"


def analyze_cpp(repo_dir: str = None):
    if repo_dir:
        cpp_repo = Path(repo_dir)
    else:
        cpp_repo = BASE_DIR / "cpp_project"
    print("[*] Running C++ analysis (cppcheck)...")

    # cppcheck focus on warnings, performance, portability
    output1 = run_command(
        "cppcheck --enable=warning,performance,portability --inconclusive --quiet --force . 2>&1",
        cwd=cpp_repo,
    )

    # clang-tidy removed: keep analyzer focused on cppcheck only
    output2 = ''

    # Write a structured JSON summary alongside the plain text report
    try:
        json_obj = {
            'cppcheck': {
                'raw': output1 or '',
                'issue_count': 0,
            }
        }
        try:
            json_obj['cppcheck']['issue_count'] = sum(1 for ln in (output1 or '').splitlines() if re.search(r'error|warning', ln, flags=re.IGNORECASE))
        except Exception:
            json_obj['cppcheck']['issue_count'] = 0

        try:
            json_path = REPORT_FILE.with_suffix('.json')
            json_path.write_text(json.dumps(json_obj, indent=2, ensure_ascii=False), encoding='utf-8')
        except Exception:
            pass
    except Exception:
        pass

    return output1


def extract_snippets(report_content):
    # Extract error and warning-level C/C++ issues. We include warnings
    # as well as errors so that cppcheck findings are fully represented
    # in the snippet output. Matches typical lines like file.cpp:123: warning: ...
    lines = report_content.splitlines()
    error_hits = []
    for ln in lines:
        s = ln.strip()
        # match typical cppcheck/clang output like file.cpp:123: error: ...
        m = re.match(r"^([^\s:]+\.(?:cpp|cc|c|hpp|hh|h)):(\d+):.*", s)
        if m:
            # include lines that indicate errors or warnings
            if re.search(r"\berror\b|\bfatal error\b|undefined reference\b|\bwarning\b", s, flags=re.IGNORECASE):
                try:
                    error_hits.append((m.group(1), int(m.group(2)), s))
                except Exception:
                    pass

    print(f"[*] Found {len(error_hits)} C/C++ issues (including warnings)")

    snippets = []
    for file_path, line_num, full_line in error_hits[:200]:
        try:
            source_file = (BASE_DIR / file_path).resolve()
            if not source_file.exists():
                source_file = BASE_DIR / "cpp_project" / file_path

            if source_file.exists():
                lines = source_file.read_text(encoding="utf-8", errors="ignore").splitlines()
                start = max(0, line_num - 5)
                end = min(len(lines), line_num + 5)
                snippet = "\n".join(lines[start:end])
                entry = f"--- {file_path}:{line_num} ---\n{snippet}\n"
                snippets.append(entry)
        except Exception as e:
            print(f"[!] Failed to extract snippet from {file_path}:{line_num} -> {e}")

    if snippets:
        SNIPPET_FILE.write_text("\n\n".join(snippets), encoding="utf-8")
        print(f"[+] C++ snippets saved to {SNIPPET_FILE}")
    # return number of error-level findings so caller can act on it
    return len(error_hits)


if __name__ == "__main__":
    args = parse_args()
    report = analyze_cpp(repo_dir=args.repo_dir)
    REPORT_FILE.write_text(report, encoding="utf-8")
    print(f"[+] C++ analysis saved to {REPORT_FILE}")
    findings = extract_snippets(report)
    # Exit with non-zero when error-level findings exist so callers (tests) can detect failures
    if findings and findings > 0:
        print(f"[!] Exiting with code 2 due to {findings} error-level findings")
        raise SystemExit(2)
