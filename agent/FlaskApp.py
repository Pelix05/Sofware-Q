from flask import Flask, request, jsonify, render_template
import subprocess
import os
import tempfile
import re
from datetime import datetime
from pathlib import Path
import zipfile
import difflib
from lc_pipeline import (
    run_iterative_fix_py,
    run_pipeline,
    REPORT_PY,
    SNIPPETS_PY,
    REPORT_CPP,
    SNIPPETS_CPP,
    run_iterative_fix_cpp,
)
import shutil
from hf_test_generator import generate_tests
import logging
import threading
import json

# Configure simple logging to the console for debugging upload requests
logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(levelname)s %(message)s')
logger = logging.getLogger(__name__)
import uuid

AGENT_DIR = Path(__file__).resolve().parent
# Preferred temporary root (use D: by default; overridable via UPLOAD_TMP_ROOT)
TMP_ROOT = Path(os.environ.get('UPLOAD_TMP_ROOT', r'D:\temp'))
TMP_ROOT.mkdir(parents=True, exist_ok=True)

# Load optional .env file in agent root to populate environment for the Flask process.
# This allows configuring QT_INCLUDES, QT_LIBS, MSYS2_PATH, QT_BIN_PATH, etc. without
# hardcoding values into the script or the system environment. Lines starting with
# '#' are ignored. Simple KEY=VALUE parsing is used.
env_path = AGENT_DIR / '.env'
if env_path.exists():
    try:
        for ln in env_path.read_text(encoding='utf-8', errors='ignore').splitlines():
            ln = ln.strip()
            if not ln or ln.startswith('#'):
                continue
            if '=' not in ln:
                continue
            k, v = ln.split('=', 1)
            k = k.strip()
            v = v.strip().strip('"').strip("'")
            # Do not overwrite existing env vars set by the system
            if k not in os.environ:
                os.environ[k] = v
        logger.info('Loaded environment from %s', env_path)
    except Exception as _e:
        logger.warning('Failed to load .env: %s', _e)
else:
    # If there's no agent/.env, also try the repo root .env (user may have edited that)
    repo_env = AGENT_DIR.parent / '.env'
    if repo_env.exists():
        try:
            for ln in repo_env.read_text(encoding='utf-8', errors='ignore').splitlines():
                ln = ln.strip()
                if not ln or ln.startswith('#'):
                    continue
                if '=' not in ln:
                    continue
                k, v = ln.split('=', 1)
                k = k.strip()
                v = v.strip().strip('"').strip("'")
                if k not in os.environ:
                    os.environ[k] = v
            logger.info('Loaded environment from repo .env %s', repo_env)
        except Exception as _e:
            logger.warning('Failed to load repo .env: %s', _e)

app = Flask(__name__)

file_uploaded = False
uploaded_cpp_files = []


# --- Helper runner used by background worker and UI commands
def run_command(cmd, cwd=None):
    """Run a shell command and return combined stdout+stderr as string."""
    try:
        if isinstance(cwd, Path):
            cwd = str(cwd)
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=cwd)
        return (result.stdout or "") + (result.stderr or "")
    except Exception as e:
        return f"[Error] {e}"


def run_static_analysis_py():
    return run_command("py -3 -u analyzer_py.py", cwd=AGENT_DIR)


def run_dynamic_py():
    return run_command("py -3 -u dynamic_tester.py --py", cwd=AGENT_DIR)


def run_static_analysis_cpp():
    return run_command("py -3 -u analyzer_cpp.py", cwd=AGENT_DIR)


def run_dynamic_cpp():
    return run_command("py -3 -u dynamic_tester.py --cpp", cwd=AGENT_DIR)


def run_patch_cpp():
    run_pipeline(REPORT_CPP, SNIPPETS_CPP, lang="cpp")
    return "Patch pipeline executed."


def run_auto_fix_py():
    return run_iterative_fix_py(max_iters=5)

def handle_file_upload(file, file_type="py"):
    """Create an isolated workspace for an uploaded C/C++ (Qt) ZIP archive.

    Returns (workspace_info, error_message).
    workspace_info: { workspace: <id>, language: 'cpp', target: <path str> }
    """
    try:
        try:
            tmpdir_root = tempfile.mkdtemp(dir=str(TMP_ROOT))
        except Exception:
            # Fallback to default temp if D: is unavailable
            tmpdir_root = tempfile.mkdtemp()
        file_path = os.path.join(tmpdir_root, file.filename)
        file.save(file_path)

        # Extract ZIP
        if zipfile.is_zipfile(file_path):
            with zipfile.ZipFile(file_path, 'r') as zip_ref:
                zip_ref.extractall(tmpdir_root)
        else:
            shutil.rmtree(tmpdir_root)
            return None, "[Error] The uploaded file is not a valid ZIP file."

        # Find C++ source files in the extracted archive
        cpp_files = [f for f in Path(tmpdir_root).rglob("*.cpp")] + [f for f in Path(tmpdir_root).rglob("*.h")] + [f for f in Path(tmpdir_root).rglob("*.pro")]

        if not cpp_files:
            shutil.rmtree(tmpdir_root)
            return None, "No C/C++ (Qt) source files found in the uploaded zip."

        # Create isolated workspace for this upload
        file_base = Path(file.filename).stem if file and getattr(file, 'filename', None) else uuid.uuid4().hex
        safe_name = re.sub(r'[^A-Za-z0-9_-]', '_', str(file_base))
        ts = datetime.now().strftime('%Y%m%d_%H%M%S')
        ws_id = f"{safe_name}_{ts}"
        workspaces_root = AGENT_DIR / "workspaces"
        workspaces_root.mkdir(parents=True, exist_ok=True)
        ws_dir = workspaces_root / ws_id
        counter = 1
        while ws_dir.exists():
            ws_id = f"{safe_name}_{ts}_{counter}"
            ws_dir = workspaces_root / ws_id
            counter += 1
        ws_dir.mkdir()

        # Copy extracted files into workspace/cpp_project (preserve root)
        target_root = ws_dir / "cpp_project"
        shutil.copytree(tmpdir_root, target_root)
        shutil.rmtree(tmpdir_root)
        return {"workspace": ws_id, "language": "cpp", "target": str(target_root)}, None

    except Exception as e:
        try:
            shutil.rmtree(tmpdir_root)
        except Exception:
            pass
        return None, f"[Error] Upload failed: {str(e)}"


def compare_files(original_file, patched_file):
    """Compare the original and patched files to prove the patch was applied."""
    with open(original_file, 'r') as f1, open(patched_file, 'r') as f2:
        original_code = f1.readlines()
        patched_code = f2.readlines()

    diff = difflib.unified_diff(original_code, patched_code, fromfile='original_code.py', tofile='patched_code.py')

    return '\n'.join(diff)  # Return the diff as a string



def run_usability_checks(target_dir: str) -> dict:
    """Basic heuristics for usability checks.

    These are lightweight checks intended for Experiment 2: presence of
    README, example usage, build instructions, and obvious UX hints for
    C++/Qt projects. This is not a human-level usability test but provides
    automated signals for the report.
    """
    p = Path(target_dir)
    res = {
        'readme_exists': False,
        'readme_length': 0,
        'readme_has_usage': False,
        'has_pro_file': False,
        'has_cmakelists': False,
        'source_file_count': 0,
        'suggestions': [],
    }

    # README checks
    for name in ('README.md', 'README.rst', 'README.txt'):
        f = p / name
        if f.exists():
            txt = f.read_text(encoding='utf-8', errors='ignore')
            res['readme_exists'] = True
            res['readme_length'] = len(txt)
            if re.search(r'usage|install|build|run|example', txt, flags=re.IGNORECASE):
                res['readme_has_usage'] = True
            break

    # Project file checks (.pro for Qt, CMakeLists for cmake)
    if any(p.glob('*.pro')):
        res['has_pro_file'] = True
    if any(p.glob('CMakeLists.txt')):
        res['has_cmakelists'] = True

    # Count source files
    src_count = sum(1 for _ in p.rglob('*.cpp')) + sum(1 for _ in p.rglob('*.h'))
    res['source_file_count'] = src_count

    # Suggestions based on heuristics
    if not res['readme_exists']:
        res['suggestions'].append('Add a README with build and run instructions.')
    else:
        if not res['readme_has_usage']:
            res['suggestions'].append('Include a Usage/Example section in the README.')
    if res['has_pro_file'] and not res['has_cmakelists']:
        res['suggestions'].append('Project is Qt (.pro) — document required Qt version and dependencies.')
    if src_count == 0:
        res['suggestions'].append('No C++ source files detected; verify upload contains project sources.')

    return res


def run_documentation_checks(target_dir: str) -> dict:
    """Simple documentation presence and basic content checks.

    Returns a dict with found files and sections detected.
    """
    p = Path(target_dir)
    res = {
        'has_docs_folder': False,
        'docs_files': [],
        'has_user_manual': False,
        'readme_sections': [],
        'score': 0,
    }

    docs_dir = p / 'docs'
    if docs_dir.exists() and any(docs_dir.iterdir()):
        res['has_docs_folder'] = True
        res['docs_files'] = [str(x.name) for x in sorted(docs_dir.iterdir()) if x.is_file()]

    # look for user manual files
    for name in ('USER_MANUAL.md', 'USER_MANUAL.txt', '用户手册.md'):
        if (p / name).exists():
            res['has_user_manual'] = True
            res['docs_files'].append(name)

    # parse README for sections
    for name in ('README.md', 'README.rst', 'README.txt'):
        f = p / name
        if f.exists():
            txt = f.read_text(encoding='utf-8', errors='ignore')
            # simple heading search
            secs = re.findall(r'^#{1,3}\s*(.+)$', txt, flags=re.MULTILINE)
            res['readme_sections'] = secs
            # score: one point each for install, usage, license, contributing
            score = 0
            for s in ('install', 'usage', 'license', 'contribute', 'example'):
                if re.search(s, txt, flags=re.IGNORECASE):
                    score += 1
            res['score'] = score
            break

    return res


# === File Upload / Background Processing ===


@app.route('/upload', methods=['POST'])
def upload_file_route():
    """Handle ZIP file upload by creating a workspace and starting background work.

    Returns immediately with {status: 'Accepted', workspace: <id>} so the client
    can poll /status for results.
    """
    if 'file' not in request.files:
        return jsonify({"status": "Error", "error": "No file part"})
    file = request.files['file']
    file_type = request.form.get('file_type')
    logger.info("/upload request received: filename=%s, file_type=%s, remote=%s", file.filename if file else None, file_type, request.remote_addr)

    if file.filename == '':
        return jsonify({"status": "Error", "error": "No selected file"})

    workspace_info, err = handle_file_upload(file, file_type)
    if err:
        logger.info("/upload error: %s", err)
        return jsonify({"status": "Error", "error": err}), 400

    ws_id = workspace_info['workspace']
    lang = workspace_info['language']
    target = workspace_info['target']

    def bg():
        logger.info("[BG] Start processing workspace %s (cpp)", ws_id)
        try:
            # For uploaded C++ Qt projects we attempt to build/run tests where
            # possible. Default to 'auto' to avoid forcing heavy compiles on
            # every upload (prevents repeated long-running builds). If you
            # want to force compilation, set `CPP_QT_BEHAVIOR=force` in the
            # agent .env or pass a request flag to the upload endpoint.
            os.environ['CPP_QT_BEHAVIOR'] = os.environ.get('CPP_QT_BEHAVIOR', 'auto')

            # Prepare workspace path
            ws_path = AGENT_DIR / 'workspaces' / ws_id
            ws_path.mkdir(parents=True, exist_ok=True)

            # helper to write lightweight status JSON for UI progress updates
            def write_status(ws_path_local, status='Processing', progress=0, message=''):
                try:
                    s = {'status': status, 'progress': int(progress), 'message': str(message)}
                    with open(ws_path_local / 'status.json', 'w', encoding='utf-8') as sf:
                        json.dump(s, sf)
                    # also keep a simple status.txt (back-compat)
                    with open(ws_path_local / 'status.txt', 'w', encoding='utf-8') as tf:
                        tf.write(status.lower())
                except Exception:
                    pass

            # initial queued status
            write_status(ws_path, status='Processing', progress=2, message='Queued')

            # Run static analysis (non-iterative)
            # If compile_commands.json is missing in the uploaded repo, try to generate
            # one with CMake in a temporary build dir so clang-tidy can run.
            static_out = ''
            try:
                repo_root = Path(target)
                tidy_needed = True
                if (repo_root / 'compile_commands.json').exists():
                    tidy_needed = False
                cmake_path = shutil.which('cmake')
                temp_build = None
                copied_compile = False
                if tidy_needed and cmake_path:
                    try:
                        temp_build = ws_path / 'clang_tidy_build'
                        if temp_build.exists():
                            shutil.rmtree(temp_build)
                        temp_build.mkdir(parents=True, exist_ok=True)
                        # Run cmake configure to generate compile_commands.json
                        cfg_cmd = [cmake_path, '-S', str(repo_root), '-B', str(temp_build), '-DCMAKE_EXPORT_COMPILE_COMMANDS=ON']
                        proc = subprocess.run(cfg_cmd, cwd=str(AGENT_DIR), capture_output=True, text=True)
                        if proc.returncode == 0:
                            cc_src = temp_build / 'compile_commands.json'
                            if cc_src.exists():
                                try:
                                    shutil.copy2(cc_src, repo_root / 'compile_commands.json')
                                    copied_compile = True
                                except Exception:
                                    copied_compile = False
                    except Exception:
                        copied_compile = False

                # Run analyzer (will pick up compile_commands.json if present)
                static_out = run_command(f"py -3 -u analyzer_cpp.py --repo-dir \"{target}\"", cwd=AGENT_DIR)

                # clang-tidy disabled: we will not run clang-tidy for uploads.
                # Keep static_out from the analyzer (cppcheck + any analyzer-produced text).

                # cleanup: remove copied compile_commands.json and temp build dir
                try:
                    if copied_compile:
                        try:
                            (repo_root / 'compile_commands.json').unlink()
                        except Exception:
                            pass
                    if temp_build and temp_build.exists():
                        shutil.rmtree(temp_build, ignore_errors=True)
                except Exception:
                    pass
            except Exception:
                # fallback: run analyzer without compile_commands.json
                static_out = run_command(f"py -3 -u analyzer_cpp.py --repo-dir \"{target}\"", cwd=AGENT_DIR)
            # If analyzer produced structured JSON (with cppcheck/clang_tidy raw sections),
            # merge those raw texts into the static_out so the UI static panel shows clang-tidy too.
                try:
                    structured_root = AGENT_DIR / 'analysis_report_cpp.json'
                    if structured_root.exists():
                        try:
                            sdata = json.loads(structured_root.read_text(encoding='utf-8'))
                            merged = (static_out or '')
                            # append cppcheck raw only
                            cpp_raw = ''
                            try:
                                cpp_raw = sdata.get('cppcheck', {}).get('raw') or ''
                            except Exception:
                                cpp_raw = ''
                            if cpp_raw and cpp_raw.strip() and cpp_raw.strip() not in merged:
                                if merged:
                                    merged += '\n\n--- cppcheck (structured) ---\n'
                                merged += cpp_raw
                            if merged:
                                static_out = merged
                        except Exception:
                            pass
                except Exception:
                    pass

            # Ensure static analysis fields exist (robust fallback).
            try:
                # Try workspace-local structured JSON first, then agent-root JSON.
                # Only merge raw structured outputs into the local `static_out`
                # so we don't reference `result` before it's created later.
                structured = None
                try:
                    pws = ws_path / 'analysis_report_cpp.json'
                    if pws.exists():
                        structured = json.loads(pws.read_text(encoding='utf-8'))
                except Exception:
                    structured = None
                if structured is None:
                    try:
                        prot = AGENT_DIR / 'analysis_report_cpp.json'
                        if prot.exists():
                            structured = json.loads(prot.read_text(encoding='utf-8'))
                    except Exception:
                        structured = None

                # If structured data found, merge its raw cppcheck/clang-tidy
                # outputs into `static_out` so the UI shows them later.
                if structured:
                    merged = static_out or ''
                    try:
                        if structured.get('cppcheck', {}).get('raw'):
                            raw_cpp = structured['cppcheck'].get('raw') or ''
                            if raw_cpp.strip() and raw_cpp.strip() not in merged:
                                if merged:
                                    merged += '\n\n--- cppcheck (structured) ---\n'
                                merged += raw_cpp
                    except Exception:
                        pass
                    try:
                        if structured.get('clang_tidy', {}).get('raw'):
                            raw_tidy = structured['clang_tidy'].get('raw') or ''
                            if raw_tidy.strip() and raw_tidy.strip() not in merged:
                                if merged:
                                    merged += '\n\n--- clang-tidy (structured) ---\n'
                                merged += raw_tidy
                    except Exception:
                        pass
                    if merged:
                        static_out = merged
            except Exception:
                pass
            # For Experiment 2 we do not apply or archive agent patches; keep
            # the workspace focused on analysis only. Leave archived list empty.
            archived_list = []

            # Now run dynamic tests (write per-workspace outputs using --out-dir)
            # Ensure the background worker provides Qt/toolchain paths to the tester when available
            # Prefer explicit environment variables: QT_INCLUDES, QT_LIBS, MSYS2_PATH, QT_BIN_PATH
            qt_includes = os.environ.get('QT_INCLUDES')
            qt_libs = os.environ.get('QT_LIBS')
            msys2_path = os.environ.get('MSYS2_PATH')
            qt_bin = os.environ.get('QT_BIN_PATH')

            # If specific MSYS/Qt bin paths are present, prepend them to PATH for this process
            path_parts = []
            if msys2_path and Path(msys2_path).exists():
                path_parts.append(msys2_path)
            if qt_bin and Path(qt_bin).exists():
                path_parts.append(qt_bin)
            # Common defaults (only add if they exist). Prefer detected Qt 6.10.1 if present.
            if not path_parts:
                default_msys = Path(r'C:\msys64\mingw64\bin')
                default_qtbin = None
                for candidate in (
                    Path(r'C:\Qt\6.10.1\mingw_64\bin'),
                    Path(r'C:\Qt\6.9.2\mingw_64\bin'),
                ):
                    if candidate.exists():
                        default_qtbin = candidate
                        break
                if default_msys.exists():
                    path_parts.append(str(default_msys))
                if default_qtbin and default_qtbin.exists():
                    path_parts.append(str(default_qtbin))
                    # If QT_INCLUDES/LIBS not set, infer from detected Qt root
                    qt_root = default_qtbin.parent
                    qt_includes = qt_includes or str(qt_root / 'include')
                    qt_libs = qt_libs or str(qt_root / 'lib')
                    # Surface inferred Qt paths into environment so tester sees them
                    os.environ.setdefault('QT_BIN_PATH', str(default_qtbin))
                    os.environ.setdefault('QT_INCLUDES', qt_includes)
                    os.environ.setdefault('QT_LIBS', qt_libs)

            if path_parts:
                # Prepend to PATH for the background thread so subprocesses see qmake/g++
                os.environ['PATH'] = ';'.join(path_parts) + ';' + os.environ.get('PATH', '')

            # Avoid heavy sanitizers on server runs to reduce OOMs
            os.environ['DYNAMIC_TESTER_NO_SANITIZERS'] = '1'

            # Write a per-workspace environment debug file so we can inspect
            # what the Flask background worker sees when executing the tester.
            try:
                dbg = {
                    'PATH': os.environ.get('PATH', ''),
                    'QT_INCLUDES': os.environ.get('QT_INCLUDES'),
                    'QT_LIBS': os.environ.get('QT_LIBS'),
                    'MSYS2_PATH': os.environ.get('MSYS2_PATH'),
                    'QT_BIN_PATH': os.environ.get('QT_BIN_PATH'),
                    'CPP_QT_BEHAVIOR': os.environ.get('CPP_QT_BEHAVIOR'),
                    'DYNAMIC_TESTER_NO_SANITIZERS': os.environ.get('DYNAMIC_TESTER_NO_SANITIZERS'),
                }
                with open(ws_path / 'env_debug.json', 'w', encoding='utf-8') as ef:
                    json.dump(dbg, ef, indent=2)
            except Exception as _e:
                logger.warning('Failed to write env debug for workspace %s: %s', ws_id, _e)

            # Build explicit env for the subprocess so the tester sees the same
            # environment as a manual run. Use subprocess.run with shell=False
            # and a list of args to avoid quoting issues.
            env = os.environ.copy()
            # Ensure QT_INCLUDES / QT_LIBS are visible to the tester process
            if qt_includes:
                env['QT_INCLUDES'] = qt_includes
            if qt_libs:
                env['QT_LIBS'] = qt_libs
            if msys2_path:
                env['MSYS2_PATH'] = msys2_path
            if qt_bin:
                env['QT_BIN_PATH'] = qt_bin
            # If QT_BIN_PATH not set but path_parts contains a Qt bin, surface it
            if 'QT_BIN_PATH' not in env:
                for ppart in path_parts:
                    if 'Qt' in str(ppart) and 'bin' in str(ppart):
                        env['QT_BIN_PATH'] = str(ppart)
                        break

            # Prepend PATH parts so tools like qmake/mingw32-make/moc are found
            if path_parts:
                env['PATH'] = ';'.join(path_parts) + ';' + env.get('PATH', '')

            # Generate HF-powered suggested test cases (if HF configured)
            try:
                write_status(ws_path, status='Processing', progress=35, message='Generating test cases')
                gen_tests = generate_tests(str(ws_path), str(target))
                # attach to result later by writing file now; generate_tests writes generated_tests.json
                write_status(ws_path, status='Processing', progress=40, message='Test cases generated')
            except Exception as _e:
                logger.warning('HF test generator failed for %s: %s', ws_id, _e)
                write_status(ws_path, status='Processing', progress=40, message='Test generation skipped')

            # Generate DiagramScene functional tests (if applicable)
            try:
                from diagramscene_functional_tests import generate_diagramscene_tests
                write_status(ws_path, status='Processing', progress=42, message='Generating DiagramScene tests')
                diag_tests = generate_diagramscene_tests(exe_path=None, out_dir=Path(ws_path))
                if diag_tests:
                    # Save to generated_tests_diagramscene.json
                    import json
                    diag_json_path = Path(ws_path) / "generated_tests_diagramscene.json"
                    diag_json_path.write_text(json.dumps(diag_tests, indent=2), encoding='utf-8')
                    logger.info('Generated %d DiagramScene functional tests for %s', len(diag_tests), ws_id)
                write_status(ws_path, status='Processing', progress=45, message='DiagramScene tests ready')
            except ImportError:
                logger.debug('DiagramScene test generator not available')
            except Exception as _e:
                logger.warning('DiagramScene test generator failed for %s: %s', ws_id, _e)
                write_status(ws_path, status='Processing', progress=45, message='DiagramScene tests skipped')

            # Ensure an injected GoogleTest scaffold exists in the workspace so
            # white-box tests can run even if the project doesn't include them.
            try:
                from dynamic_tester import ensure_injected_googletest
                try:
                    ensure_injected_googletest(Path(target), out_dir=ws_path)
                except Exception:
                    pass
            except Exception:
                # dynamic_tester may not be importable in some environments
                pass

            # Also ensure a lightweight doctest scaffold is present so simple
            # white-box tests are available without pulling external deps.
            try:
                from dynamic_tester import ensure_injected_doctest
                try:
                    ensure_injected_doctest(Path(target), out_dir=ws_path)
                except Exception:
                    pass
            except Exception:
                pass

            # If DiagramScene functional tests were generated, create a small
            # stub executable and patch the project's CMakeLists so the stub
            # is built when Qt is not available. This ensures generated
            # DiagramScene tests can exercise a real binary.
            def _create_diagramscene_stub_if_needed(ws_path_local, target_root):
                try:
                    # detect presence of DiagramScene generated tests
                    diag_json = ws_path_local / 'generated_tests_diagramscene.json'
                    if not diag_json.exists():
                        return
                    # Find candidate project directories (CMakeLists mentioning Qt)
                    proj_candidates = []
                    for cm in Path(target_root).rglob('CMakeLists.txt'):
                        try:
                            txt = cm.read_text(encoding='utf-8', errors='ignore')
                            if 'Qt6' in txt or 'find_package(Qt6' in txt or 'diagramscene' in str(cm.parent).lower():
                                proj_candidates.append(cm.parent)
                        except Exception:
                            continue
                    if not proj_candidates:
                        return
                    proj = proj_candidates[0]
                    stub_cpp = proj / 'diagramscene_stub.cpp'
                    cmake_file = proj / 'CMakeLists.txt'
                    # write a simple stub
                    if not stub_cpp.exists():
                        stub_cpp.write_text('''#include <iostream>\n#include <string>\nint main(int argc, char** argv) {\n    std::cout << "diagramscene stub running\n";\n    for (int i=1;i<argc;i++) {\n        std::string a = argv[i];\n        if (a == "--nodes" && i+1<argc) { std::cout << "Nodes processed: " << argv[++i] << "\n"; }\n        else if (a == "--export" && i+1<argc) { std::cout << "Exported svg: " << argv[++i] << "\n"; }\n        else if (a == "--label" && i+1<argc) { std::cout << "Labeled: " << argv[++i] << "\n"; }\n    }\n    return 0;\n}\n''', encoding='utf-8')
                    # patch CMakeLists to add a fallback target if not already present
                    if cmake_file.exists():
                        cmtext = cmake_file.read_text(encoding='utf-8', errors='ignore')
                        if '## AGENT_STUB_ADDED' not in cmtext:
                            add_block = '\n# ## AGENT_STUB_ADDED - agent fallback target for diagramscene\nif(NOT TARGET diagramscene AND NOT TARGET diagramscene_stub)\n  add_executable(diagramscene_stub diagramscene_stub.cpp)\n  set_target_properties(diagramscene_stub PROPERTIES OUTPUT_NAME "diagramscene")\nendif()\n'
                            try:
                                with open(cmake_file, 'a', encoding='utf-8') as cf:
                                    cf.write(add_block)
                            except Exception:
                                pass
                except Exception:
                    pass

            try:
                _create_diagramscene_stub_if_needed(ws_path, target)
            except Exception:
                pass

            # Build argument list mirroring manual invocation
            args = [
                'py', '-3', '-u', 'dynamic_tester.py',
                '--cpp',
                '--cpp-repo', str(target),
                '--out-dir', str(ws_path),
            ]
            if qt_includes:
                args += ['--qt-includes', qt_includes]
            if qt_libs:
                args += ['--qt-libs', qt_libs]
            # If we inferred Qt from defaults, ensure env also sees these
            if qt_includes and 'QT_INCLUDES' not in env:
                env['QT_INCLUDES'] = qt_includes
            if qt_libs and 'QT_LIBS' not in env:
                env['QT_LIBS'] = qt_libs

            try:
                proc = subprocess.run(args, cwd=str(AGENT_DIR), env=env, capture_output=True, text=True)
                dyn_out = (proc.stdout or '') + (proc.stderr or '')
            except Exception as _e:
                dyn_out = f"[Error] failed to launch dynamic tester: {_e}"

            # Copy static analysis report into workspace so each workspace is self-contained.
            static_report_src = AGENT_DIR / 'analysis_report_cpp.txt'
            static_report_dst = ws_path / 'analysis_report_cpp.txt'
            try:
                if static_report_src.exists():
                    shutil.copy2(static_report_src, static_report_dst)
                else:
                    # If we merged structured output into static_out, write it into workspace file
                    try:
                        if static_out:
                            (ws_path / 'analysis_report_cpp.txt').write_text(static_out, encoding='utf-8')
                    except Exception:
                        pass
                # Also copy structured JSON into workspace when available so UI can load it locally
                structured_root = AGENT_DIR / 'analysis_report_cpp.json'
                if structured_root.exists():
                    try:
                        shutil.copy2(structured_root, ws_path / 'analysis_report_cpp.json')
                    except Exception:
                        pass
            except Exception as _e:
                logger.warning("Failed to copy static report to workspace %s: %s", ws_id, _e)

            # Usability and documentation checks (automated heuristics)
            try:
                usability = run_usability_checks(target)
            except Exception as _e:
                usability = {'error': str(_e)}
            try:
                documentation = run_documentation_checks(target)
            except Exception as _e:
                documentation = {'error': str(_e)}

            # Clean dynamic output for UI (remove verbose patch summary lines)
            dyn_clean_lines = [ln for ln in (dyn_out or "").splitlines() if not ln.strip().startswith("Patches applied:")]
            dyn_clean = "\n".join(dyn_clean_lines)

            # If dynamic tester produced a structured JSON report, include it.
            dyn_json = None
            dyn_json_path = ws_path / 'dynamic_analysis_report.json'
            try:
                if dyn_json_path.exists():
                    with open(dyn_json_path, 'r', encoding='utf-8') as dj:
                        dyn_json = json.load(dj)
            except Exception:
                dyn_json = None

            # Build enriched result.json with metadata and machine-readable dynamic report
            result = {
                "workspace": ws_id,
                "run_id": ws_id,
                "timestamp": datetime.utcnow().isoformat() + 'Z',
                "language": lang,
                "agent_root": str(AGENT_DIR),
                "static_summary": {
                    "raw": static_out,
                    "length": len(static_out) if static_out else 0,
                },
                "dynamic_raw": dyn_out,
                "dynamic_text": dyn_clean,
                "dynamic_structured": dyn_json,
                "usability_checks": usability,
                "documentation_checks": documentation,
                "suggested_patches": [],
                "archived_agent_patches": archived_list,
            }
            # Ensure structured static analysis (cppcheck/clang-tidy) is attached
            try:
                # prefer workspace-local JSON, fall back to agent root
                sp_ws = ws_path / 'analysis_report_cpp.json'
                sp_root = AGENT_DIR / 'analysis_report_cpp.json'
                structured = None
                if sp_ws.exists():
                    try:
                        structured = json.loads(sp_ws.read_text(encoding='utf-8'))
                    except Exception:
                        structured = None
                elif sp_root.exists():
                    try:
                        structured = json.loads(sp_root.read_text(encoding='utf-8'))
                    except Exception:
                        structured = None

                if structured:
                    result['static_structured'] = structured
                    try:
                        cpp_cnt = int(structured.get('cppcheck', {}).get('issue_count', 0) or 0)
                    except Exception:
                        cpp_cnt = 0
                    try:
                        tidy_cnt = int(structured.get('clang_tidy', {}).get('issue_count', 0) or 0)
                    except Exception:
                        tidy_cnt = 0
                    total_cnt = cpp_cnt + tidy_cnt
                    result['static_count'] = total_cnt
                    # merge raw text pieces into static_full for UI convenience
                    try:
                        merged = result.get('static_full', '') or result.get('static', '') or ''
                        if structured.get('cppcheck', {}).get('raw'):
                            rc = structured['cppcheck'].get('raw') or ''
                            if rc.strip() and rc.strip() not in merged:
                                if merged:
                                    merged += "\n\n--- cppcheck (structured) ---\n"
                                merged += rc
                        if structured.get('clang_tidy', {}).get('raw'):
                            rt = structured['clang_tidy'].get('raw') or ''
                            if rt.strip() and rt.strip() not in merged:
                                if merged:
                                    merged += "\n\n--- clang-tidy (structured) ---\n"
                                merged += rt
                        if merged:
                            result['static_full'] = merged
                            result['static'] = merged
                    except Exception:
                        pass
                else:
                    # ensure keys exist even when no structured JSON is available
                    result.setdefault('static_structured', None)
                    result.setdefault('static_count', 0)
            except Exception:
                result.setdefault('static_structured', None)
                result.setdefault('static_count', 0)
            # Attach generated HF tests if present and normalize entries for the UI
            try:
                gen_path = ws_path / 'generated_tests.json'
                if gen_path.exists():
                    try:
                        gt = json.loads(gen_path.read_text(encoding='utf-8'))
                    except Exception:
                        gt = None
                    if isinstance(gt, list):
                        norm = []
                        for entry in gt:
                            try:
                                e = dict(entry) if isinstance(entry, dict) else {'name': str(entry)}
                                # ensure common fields exist
                                e['name'] = e.get('name') or e.get('title') or e.get('test') or ''
                                e['title'] = e.get('title') or e.get('name')
                                # normalize commands to a list of strings
                                cmds = e.get('commands') or e.get('command') or []
                                if isinstance(cmds, str):
                                    cmds = [cmds]
                                # ensure each command is a string
                                cmds2 = []
                                for c in cmds:
                                    try:
                                        cmds2.append(str(c))
                                    except Exception:
                                        cmds2.append('')
                                e['commands'] = cmds2
                                # preserve detail/status; default to UNKNOWN
                                st = str(e.get('status') or e.get('result') or '').upper()
                                if st not in ('PASS', 'FAIL', 'SKIPPED'):
                                    e['status'] = e.get('status') or 'UNKNOWN'
                                else:
                                    e['status'] = st
                                # mark skipped if dynamic_tester flagged it
                                if e.get('_skip_compiler_helper') or str(e.get('status')).upper() == 'SKIPPED':
                                    e['skipped'] = True
                                else:
                                    e['skipped'] = False
                                norm.append(e)
                            except Exception:
                                continue
                        result['generated_tests'] = norm
                        result['generated_tests_path'] = str(gen_path)
                    else:
                        result['generated_tests'] = gt
                        result['generated_tests_path'] = str(gen_path)
                else:
                    result['generated_tests'] = None
                    result['generated_tests_path'] = None
            except Exception:
                result['generated_tests'] = None
                result['generated_tests_path'] = None
            # If the tester produced a ui-friendly summary, surface it at top-level
            try:
                if dyn_json and isinstance(dyn_json, dict):
                    ui = dyn_json.get('ui_summary')
                    if ui:
                        result['ui_summary'] = ui.get('ui_text') if isinstance(ui.get('ui_text'), str) else ''
                        result['ui_html'] = ui.get('ui_html') if isinstance(ui.get('ui_html'), str) else ''
                        # Also write a small HTML file into the workspace for quick viewing
                        try:
                            if result['ui_html']:
                                (ws_path / 'ui_report.html').write_text('<html><body>' + result['ui_html'] + '</body></html>', encoding='utf-8')
                        except Exception:
                            pass
            except Exception:
                pass
            # Backwards compatibility for the UI template which expects `static` and `dynamic` keys
            # Keep these in sync with the newer structured fields.
            try:
                result['static'] = result['static_summary']['raw'] if 'static_summary' in result else (static_out or '')
            except Exception:
                result['static'] = static_out or ''
            try:
                result['dynamic'] = result.get('dynamic_text') or (dyn_out or '')
            except Exception:
                result['dynamic'] = dyn_out or ''

            # --- UI left-bottom concise summary ---
            # Build a compact, human-friendly summary for the UI (left-bottom)
            ui_left = {'static': '', 'dynamic': ''}
            try:
                # Static: prefer workspace-local static report if present
                static_txt = ''
                if (ws_path / 'analysis_report_cpp.txt').exists():
                    static_txt = (ws_path / 'analysis_report_cpp.txt').read_text(encoding='utf-8', errors='ignore')
                elif static_out:
                    static_txt = static_out
                # Extract key summary: look for 'Found N' pattern or 'error-level' mention
                static_count = None
                top_issues = []
                if static_txt:
                    m = re.search(r'Found\s+(\d+)\s+C/C\+\+\s+error-level', static_txt)
                    if not m:
                        m = re.search(r'Found\s+(\d+)\s+error', static_txt, re.IGNORECASE)
                    if m:
                        static_count = int(m.group(1))
                    # grab first few lines that look like issues (contain 'error' or 'warning')
                    for ln in static_txt.splitlines():
                        if len(top_issues) >= 3:
                            break
                        if 'error' in ln.lower() or 'fatal' in ln.lower() or 'warning' in ln.lower():
                            clean = ln.strip()
                            if clean and clean not in top_issues:
                                top_issues.append(clean)
                if static_count is not None:
                    ui_left['static'] = f"Static: {static_count} C/C++ error-level issues"
                else:
                    # fallback: provide short summary with bytes/lines
                    if static_txt:
                        ui_left['static'] = f"Static: {min(len(static_txt.splitlines()), 5)} lines of findings"
                    else:
                        ui_left['static'] = 'Static: no report'
                if top_issues:
                    ui_left['static_details'] = top_issues
            except Exception:
                ui_left['static'] = 'Static: N/A'

            # Expose the full static analysis text into the result so the UI
            # can show details inline without requiring the user to click
            # "View full static analysis file". Prefer workspace-local file
            # if present, otherwise use the captured `static_out`.
            try:
                full_static = ''
                try:
                    if (ws_path / 'analysis_report_cpp.txt').exists():
                        full_static = (ws_path / 'analysis_report_cpp.txt').read_text(encoding='utf-8', errors='ignore')
                    else:
                        full_static = static_out or ''
                except Exception:
                    full_static = static_out or ''
                result['static_full'] = full_static
                # include structured static JSON if analyzer produced it
                structured_path_ws = ws_path / 'analysis_report_cpp.json'
                structured_path_root = AGENT_DIR / 'analysis_report_cpp.json'
                structured = None
                if structured_path_ws.exists():
                    try:
                        structured = json.loads(structured_path_ws.read_text(encoding='utf-8'))
                    except Exception:
                        structured = None
                elif structured_path_root.exists():
                    try:
                        structured = json.loads(structured_path_root.read_text(encoding='utf-8'))
                    except Exception:
                        structured = None
                if structured:
                    # attach structured data and compute counts
                    result['static_structured'] = structured
                    try:
                        c = structured.get('cppcheck', {})
                        t = structured.get('clang_tidy', {})
                        cpp_cnt = int(c.get('issue_count', 0)) if isinstance(c, dict) else 0
                        tidy_cnt = int(t.get('issue_count', 0)) if isinstance(t, dict) else 0
                        total_cnt = cpp_cnt + tidy_cnt
                        result['static_count'] = total_cnt
                        # build a readable ui_left summary
                        if total_cnt > 0:
                            result['ui_left']['static'] = f"Static: {total_cnt} issues (cppcheck: {cpp_cnt}, clang-tidy: {tidy_cnt})"
                        else:
                            result['ui_left']['static'] = result.get('ui_left', {}).get('static', '')
                    except Exception:
                        result['static_count'] = 0

                    # merge structured raw outputs into the full static text so UI shows clang-tidy too
                    merged = full_static or ''
                    try:
                        if structured.get('cppcheck') and structured['cppcheck'].get('raw'):
                            raw_cpp = structured['cppcheck'].get('raw') or ''
                            if raw_cpp.strip() and raw_cpp.strip() not in merged:
                                if merged:
                                    merged += "\n\n--- cppcheck (structured) ---\n"
                                merged += raw_cpp
                    except Exception:
                        pass
                    try:
                        if structured.get('clang_tidy') and structured['clang_tidy'].get('raw'):
                            raw_tidy = structured['clang_tidy'].get('raw') or ''
                            if raw_tidy.strip() and raw_tidy.strip() not in merged:
                                if merged:
                                    merged += "\n\n--- clang-tidy (structured) ---\n"
                                merged += raw_tidy
                    except Exception:
                        pass

                    if merged:
                        result['static_full'] = merged
                        result['static'] = merged
                        try:
                            top_issues = []
                            for ln in (merged or '').splitlines():
                                if len(top_issues) >= 3:
                                    break
                                if 'error' in ln.lower() or 'warning' in ln.lower() or 'fatal' in ln.lower():
                                    clean = ln.strip()
                                    if clean and clean not in top_issues:
                                        top_issues.append(clean)
                            if top_issues:
                                result['ui_left']['static_details'] = top_issues
                        except Exception:
                            pass

                    # If we didn't get a numeric count from structured JSON, estimate from merged text
                    try:
                        if 'static_count' not in result or result.get('static_count') is None:
                            merged_text = merged or ''
                            est = sum(1 for ln in merged_text.splitlines() if re.search(r'error|warning|fatal', ln, flags=re.IGNORECASE))
                            result['static_count'] = est
                            if not result['ui_left'].get('static'):
                                result['ui_left']['static'] = f"Static: {est} findings"
                    except Exception:
                        pass
                # Overwrite the legacy `static` field with the full text so
                # the UI static panel displays details directly.
                result['static'] = full_static
                # Robust fallback: if no structured JSON was found by the
                # earlier logic, synthesize a minimal `static_structured`
                # from the collected `full_static` text so the UI can show
                # counts and raw text for new uploads even when the
                # analyzer didn't write a JSON file.
                try:
                    sp_ws2 = ws_path / 'analysis_report_cpp.json'
                    sp_root2 = AGENT_DIR / 'analysis_report_cpp.json'
                    found_struct = None
                    if sp_ws2.exists():
                        try:
                            found_struct = json.loads(sp_ws2.read_text(encoding='utf-8'))
                        except Exception:
                            found_struct = None
                    elif sp_root2.exists():
                        try:
                            found_struct = json.loads(sp_root2.read_text(encoding='utf-8'))
                        except Exception:
                            found_struct = None
                    if not found_struct and full_static:
                        est_cnt = sum(1 for ln in (full_static or '').splitlines() if re.search(r'error|warning|fatal', ln, flags=re.IGNORECASE))
                        synth = {
                            'cppcheck': {'raw': full_static or '', 'issue_count': est_cnt},
                            'clang_tidy': {'raw': '', 'issue_count': 0}
                        }
                        result['static_structured'] = synth
                        result['static_count'] = est_cnt
                        # merge synthesized raw into static_full/static if not present
                        merged2 = result.get('static_full', '') or result.get('static', '') or ''
                        if (full_static or '').strip() and full_static.strip() not in merged2:
                            if merged2:
                                merged2 += '\n\n--- cppcheck (synth) ---\n'
                            merged2 += full_static
                        if merged2:
                            result['static_full'] = merged2
                            result['static'] = merged2
                        # update ui_left summary
                        try:
                            result['ui_left']['static'] = f"Static: {est_cnt} findings"
                        except Exception:
                            pass
                except Exception:
                    pass
                # If we have a generated static analysis test, attach the
                # full output into its detail field so UI test table shows it.
                if result.get('generated_tests') and isinstance(result['generated_tests'], list):
                    for t in result['generated_tests']:
                        try:
                            nm = (t.get('name') or t.get('title') or '').lower()
                            if 'static:analyzer' in nm or 'static analysis' in nm or (t.get('title') and 'static' in t.get('title').lower()):
                                t['detail'] = full_static
                                # mark FAIL if analyzer found errors
                                if full_static and ('Exiting with code' in full_static or 'error-level' in full_static.lower() or 'error' in full_static.lower()):
                                    t['status'] = 'FAIL'
                        except Exception:
                            continue
            except Exception:
                pass

            try:
                # Dynamic: prefer structured JSON tests if available
                dyn_summary = ''
                dyn_rows = []
                if dyn_json and isinstance(dyn_json, dict):
                    tests = dyn_json.get('tests', [])
                    pass_c = sum(1 for t in tests if str(t.get('status','')).upper() == 'PASS')
                    fail_c = sum(1 for t in tests if str(t.get('status','')).upper() == 'FAIL')
                    skip_c = sum(1 for t in tests if str(t.get('status','')).upper() == 'SKIPPED')
                    dyn_summary = f"Dynamic: {pass_c} PASS, {fail_c} FAIL, {skip_c} SKIPPED"
                    # list failing test names (up to 5)
                    fails = [t.get('test') for t in tests if str(t.get('status','')).upper() == 'FAIL']
                    if fails:
                        ui_left['dynamic_failures'] = fails[:5]
                else:
                    # fallback: parse cleaned dynamic text lines that start with [+]/[-]/[!]
                    lines = (dyn_clean or '').splitlines()
                    pass_c = sum(1 for l in lines if l.strip().startswith('[+]'))
                    fail_c = sum(1 for l in lines if l.strip().startswith('[-]'))
                    skip_c = sum(1 for l in lines if l.strip().startswith('[!]'))
                    dyn_summary = f"Dynamic: {pass_c} PASS, {fail_c} FAIL, {skip_c} SKIPPED"
                ui_left['dynamic'] = dyn_summary
            except Exception:
                ui_left['dynamic'] = 'Dynamic: N/A'

            result['ui_left'] = ui_left

            # --- White-box & Black-box concise summaries ---
            try:
                white_box = {
                    'summary': ui_left.get('static') if isinstance(ui_left, dict) else (static_out or 'Static: N/A'),
                    'details': ui_left.get('static_details', []) if isinstance(ui_left, dict) else [],
                    'usability': {}
                }
                if isinstance(usability, dict):
                    white_box['usability'] = {
                        'readme_exists': bool(usability.get('readme_exists')),
                        'readme_length': int(usability.get('readme_length', 0)) if usability.get('readme_length') is not None else 0,
                        'suggestions': (usability.get('suggestions') or [])[:3]
                    }
                else:
                    white_box['usability'] = {}

                black_box = {
                    'summary': ui_left.get('dynamic') if isinstance(ui_left, dict) else (dyn_out or 'Dynamic: N/A'),
                    'failures': ui_left.get('dynamic_failures', []) if isinstance(ui_left, dict) else [],
                    'generated_tests_count': 0
                }
                if result.get('generated_tests'):
                    try:
                        if isinstance(result['generated_tests'], list):
                            black_box['generated_tests_count'] = len(result['generated_tests'])
                        elif isinstance(result['generated_tests'], dict):
                            black_box['generated_tests_count'] = len(result['generated_tests'].get('tests', []))
                    except Exception:
                        black_box['generated_tests_count'] = 0

                result['white_box'] = white_box
                result['black_box'] = black_box
            except Exception:
                result['white_box'] = {'summary': 'N/A', 'details': []}
                result['black_box'] = {'summary': 'N/A', 'failures': []}

            # Merge unit tests from the dynamic structured report into top-level result
            try:
                if dyn_json and isinstance(dyn_json, dict):
                    dyn_tests = dyn_json.get('tests')
                    if isinstance(dyn_tests, list) and dyn_tests:
                        # place under `unit_tests` for UI compatibility
                        result['unit_tests'] = dyn_tests
                    # preserve list of source files merged (if present)
                    if 'merged_test_results_files' in dyn_json:
                        result['merged_test_results_files'] = dyn_json.get('merged_test_results_files')
            except Exception:
                pass

            with open(ws_path / 'result.json', 'w', encoding='utf-8') as fh:
                json.dump(result, fh, ensure_ascii=False, indent=2)
            # Create a submission package (zip) inside the workspace
            try:
                pkg = create_submission_package(ws_id)
                if pkg:
                    result['submission_package'] = pkg
                    with open(ws_path / 'result.json', 'w', encoding='utf-8') as fh:
                        json.dump(result, fh, ensure_ascii=False, indent=2)
            except Exception as _e:
                logger.warning("Failed to create submission package: %s", _e)
            # finalize
            write_status(ws_path, status='Done', progress=100, message='Complete')

            logger.info("[BG] Finished processing workspace %s", ws_id)
        except Exception as e:
            logger.exception("[BG] Error processing workspace %s: %s", ws_id, e)
            try:
                ws_path = AGENT_DIR / 'workspaces' / ws_id
                with open(ws_path / 'result.json', 'w', encoding='utf-8') as fh:
                    json.dump({"error": str(e)}, fh)
                # write error status.json and status.txt
                try:
                    with open(ws_path / 'status.json', 'w', encoding='utf-8') as sf:
                        json.dump({'status': 'Error', 'progress': 100, 'message': str(e)}, sf)
                except Exception:
                    pass
                with open(ws_path / 'status.txt', 'w', encoding='utf-8') as fh:
                    fh.write('error')
            except Exception:
                pass

    t = threading.Thread(target=bg, daemon=True)
    t.start()

    logger.info("/upload accepted: workspace=%s", ws_id)
    return jsonify({"status": "Accepted", "workspace": ws_id})


def create_submission_package(ws_id: str, team_name: str = None):
    """Collect workspace artifacts and suggested patches into a zip for submission."""
    ws_path = AGENT_DIR / 'workspaces' / ws_id
    if not ws_path.exists():
        return None

    if not team_name:
        team_name = ws_id

    pkg_name = f"project_submission_{team_name}_{ws_id}.zip"
    pkg_path = ws_path / pkg_name

    with zipfile.ZipFile(pkg_path, 'w', compression=zipfile.ZIP_DEFLATED) as zf:
        # include workspace result and suggested patches
        if (ws_path / 'result.json').exists():
            zf.write(ws_path / 'result.json', arcname='result.json')

        suggested_dir = ws_path / 'suggested_patches'
        if suggested_dir.exists():
            for p in suggested_dir.rglob('*'):
                if p.is_file():
                    zf.write(p, arcname=str(Path('suggested_patches') / p.name))

        # include global agent reports if present
        # Prefer workspace-local reports; fall back to agent root if not present
        for fname in ('dynamic_analysis_report.txt', 'dynamic_analysis_report_raw.txt', 'dynamic_analysis_report.json'):
            fpath_ws = ws_path / fname
            if fpath_ws.exists():
                zf.write(fpath_ws, arcname=fname)
            else:
                fpath = AGENT_DIR / fname
                if fpath.exists():
                    zf.write(fpath, arcname=fname)
        # include static analysis report preferring workspace-local copy
        f_static_ws = ws_path / 'analysis_report_cpp.txt'
        if f_static_ws.exists():
            zf.write(f_static_ws, arcname='analysis_report_cpp.txt')
        else:
            f_static = AGENT_DIR / 'analysis_report_cpp.txt'
            if f_static.exists():
                zf.write(f_static, arcname='analysis_report_cpp.txt')

        # include any workspace logs
        for p in (ws_path / 'logs').glob('**/*') if (ws_path / 'logs').exists() else []:
            if p.is_file():
                zf.write(p, arcname=str(Path('logs') / p.name))

    return str(pkg_path)


@app.route('/status', methods=['GET'])
def status_route():
    ws = request.args.get('ws')
    if not ws:
        return jsonify({"status": "Error", "error": "Missing workspace id (ws)"}), 400
    ws_path = AGENT_DIR / 'workspaces' / ws
    if not ws_path.exists():
        return jsonify({"status": "Error", "error": "Workspace not found"}), 404
    status_json = ws_path / 'status.json'
    status_file = ws_path / 'status.txt'
    result_file = ws_path / 'result.json'
    # Prefer status.json (rich) if present
    if status_json.exists():
        try:
            data = json.loads(status_json.read_text(encoding='utf-8'))
            # If done, include result when available
            if str(data.get('status', '')).lower() in ('done', 'complete') and result_file.exists():
                res = json.loads(result_file.read_text(encoding='utf-8'))
                return jsonify({**data, 'result': res})
            return jsonify(data)
        except Exception:
            pass
    # Fallback to legacy status.txt behaviour
    if status_file.exists():
        st = status_file.read_text(encoding='utf-8')
        if st.strip() == 'done' and result_file.exists():
            data = json.loads(result_file.read_text(encoding='utf-8'))
            return jsonify({"status": "Done", "result": data})
        else:
            return jsonify({"status": st.strip()})
    else:
        return jsonify({"status": "Processing", "progress": 5, "message": "Queued"})


# === Command Interpreter ===

def interpret_command(user_input: str):
    """Interpret user command and execute corresponding function."""
    user_input_lower = user_input.strip().lower()

    try:
        # Conversation responses
        if "hello" in user_input_lower or "hi" in user_input_lower:
            return "Hello! 👋 Ready to analyze your code."
        elif "how are you" in user_input_lower:
            return "I'm great! Let's fix some code today 😄"
        elif "bye" in user_input_lower:
            return "Goodbye! 👋"

        # Require upload first
        if not file_uploaded:
            return "⚠️ Please upload a file before running commands."

        # Command matching
        # Command matching (C/C++ only)
        if "static" in user_input_lower and "cpp" in user_input_lower:
            return run_static_analysis_cpp()
        elif "dynamic" in user_input_lower and "cpp" in user_input_lower:
            return run_dynamic_cpp()
        elif "patch" in user_input_lower and "cpp" in user_input_lower:
            return run_patch_cpp()
        elif "auto_fix" in user_input_lower and "cpp" in user_input_lower:
            return run_iterative_fix_cpp(max_iters=5)
        elif "compare" in user_input_lower and "patch" in user_input_lower:
            return compare_patch()
        else:
            return "❓ Unknown command. Try: static cpp | dynamic cpp | patch cpp | auto_fix cpp | compare patch"
    except Exception as e:
        return f"[Error] {str(e)}"


# === Flask Routes ===

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/process', methods=['POST'])
def process_command():
    """Handle text commands."""
    user_input = request.form.get('command')
    if not user_input:
        return jsonify({"status": "Error", "error": "No command entered."})

    result = interpret_command(user_input)

    if "patch cpp" in user_input.lower():
        # Ensure the file has been uploaded first
        if not file_uploaded:
            return jsonify({"status": "Error", "error": "No file uploaded."})

        patch_result = run_patch_cpp()
        return jsonify({"status": "Success", "result": patch_result})

    # If it's an auto-fix command
    if "auto_fix cpp" in user_input.lower():
        # Run the auto-fix process and show progress
        auto_fix_result = run_iterative_fix_cpp(max_iters=5)
        return jsonify({"status": "Success", "result": auto_fix_result})

    return jsonify({"status": "Success", "result": result})


@app.route('/compare_patch', methods=['POST'])
def compare_patch():
    """Compare original file and patched file for C/C++ upload."""
    if not file_uploaded:
        return jsonify({"status": "Error", "error": "No file uploaded for patch comparison."})

    if not uploaded_cpp_files:
        return jsonify({"status": "Error", "error": "No uploaded C/C++ files available for comparison."})

    original_file = Path(uploaded_cpp_files[0])
    patched_file = original_file.with_name(original_file.stem + "_patched" + original_file.suffix)

    if not patched_file.exists():
        return jsonify({"status": "Error", "error": "Patched file not found."})

    # Get the diff between the original and patched files
    diff = compare_files(str(original_file), str(patched_file))
    
    return jsonify({"status": "Success", "diff": diff})


# === Config ===

app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['STATIC_FOLDER'] = 'static'
app.config['TEMPLATES_FOLDER'] = 'templates'


if __name__ == '__main__':
    # Disable the reloader to avoid the Flask dev server restarting when
    # uploaded files are copied into the project folder (which triggers
    # the watchdog and causes the request to be interrupted).
    # Keeping debug=True preserves helpful tracebacks; use_reloader=False
    # prevents automatic process restarts when files change.
    app.run(debug=True, host='0.0.0.0', port=5000, use_reloader=False, threaded=True)
