#!/usr/bin/env python
"""Debug test execution to see what's failing"""
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
    
    # Show first test in detail
    t = executed_tests[0]
    print(f"Test: {t['test']}")
    print(f"Status: {t['status']}")
    print(f"\nFull Detail Output:")
    print(t.get('detail', 'NO DETAIL'))
