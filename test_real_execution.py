#!/usr/bin/env python
"""Test real tests execution"""
import sys
import json
import tempfile
from pathlib import Path

sys.path.insert(0, 'agent')

from diagramscene_real_tests import generate_diagramscene_real_tests
from dynamic_tester import run_generated_tests

with tempfile.TemporaryDirectory() as tmpdir:
    tmpdir = Path(tmpdir)
    
    # Generate real tests
    tests = generate_diagramscene_real_tests()
    print(f'Generated {len(tests)} real tests')
    
    # Save to JSON
    gen_tests_path = tmpdir / 'generated_tests.json'
    gen_tests_path.write_text(json.dumps(tests, indent=2), encoding='utf-8')
    
    # Execute them
    executed_tests = run_generated_tests(Path.cwd(), out_dir=tmpdir)
    
    # Show results
    passed = sum(1 for t in executed_tests if t['status'] == 'PASS')
    failed = sum(1 for t in executed_tests if t['status'] == 'FAIL')
    
    print(f'\nResults:')
    print(f'  PASS: {passed}')
    print(f'  FAIL: {failed}')
    
    # Show first 3
    print(f'\nFirst 3 tests:')
    for t in executed_tests[:3]:
        print(f'  {t["test"]}: {t["status"]}')
