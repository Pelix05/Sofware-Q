#!/usr/bin/env python3
"""Simulate uploading a ZIP or folder and run the same analysis pipeline the Flask worker uses.

Usage:
  py -3 simulate_upload.py --source <path-to-zip-or-folder>

This will create a workspace under agent/workspaces and run:
 - analyzer_cpp.py --repo-dir <target>
 - run_clang_tidy_safe.py --workspace <target> --analysis-json <ws>/analysis_report_cpp.json
 - clean_clang_output.py --analysis-json <ws>/analysis_report_cpp.json
 - fix_result_static.py <ws_id>
"""
import argparse
import tempfile
import shutil
import json
from pathlib import Path
from datetime import datetime
import re
import subprocess
import os

AGENT_DIR = Path(__file__).resolve().parent
TMP_ROOT = Path(os.environ.get('UPLOAD_TMP_ROOT', str(Path('D:/temp'))))
TMP_ROOT.mkdir(parents=True, exist_ok=True)


def safe_name_from(s: str) -> str:
    base = Path(s).stem
    return re.sub(r'[^A-Za-z0-9_-]', '_', base)


def run(cmd, cwd=None):
    print('> ', cmd)
    proc = subprocess.run(cmd, shell=True, cwd=cwd or str(AGENT_DIR))
    return proc.returncode


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--source', '-s', required=True, help='Path to a zip file or folder to upload')
    args = ap.parse_args()

    src = Path(args.source).resolve()
    if not src.exists():
        print('Source not found:', src)
        return 2

    # create a temp dir and place the files there (zip or copy)
    try:
        tmpdir = Path(tempfile.mkdtemp(dir=str(TMP_ROOT)))
    except Exception:
        tmpdir = Path(tempfile.mkdtemp())

    if src.is_dir():
        # copy content into tmpdir
        for item in src.iterdir():
            dest = tmpdir / item.name
            if item.is_dir():
                shutil.copytree(item, dest)
            else:
                shutil.copy2(item, dest)
    else:
        # assume zip
        try:
            import zipfile
            with zipfile.ZipFile(str(src), 'r') as zf:
                zf.extractall(str(tmpdir))
        except Exception as e:
            print('Failed to extract zip:', e)
            shutil.rmtree(tmpdir, ignore_errors=True)
            return 3

    # build workspace id
    file_base = safe_name_from(src.name)
    ts = datetime.now().strftime('%Y%m%d_%H%M%S')
    ws_id = f"{file_base}_{ts}"
    ws_root = AGENT_DIR / 'workspaces'
    ws_root.mkdir(parents=True, exist_ok=True)
    ws_dir = ws_root / ws_id
    counter = 1
    while ws_dir.exists():
        ws_id = f"{file_base}_{ts}_{counter}"
        ws_dir = ws_root / ws_id
        counter += 1
    # copy tempdir content into workspace/cpp_project
    target_root = ws_dir / 'cpp_project'
    try:
        shutil.copytree(tmpdir, target_root)
    except Exception as e:
        print('Failed to copy into workspace:', e)
        shutil.rmtree(tmpdir, ignore_errors=True)
        return 4

    # cleanup temp
    shutil.rmtree(tmpdir, ignore_errors=True)

    print('Created workspace:', ws_id)

    target = str(target_root)
    # create an initial minimal result.json so fix_result_static can merge into it
    try:
        init = {
            'workspace': ws_id,
            'run_id': ws_id,
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'language': 'cpp',
            'agent_root': str(AGENT_DIR),
            'static_summary': {'raw': ''},
        }
        (ws_dir / 'result.json').write_text(json.dumps(init, indent=2, ensure_ascii=False), encoding='utf-8')
    except Exception as e:
        print('Failed to write initial result.json:', e)
    # Run analyzer
    run(f'py -3 -u analyzer_cpp.py --repo-dir "{target}"', cwd=str(AGENT_DIR))

    # Run clang-tidy writing to workspace-local JSON
    ws_json = ws_dir / 'analysis_report_cpp.json'
    run(f'py -3 -u run_clang_tidy_safe.py --workspace "{target}" --analysis-json "{str(ws_json)}"', cwd=str(AGENT_DIR))

    # Clean workspace JSON
    run(f'py -3 -u clean_clang_output.py --analysis-json "{str(ws_json)}"', cwd=str(AGENT_DIR))

    # Merge into workspace result
    run(f'py -3 -u fix_result_static.py {ws_id}', cwd=str(AGENT_DIR))

    print('Simulation finished. Workspace path:', ws_dir)
    print('Result JSON:', ws_dir / 'result.json')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
