import subprocess
import re
from pathlib import Path
import argparse

BASE_DIR = Path(__file__).resolve().parent.parent
REPORT_FILE = Path(__file__).resolve().parent / "analysis_report_cpp.txt"
SNIPPET_FILE = Path(__file__).resolve().parent / "snippets" / "bug_snippets_cpp.txt"
SNIPPET_FILE.parent.mkdir(exist_ok=True)


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument('--repo-dir', type=str, help='Optional path to cpp_project root to analyze')
    return p.parse_args()


def run_command(cmd, cwd=None):
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=cwd)
    return result.stdout + result.stderr


def analyze_cpp(repo_dir: str = None):
    if repo_dir:
        cpp_repo = Path(repo_dir)
    else:
        cpp_repo = BASE_DIR / "cpp_project"
    print("[*] Running C++ analysis (cppcheck + optional clang-tidy)...")

    # Run cppcheck with a verbose configuration on each upload so the
    # full report is attached to the workspace. Use --enable=all to
    # surface all checks and include the message id in a compact template.
    # Use double quotes for the template so Windows `cmd.exe` handles it
    # correctly (single quotes are not recognized by cmd). Remove shell
    # redirection; `run_command` captures stdout/stderr.
    cpp_cmd = 'cppcheck --enable=all --inconclusive --force --template="{file}:{line}: {severity}: {id}: {message}" .'
    # Ensure cwd passed as string to subprocess.run on Windows
    output1 = run_command(cpp_cmd, cwd=str(cpp_repo))

    # clang-tidy (optional, if compile_commands.json exists)
    tidy_file = cpp_repo / "compile_commands.json"
    output2 = ""
    if tidy_file.exists():
        output2 = run_command("clang-tidy **/*.cpp -- -std=c++17", cwd=cpp_repo)

    combined = output1 + "\n" + output2

    # Server-side filtering: remove noisy/generated/build files to reduce UI noise.
    def _filter_report(text: str) -> str:
        import re
        out_lines = []
        for ln in text.splitlines():
            # Skip entries that are clearly from build folders or generated moc/qrc files
            if re.search(r'[\\/](?:build|release|debug)[\\/]', ln, flags=re.IGNORECASE):
                continue
            if re.search(r'\bmoc_\w+\.cpp\b', ln, flags=re.IGNORECASE):
                continue
            if re.search(r'\bqrc_\w+\.cpp\b', ln, flags=re.IGNORECASE):
                continue
            out_lines.append(ln)
        return '\n'.join(out_lines)

    filtered = _filter_report(combined)
    return filtered


def extract_snippets(report_content):
    # Extract error and warning level C/C++ issues. We now include
    # both errors and warnings so the UI can surface warnings as well.
    lines = report_content.splitlines()
    issue_hits = []
    for ln in lines:
        s = ln.strip()
        # match typical cppcheck/clang output like file.cpp:123: error: ...
        m = re.match(r"^([^\s:]+\.(?:cpp|cc|c|hpp|hh|h)):(\d+):.*", s)
        if m:
            # include lines that indicate errors or warnings
            if re.search(r"\berror\b|\bfatal error\b|undefined reference\b|\bwarning\b", s, flags=re.IGNORECASE):
                try:
                    issue_hits.append((m.group(1), int(m.group(2)), s))
                except Exception:
                    pass

    print(f"[*] Found {len(issue_hits)} C/C++ issues (errors+warnings included)")

    snippets = []
    for file_path, line_num, full_line in issue_hits[:200]:
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


if __name__ == "__main__":
    args = parse_args()
    report = analyze_cpp(repo_dir=args.repo_dir)
    REPORT_FILE.write_text(report, encoding="utf-8")
    print(f"[+] C++ analysis saved to {REPORT_FILE}")
    extract_snippets(report)
