#!/usr/bin/env python
"""Check which tests are failing and why"""
import sys
import json
import tempfile
from pathlib import Path

sys.path.insert(0, 'agent')

with tempfile.TemporaryDirectory() as tmpdir:
    tmpdir = Path(tmpdir)
    
    from diagramscene_functional_tests import DiagramSceneFunctionalTests
    dt = DiagramSceneFunctionalTests()
    tests = dt.build_all_tests()
    
    gen_tests_path = tmpdir / 'generated_tests.json'
    gen_tests_path.write_text(json.dumps(tests, indent=2), encoding='utf-8')
    
    from dynamic_tester import run_generated_tests
    executed_tests = run_generated_tests(Path.cwd(), out_dir=tmpdir)
    
    # Show failing tests
    print("Failing tests:")
    for t in executed_tests:
        if t['status'] == 'FAIL':
            print(f"\n{t['test']}: FAIL")
            # Get the expected value from original tests
            orig = next((x for x in tests if x['test'] == t['test']), None)
            if orig:
                print(f"  Expected: {orig.get('expected', 'N/A')}")
                print(f"  Commands: {orig.get('commands', [])}")
            # Show output snippet
            detail = t.get('detail', '')
            if detail:
                lines = detail.split('\n')
                print(f"  Output: {lines[-2] if len(lines) > 1 else lines[0]}")
