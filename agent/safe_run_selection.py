#!/usr/bin/env python3
"""
Safely execute a selected code snippet by wrapping it in a function.

Usage:
  python safe_run_selection.py --snippet "<code>"
  python safe_run_selection.py --file path/to/snippet.py

This avoids running partial selections directly (which editors sometimes
save to temporary files and execute), causing syntax/indentation errors.
"""
import argparse
import tempfile
import textwrap
import subprocess
import sys
from pathlib import Path


def make_wrapped_module(snippet: str) -> str:
    # Indent snippet lines so they are inside a function body
    indented = '\n'.join('    ' + ln for ln in snippet.splitlines())
    # Build module explicitly without using dedent so we preserve indentation
    module_lines = []
    module_lines.append('def __selection_wrapper():')
    if indented:
        module_lines.append(indented)
    else:
        # empty body: add a pass to avoid syntax error
        module_lines.append('    pass')
    module_lines.append('')
    module_lines.append("if __name__ == '__main__':")
    module_lines.append("    try:")
    module_lines.append("        __selection_wrapper()")
    module_lines.append("    except Exception as e:")
    module_lines.append("        print('SAFE_RUN_ERROR:', e, file=__import__('sys').stderr)")
    module_lines.append("        raise")
    return '\n'.join(module_lines) + '\n'


def run_snippet(snippet: str):
    module_text = make_wrapped_module(snippet)
    with tempfile.NamedTemporaryFile('w', suffix='.py', delete=False, encoding='utf-8') as tf:
        tf.write(module_text)
        tmp_path = Path(tf.name)
    try:
        # Run with same python executable
        proc = subprocess.run([sys.executable, str(tmp_path)], capture_output=True, text=True)
        print(proc.stdout, end='')
        if proc.stderr:
            print(proc.stderr, end='', file=sys.stderr)
        return proc.returncode
    finally:
        try:
            tmp_path.unlink()
        except Exception:
            pass


def main():
    p = argparse.ArgumentParser(description='Safely run a selected code snippet')
    group = p.add_mutually_exclusive_group(required=True)
    group.add_argument('--snippet', type=str, help='Code snippet to run (pass as string)')
    group.add_argument('--file', type=str, help='Path to file containing snippet to run')
    args = p.parse_args()

    if args.file:
        path = Path(args.file)
        if not path.exists():
            print(f'Error: file not found: {path}', file=sys.stderr)
            sys.exit(2)
        snippet = path.read_text(encoding='utf-8')
    else:
        snippet = args.snippet or ''

    # Run and propagate exit code
    code = run_snippet(snippet)
    sys.exit(code)


if __name__ == '__main__':
    main()
