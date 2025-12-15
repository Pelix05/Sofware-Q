import json
from pathlib import Path
import sys

AGENT_DIR = Path(__file__).resolve().parent

def fix(ws_id):
    ws_path = AGENT_DIR / 'workspaces' / ws_id
    if not ws_path.exists():
        print('Workspace not found:', ws_id)
        return 1
    result_file = ws_path / 'result.json'
    if not result_file.exists():
        print('result.json missing for', ws_id)
        return 1
    data = json.loads(result_file.read_text(encoding='utf-8'))
    sp_ws = ws_path / 'analysis_report_cpp.json'
    sp_root = AGENT_DIR / 'analysis_report_cpp.json'
    structured = None
    if sp_ws.exists():
        try:
            structured = json.loads(sp_ws.read_text(encoding='utf-8'))
        except Exception as e:
            print('Failed to load workspace structured JSON:', e)
    elif sp_root.exists():
        try:
            structured = json.loads(sp_root.read_text(encoding='utf-8'))
        except Exception as e:
            print('Failed to load root structured JSON:', e)
    if structured:
        data['static_structured'] = structured
        cpp_cnt = 0
        tidy_cnt = 0
        try:
            cpp_cnt = int(structured.get('cppcheck', {}).get('issue_count', 0) or 0)
        except Exception:
            cpp_cnt = 0
        try:
            tidy_cnt = int(structured.get('clang_tidy', {}).get('issue_count', 0) or 0)
        except Exception:
            tidy_cnt = 0
        data['static_count'] = cpp_cnt + tidy_cnt
        merged = data.get('static_full') or data.get('static') or ''
        try:
            if structured.get('cppcheck', {}).get('raw'):
                rc = structured['cppcheck'].get('raw') or ''
                if rc.strip() and rc.strip() not in merged:
                    if merged:
                        merged += '\n\n--- cppcheck (structured) ---\n'
                    merged += rc
            if structured.get('clang_tidy', {}).get('raw'):
                rt = structured['clang_tidy'].get('raw') or ''
                if rt.strip() and rt.strip() not in merged:
                    if merged:
                        merged += '\n\n--- clang-tidy (structured) ---\n'
                    merged += rt
            if merged:
                data['static_full'] = merged
                data['static'] = merged
        except Exception:
            pass
    else:
        data.setdefault('static_structured', None)
        data.setdefault('static_count', 0)
    result_file.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
    print('Updated', result_file)
    return 0

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Usage: python fix_result_static.py <workspace_id>')
        sys.exit(1)
    ws = sys.argv[1]
    sys.exit(fix(ws))
