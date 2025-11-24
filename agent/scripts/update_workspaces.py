import json
from pathlib import Path

WS_ROOT = Path(__file__).resolve().parent.parent / 'workspaces'

for ws in sorted(WS_ROOT.iterdir()):
    if not ws.is_dir():
        continue
    resf = ws / 'result.json'
    if not resf.exists():
        print('no result.json for', ws.name)
        continue
    try:
        res = json.loads(resf.read_text(encoding='utf-8'))
    except Exception as e:
        print('failed to read', resf, e)
        continue
    changed = False
    dyn_json_f = ws / 'dynamic_analysis_report.json'
    dyn_txt_f = ws / 'dynamic_analysis_report.txt'
    if dyn_json_f.exists():
        try:
            dyn_json = json.loads(dyn_json_f.read_text(encoding='utf-8'))
            if res.get('dynamic_structured') != dyn_json:
                res['dynamic_structured'] = dyn_json
                changed = True
        except Exception as e:
            print('failed to load json', dyn_json_f, e)
    if dyn_txt_f.exists():
        try:
            txt = dyn_txt_f.read_text(encoding='utf-8')
            if res.get('dynamic_text') != txt:
                res['dynamic_text'] = txt
                changed = True
        except Exception as e:
            print('failed to load txt', dyn_txt_f, e)
    # ensure compatibility keys
    if 'static' not in res and 'static_summary' in res:
        res['static'] = res['static_summary'].get('raw','')
        changed = True
    if 'dynamic' not in res:
        res['dynamic'] = res.get('dynamic_text','')
        changed = True
    if changed:
        try:
            resf.write_text(json.dumps(res, ensure_ascii=False, indent=2), encoding='utf-8')
            print('updated', resf)
        except Exception as e:
            print('failed to write', resf, e)
    else:
        print('no changes for', resf)
