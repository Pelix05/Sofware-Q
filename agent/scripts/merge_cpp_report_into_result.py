#!/usr/bin/env python3
import sys
import os
import json

def merge(workspace_dir: str):
    workspace_dir = os.path.abspath(workspace_dir)
    result_path = os.path.join(workspace_dir, 'result.json')
    report_path = os.path.join(workspace_dir, 'analysis_report_cpp.txt')

    if not os.path.exists(result_path):
        print('ERROR: result.json not found at', result_path)
        return 2
    if not os.path.exists(report_path):
        print('ERROR: analysis_report_cpp.txt not found at', report_path)
        return 3

    with open(report_path, 'r', encoding='utf-8', errors='replace') as f:
        report_text = f.read()

    with open(result_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    data['analysis_report_cpp'] = report_text
    data['analysis_report_cpp_summary_length'] = len(report_text)

    # write back
    with open(result_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print('Merged analysis_report_cpp.txt into', result_path)
    return 0

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Usage: merge_cpp_report_into_result.py <workspace_dir>')
        sys.exit(1)
    sys.exit(merge(sys.argv[1]))
