import importlib
from pathlib import Path


def test_dynamic_tester_importable():
    mod = importlib.import_module('dynamic_tester')
    assert hasattr(mod, 'run_generated_tests')


def test_run_generated_tests_no_workspace(tmp_path):
    # Ensure function handles missing generated_tests.json gracefully
    import dynamic_tester as dt
    results = dt.run_generated_tests(tmp_path, out_dir=tmp_path)
    assert isinstance(results, list)
    # Should return either SKIPPED or a structured response
    assert any(isinstance(r.get('test'), str) for r in results)
