import json
import sys
from pathlib import Path
import datetime

def main(ws_path):
    ws = Path(ws_path)
    if not ws.exists():
        print('workspace not found', ws)
        return 2
    dyn = ws / 'dynamic_analysis_report.json'
    static = ws / 'analysis_report_cpp.txt'
    out = {}
    out['workspace'] = ws.name
    out['run_id'] = ws.name
    out['timestamp'] = datetime.datetime.utcnow().isoformat() + 'Z'
    out['language'] = 'cpp'
    if dyn.exists():
        try:
            d = json.loads(dyn.read_text(encoding='utf-8'))
            out['dynamic_structured'] = d
            out['unit_tests'] = d.get('tests', [])
            out['dynamic_raw'] = (ws / 'dynamic_analysis_report_raw.txt').read_text(encoding='utf-8') if (ws / 'dynamic_analysis_report_raw.txt').exists() else ''
            out['dynamic_text'] = (ws / 'dynamic_analysis_report.txt').read_text(encoding='utf-8') if (ws / 'dynamic_analysis_report.txt').exists() else ''
        except Exception as e:
            out['dynamic_text'] = f'Failed to load dynamic report: {e}'
    else:
        out['dynamic_text'] = ''
    if static.exists():
        out['static_full'] = static.read_text(encoding='utf-8', errors='ignore')
        out['static'] = out['static_full']
    else:
        out['static_full'] = ''
        out['static'] = ''

    # preserve generated_tests if present
    gen = ws / 'generated_tests.json'
    if gen.exists():
        try:
            out['generated_tests'] = json.loads(gen.read_text(encoding='utf-8'))
        except Exception:
            out['generated_tests'] = None

    # write result.json
    rpath = ws / 'result.json'
    rpath.write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding='utf-8')
    print('wrote', rpath)
    return 0

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('usage: generate_result_json.py <workspace_path>')
        sys.exit(2)
    sys.exit(main(sys.argv[1]))
