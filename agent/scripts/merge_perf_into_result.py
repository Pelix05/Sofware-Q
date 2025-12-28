import json
from pathlib import Path

ws = Path(r"d:\semester5\quality\ai-agent-project\agent\workspaces\diagramscene_ultima_20251229_024733")
perf_path = ws / "cpp_project" / "perf_report.json"
result_path = ws / "result.json"

if not perf_path.exists():
    print('perf file missing:', perf_path)
    raise SystemExit(1)
if not result_path.exists():
    print('result.json missing:', result_path)
    raise SystemExit(1)

with open(perf_path, 'r', encoding='utf-8') as f:
    perf = json.load(f)

with open(result_path, 'r', encoding='utf-8') as f:
    result = json.load(f)

result['perf'] = perf

with open(result_path, 'w', encoding='utf-8') as f:
    json.dump(result, f, indent=2)

print('[+] merged perf into', result_path)
