#!/usr/bin/env python
"""Simulate the test execution flow to verify PASS status"""
import sys
import json
import tempfile
from pathlib import Path

sys.path.insert(0, 'agent')

# Create a temp directory for testing
with tempfile.TemporaryDirectory() as tmpdir:
    tmpdir = Path(tmpdir)
    
    # Step 1: Generate DiagramScene tests
    from diagramscene_functional_tests import DiagramSceneFunctionalTests
    
    dt = DiagramSceneFunctionalTests()
    tests = dt.build_all_tests()
    print(f"[1] Generated {len(tests)} tests")
    print(f"    Initial status: {tests[0]['status']}")
    
    # Step 2: Save to generated_tests.json (simulating what dynamic_tester does)
    gen_tests_path = tmpdir / 'generated_tests.json'
    gen_tests_path.write_text(json.dumps(tests, indent=2), encoding='utf-8')
    print(f"[2] Saved tests to {gen_tests_path}")
    
    # Step 3: Execute them through run_generated_tests
    from dynamic_tester import run_generated_tests
    
    executed_tests = run_generated_tests(Path.cwd(), out_dir=tmpdir)
    print(f"[3] Executed {len(executed_tests)} tests through run_generated_tests()")
    
    # Step 4: Check results
    passed = sum(1 for t in executed_tests if t.get('status') == 'PASS')
    failed = sum(1 for t in executed_tests if t.get('status') == 'FAIL')
    skipped = sum(1 for t in executed_tests if t.get('status') == 'SKIPPED')
    
    print(f"\n[4] Results:")
    print(f"    PASS:    {passed}")
    print(f"    FAIL:    {failed}")
    print(f"    SKIPPED: {skipped}")
    print(f"    TOTAL:   {len(executed_tests)}")
    
    # Show first 3 tests
    print(f"\n[5] Sample executed tests:")
    for t in executed_tests[:3]:
        print(f"    {t['test']}: {t['status']}")
        if 'detail' in t and len(t['detail']) > 100:
            print(f"       Detail: {t['detail'][:100]}...")
